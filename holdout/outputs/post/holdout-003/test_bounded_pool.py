"""Tests for the bounded_pool async context manager."""

import asyncio
import pytest

from bounded_pool import bounded_pool


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_submit_zero_tasks_exits_cleanly():
    """Pool with no submitted tasks exits without error or hang."""

    async def run():
        async with bounded_pool(max_workers=2, max_queue=4) as pool:
            pass  # submit nothing

    asyncio.run(run())


def test_all_tasks_complete_before_exit():
    """All submitted coroutines finish by the time the context manager exits."""
    results = []

    async def record(n: int) -> None:
        await asyncio.sleep(0)
        results.append(n)

    async def run():
        async with bounded_pool(max_workers=4, max_queue=16) as pool:
            for i in range(20):
                await pool.submit(record, i)

    asyncio.run(run())
    assert sorted(results) == list(range(20))


def test_tasks_run_concurrently():
    """With multiple workers, tasks overlap in time (total wall time < sum of individual times)."""
    import time

    async def slow_task() -> None:
        await asyncio.sleep(0.05)

    async def run() -> float:
        start = time.monotonic()
        async with bounded_pool(max_workers=4, max_queue=8) as pool:
            for _ in range(4):
                await pool.submit(slow_task)
        return time.monotonic() - start

    elapsed = asyncio.run(run())
    # 4 tasks × 50 ms each, with 4 workers they should finish in ~50 ms, not 200 ms.
    assert elapsed < 0.15, f"Expected concurrent execution, but took {elapsed:.3f}s"


def test_max_workers_1_runs_serially():
    """With max_workers=1 tasks execute one at a time (FIFO order preserved)."""
    order = []

    async def record(n: int) -> None:
        order.append(n)
        await asyncio.sleep(0)

    async def run():
        async with bounded_pool(max_workers=1, max_queue=8) as pool:
            for i in range(5):
                await pool.submit(record, i)

    asyncio.run(run())
    assert order == list(range(5))


def test_backpressure_max_queue_1():
    """With max_queue=1, producer blocks on every submit until the slot clears."""
    results = []

    async def work(n: int) -> None:
        await asyncio.sleep(0.01)
        results.append(n)

    async def run():
        async with bounded_pool(max_workers=1, max_queue=1) as pool:
            for i in range(5):
                await pool.submit(work, i)

    asyncio.run(run())
    assert sorted(results) == list(range(5))


def test_kwargs_forwarded_to_coroutine():
    """Keyword arguments passed to submit are forwarded correctly."""
    captured: dict = {}

    async def capture(*, key: str, value: int) -> None:
        captured[key] = value

    async def run():
        async with bounded_pool(max_workers=1, max_queue=4) as pool:
            await pool.submit(capture, key="x", value=42)

    asyncio.run(run())
    assert captured == {"x": 42}


# ---------------------------------------------------------------------------
# Error-handling tests
# ---------------------------------------------------------------------------


def test_exception_in_task_is_reraised():
    """An exception raised by a submitted coroutine propagates on pool exit."""

    async def boom() -> None:
        raise ValueError("task failure")

    async def run():
        async with bounded_pool(max_workers=2, max_queue=4) as pool:
            await pool.submit(boom)

    with pytest.raises(ValueError, match="task failure"):
        asyncio.run(run())


def test_remaining_tasks_drain_after_exception():
    """Pool drains all work even when one task raises."""
    results = []

    async def maybe_fail(n: int) -> None:
        if n == 2:
            raise RuntimeError("injected error")
        results.append(n)

    async def run():
        async with bounded_pool(max_workers=1, max_queue=8) as pool:
            for i in range(5):
                await pool.submit(maybe_fail, i)

    with pytest.raises(RuntimeError, match="injected error"):
        asyncio.run(run())

    # Tasks 0, 1, 3, 4 should still have completed.
    assert sorted(results) == [0, 1, 3, 4]


def test_submit_after_exit_raises_runtime_error():
    """Calling submit() after the pool has exited raises RuntimeError."""

    async def noop() -> None:
        pass

    async def run():
        async with bounded_pool(max_workers=2, max_queue=4) as pool:
            pass
        # Pool is now closed; submit should raise.
        await pool.submit(noop)

    with pytest.raises(RuntimeError):
        asyncio.run(run())


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


def test_max_queue_zero_raises_value_error():
    """max_queue=0 raises ValueError immediately (before entering the block)."""

    async def run():
        async with bounded_pool(max_workers=2, max_queue=0):
            pass

    with pytest.raises(ValueError, match="max_queue"):
        asyncio.run(run())


def test_max_workers_zero_raises_value_error():
    """max_workers=0 raises ValueError immediately."""

    async def run():
        async with bounded_pool(max_workers=0, max_queue=4):
            pass

    with pytest.raises(ValueError, match="max_workers"):
        asyncio.run(run())


def test_negative_max_workers_raises_value_error():
    """Negative max_workers raises ValueError."""

    async def run():
        async with bounded_pool(max_workers=-1, max_queue=4):
            pass

    with pytest.raises(ValueError, match="max_workers"):
        asyncio.run(run())


def test_negative_max_queue_raises_value_error():
    """Negative max_queue raises ValueError."""

    async def run():
        async with bounded_pool(max_workers=2, max_queue=-5):
            pass

    with pytest.raises(ValueError, match="max_queue"):
        asyncio.run(run())


# ---------------------------------------------------------------------------
# Stress / load test
# ---------------------------------------------------------------------------


def test_large_batch_all_complete():
    """100 tasks with default pool settings all complete without error."""
    counter = 0

    async def increment() -> None:
        nonlocal counter
        await asyncio.sleep(0)
        counter += 1

    async def run():
        async with bounded_pool(max_workers=4, max_queue=16) as pool:
            for _ in range(100):
                await pool.submit(increment)

    asyncio.run(run())
    assert counter == 100
