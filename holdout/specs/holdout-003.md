# Holdout Task 003: bounded_pool

## Function Signature

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def bounded_pool(max_workers: int = 4, max_queue: int = 16):
    ...
    yield pool
    ...
```

The yielded `pool` object exposes:

```python
async def pool.submit(coro_fn, *args, **kwargs) -> None:
```

## Description

An async context manager that provides a bounded worker pool with backpressure. Workers pull coroutines from a fixed-size queue and execute them concurrently. When the queue is full, `submit()` awaits until a slot opens, providing natural backpressure to the producer. On context manager exit, the pool drains all pending work and re-raises any captured exceptions.

## Requirements

- `bounded_pool(max_workers, max_queue)` returns an async context manager.
- The yielded pool object has a `submit(coro_fn, *args, **kwargs)` method.
- `submit()` schedules `coro_fn(*args, **kwargs)` for execution by a worker.
- `submit()` is a coroutine. If the internal queue is full, it awaits (blocks the caller) until a slot is available. This is the backpressure mechanism.
- Exactly `max_workers` concurrent worker tasks pull from the queue.
- When the `async with` block exits, the pool waits for all queued and in-flight work to complete before returning.
- If any submitted coroutine raises an exception, that exception is captured and re-raised when the pool context manager exits (after all work is drained).
- If multiple submitted coroutines raise, at least the first exception must be raised (wrapping in an `ExceptionGroup` or raising the first one are both acceptable).
- `max_queue=0` raises `ValueError` immediately (a zero-size queue is not useful).
- `max_workers=0` raises `ValueError` immediately.
- Calling `pool.submit()` after the pool's `async with` block has exited raises `RuntimeError`.

## Edge Cases

- `max_workers=1`: all submitted coroutines run serially (one at a time).
- `max_queue=1`: extreme backpressure; producer blocks on every submit until the single slot clears.
- `max_queue=0`: raises `ValueError` at construction time.
- `max_workers=0`: raises `ValueError` at construction time.
- Submitting zero tasks and exiting cleanly: no error, no hang.
- A submitted coroutine raises an exception: pool still drains remaining work, then re-raises.
- Calling `submit()` after exit: raises `RuntimeError`.

## Examples

```python
import asyncio

async def process_item(item: int) -> None:
    await asyncio.sleep(0.1)
    print(f"processed {item}")

async def main():
    async with bounded_pool(max_workers=4, max_queue=16) as pool:
        for i in range(100):
            await pool.submit(process_item, i)
    # All 100 items are processed by the time we reach here.
    print("done")

asyncio.run(main())
```

```python
# Backpressure demonstration — producer is slowed by slow consumers
async def slow_work(n: int) -> None:
    await asyncio.sleep(1)

async def main():
    async with bounded_pool(max_workers=2, max_queue=2) as pool:
        for i in range(10):
            # When 2 workers are busy and queue has 2 items,
            # this await blocks until a worker finishes one.
            await pool.submit(slow_work, i)

asyncio.run(main())
```

```python
# Error propagation
async def failing_task() -> None:
    raise ValueError("boom")

async def main():
    try:
        async with bounded_pool(max_workers=2, max_queue=4) as pool:
            await pool.submit(failing_task)
    except ValueError as e:
        print(f"Caught: {e}")  # => "Caught: boom"

asyncio.run(main())
```

```python
# Invalid configuration
async def main():
    try:
        async with bounded_pool(max_workers=2, max_queue=0) as pool:
            pass
    except ValueError:
        print("max_queue=0 rejected")  # => printed

asyncio.run(main())
```

## Scope Boundary

- NO cancellation API (cannot cancel individual submitted tasks).
- NO result collection (fire-and-forget; results are discarded, only errors propagate).
- NO priority queue (FIFO only).
- NO dynamic resizing of worker count or queue size after construction.
- NO timeout parameter on `submit()` or on the pool itself.
