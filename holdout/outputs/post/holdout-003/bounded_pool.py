"""Bounded async worker pool with backpressure via a fixed-size queue."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable, Coroutine


class _Pool:
    """Internal pool object yielded by the bounded_pool context manager.

    Manages a queue of coroutine factories and dispatches them to a fixed
    number of concurrent worker tasks.
    """

    def __init__(self, queue: asyncio.Queue, closed: bool = False) -> None:
        """Initialise the pool with a shared queue.

        Args:
            queue: The bounded asyncio.Queue shared with all workers.
            closed: Whether the pool has already been closed.
        """
        self._queue = queue
        self._closed = closed
        self._errors: list[BaseException] = []

    async def submit(
        self,
        coro_fn: Callable[..., Coroutine[Any, Any, Any]],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Schedule a coroutine for execution by the pool.

        If the internal queue is full, this coroutine awaits until a slot
        is available, providing natural backpressure to the producer.

        Args:
            coro_fn: A callable that returns a coroutine when invoked.
            *args: Positional arguments forwarded to ``coro_fn``.
            **kwargs: Keyword arguments forwarded to ``coro_fn``.

        Raises:
            RuntimeError: If called after the pool's ``async with`` block
                has already exited.

        Examples:
            >>> async with bounded_pool(max_workers=2, max_queue=8) as pool:
            ...     await pool.submit(my_coroutine, arg1, kwarg=value)
        """
        if self._closed:
            raise RuntimeError("Cannot submit to a pool that has already exited.")
        await self._queue.put((coro_fn, args, kwargs))

    def _record_error(self, exc: BaseException) -> None:
        """Record an exception raised by a worker task."""
        self._errors.append(exc)


async def _worker(queue: asyncio.Queue, pool: _Pool) -> None:
    """Pull coroutine factories from the queue and execute them.

    Runs until a ``None`` sentinel is dequeued, signalling shutdown.
    """
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        coro_fn, args, kwargs = item
        try:
            await coro_fn(*args, **kwargs)
        except Exception as exc:
            pool._record_error(exc)
        finally:
            queue.task_done()


@asynccontextmanager
async def bounded_pool(max_workers: int = 4, max_queue: int = 16):
    """Async context manager providing a bounded worker pool with backpressure.

    Spawns ``max_workers`` concurrent worker tasks that pull coroutines from
    an internal queue of size ``max_queue``.  When the queue is full,
    ``pool.submit()`` awaits until a slot is available.  On exit the pool
    drains all pending and in-flight work before returning, then re-raises
    any captured exceptions.

    Args:
        max_workers: Number of concurrent worker tasks.  Must be >= 1.
        max_queue: Maximum number of items that can sit in the queue at once.
            Must be >= 1.

    Yields:
        A ``_Pool`` instance with a ``submit(coro_fn, *args, **kwargs)``
        coroutine method.

    Raises:
        ValueError: If ``max_workers`` or ``max_queue`` is less than 1.
        Exception: The first exception raised by any submitted coroutine,
            re-raised after all work has been drained.

    Examples:
        >>> import asyncio
        >>> async def work(n):
        ...     await asyncio.sleep(0)
        ...
        >>> async def main():
        ...     async with bounded_pool(max_workers=2, max_queue=4) as pool:
        ...         for i in range(10):
        ...             await pool.submit(work, i)
        ...
        >>> asyncio.run(main())
    """
    if max_workers < 1:
        raise ValueError(f"max_workers must be >= 1, got {max_workers}")
    if max_queue < 1:
        raise ValueError(f"max_queue must be >= 1, got {max_queue}")

    queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue)
    pool = _Pool(queue)

    workers = [
        asyncio.create_task(_worker(queue, pool))
        for _ in range(max_workers)
    ]

    try:
        yield pool
    finally:
        pool._closed = True

        # Send one sentinel per worker to signal shutdown.
        for _ in range(max_workers):
            await queue.put(None)

        # Wait for all items (including sentinels) to be processed.
        await queue.join()

        # Await worker tasks to surface any unexpected task-level errors.
        await asyncio.gather(*workers, return_exceptions=True)

    if pool._errors:
        raise pool._errors[0]
