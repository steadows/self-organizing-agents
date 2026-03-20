"""Async bounded worker pool with backpressure.

Provides an async context manager that yields a pool object with a submit()
method. Workers pull coroutines from a fixed-size asyncio.Queue and execute
them concurrently. When the queue is full, submit() awaits until a slot opens,
providing natural backpressure to the producer.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable, Coroutine


class _BoundedPool:
    """Internal pool object yielded by bounded_pool()."""

    def __init__(self, queue: asyncio.Queue[tuple[Callable[..., Coroutine[Any, Any, Any]], tuple[Any, ...], dict[str, Any]] | None]) -> None:
        self._queue = queue
        self._closed = False

    async def submit(self, coro_fn: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any) -> None:
        """Schedule a coroutine for execution by a worker.

        Args:
            coro_fn: An async callable to execute.
            *args: Positional arguments forwarded to coro_fn.
            **kwargs: Keyword arguments forwarded to coro_fn.

        Raises:
            RuntimeError: If the pool has already been closed.
        """
        if self._closed:
            raise RuntimeError("Cannot submit to a closed pool")
        await self._queue.put((coro_fn, args, kwargs))

    def _close(self) -> None:
        """Mark the pool as closed so future submits are rejected."""
        self._closed = True


@asynccontextmanager
async def bounded_pool(max_workers: int = 4, max_queue: int = 16):
    """Async context manager providing a bounded worker pool with backpressure.

    Args:
        max_workers: Number of concurrent worker tasks pulling from the queue.
        max_queue: Maximum size of the internal work queue. When full, submit()
            blocks until a slot is available.

    Yields:
        A pool object with a ``submit(coro_fn, *args, **kwargs)`` method.

    Raises:
        ValueError: If max_workers or max_queue is less than 1.
    """
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    if max_queue < 1:
        raise ValueError("max_queue must be at least 1")

    queue: asyncio.Queue[tuple[Callable[..., Coroutine[Any, Any, Any]], tuple[Any, ...], dict[str, Any]] | None] = asyncio.Queue(maxsize=max_queue)
    errors: list[BaseException] = []
    pool = _BoundedPool(queue)

    async def _worker() -> None:
        while True:
            item = await queue.get()
            if item is None:
                queue.task_done()
                break
            coro_fn, args, kwargs = item
            try:
                await coro_fn(*args, **kwargs)
            except BaseException as exc:
                errors.append(exc)
            finally:
                queue.task_done()

    workers = [asyncio.create_task(_worker()) for _ in range(max_workers)]

    try:
        yield pool
    finally:
        pool._close()

        # Wait for all queued work to be consumed
        await queue.join()

        # Send sentinel to each worker so they exit
        for _ in workers:
            await queue.put(None)

        # Wait for all workers to finish
        await asyncio.gather(*workers)

        # Re-raise captured exceptions
        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise ExceptionGroup("bounded_pool: multiple tasks failed", errors)
