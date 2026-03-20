"""Tests for bounded_pool async worker pool."""

import asyncio

import pytest

from bounded_pool import bounded_pool


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_max_queue_zero_raises_value_error():
    with pytest.raises(ValueError, match="max_queue"):
        async with bounded_pool(max_workers=2, max_queue=0) as pool:
            pass


@pytest.mark.asyncio
async def test_max_workers_zero_raises_value_error():
    with pytest.raises(ValueError, match="max_workers"):
        async with bounded_pool(max_workers=0, max_queue=4) as pool:
            pass


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_processes_all_items():
    results: list[int] = []

    async def collect(item: int) -> None:
        results.append(item)

    async with bounded_pool(max_workers=4, max_queue=16) as pool:
        for i in range(50):
            await pool.submit(collect, i)

    assert sorted(results) == list(range(50))


@pytest.mark.asyncio
async def test_submit_zero_tasks_exits_cleanly():
    async with bounded_pool(max_workers=2, max_queue=4) as pool:
        pass  # no submits — should not hang or error


@pytest.mark.asyncio
async def test_single_worker_runs_serially():
    """With max_workers=1 tasks must run one at a time."""
    running = 0
    max_concurrent = 0

    async def track() -> None:
        nonlocal running, max_concurrent
        running += 1
        if running > max_concurrent:
            max_concurrent = running
        await asyncio.sleep(0.01)
        running -= 1

    async with bounded_pool(max_workers=1, max_queue=8) as pool:
        for _ in range(6):
            await pool.submit(track)

    assert max_concurrent == 1


@pytest.mark.asyncio
async def test_concurrency_limited_to_max_workers():
    """Concurrent tasks should never exceed max_workers."""
    max_workers = 3
    running = 0
    max_concurrent = 0

    async def track() -> None:
        nonlocal running, max_concurrent
        running += 1
        if running > max_concurrent:
            max_concurrent = running
        await asyncio.sleep(0.02)
        running -= 1

    async with bounded_pool(max_workers=max_workers, max_queue=16) as pool:
        for _ in range(20):
            await pool.submit(track)

    assert max_concurrent <= max_workers


# ---------------------------------------------------------------------------
# Backpressure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_backpressure_with_max_queue_one():
    """max_queue=1 means the producer blocks on every submit once the slot is taken."""
    results: list[int] = []

    async def work(n: int) -> None:
        await asyncio.sleep(0.01)
        results.append(n)

    async with bounded_pool(max_workers=1, max_queue=1) as pool:
        for i in range(5):
            await pool.submit(work, i)

    assert sorted(results) == list(range(5))


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_error_reraised():
    async def boom() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        async with bounded_pool(max_workers=2, max_queue=4) as pool:
            await pool.submit(boom)


@pytest.mark.asyncio
async def test_error_after_drain_remaining_work():
    """Pool should drain remaining work even when a task fails."""
    results: list[int] = []

    async def good(n: int) -> None:
        await asyncio.sleep(0.01)
        results.append(n)

    async def bad() -> None:
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError, match="fail"):
        async with bounded_pool(max_workers=2, max_queue=8) as pool:
            await pool.submit(good, 1)
            await pool.submit(bad)
            await pool.submit(good, 2)
            await pool.submit(good, 3)

    # All good tasks should still have completed
    assert sorted(results) == [1, 2, 3]


@pytest.mark.asyncio
async def test_multiple_errors_raises_exception_group():
    async def fail(msg: str) -> None:
        raise ValueError(msg)

    with pytest.raises((ValueError, ExceptionGroup)):
        async with bounded_pool(max_workers=2, max_queue=4) as pool:
            await pool.submit(fail, "a")
            await pool.submit(fail, "b")


# ---------------------------------------------------------------------------
# Post-exit submit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_submit_after_exit_raises_runtime_error():
    async def noop() -> None:
        pass

    async with bounded_pool(max_workers=2, max_queue=4) as pool:
        await pool.submit(noop)

    with pytest.raises(RuntimeError, match="closed"):
        await pool.submit(noop)


# ---------------------------------------------------------------------------
# kwargs forwarding
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_kwargs_forwarded():
    captured: dict[str, object] = {}

    async def work(*, key: str, value: int) -> None:
        captured["key"] = key
        captured["value"] = value

    async with bounded_pool(max_workers=1, max_queue=4) as pool:
        await pool.submit(work, key="hello", value=42)

    assert captured == {"key": "hello", "value": 42}
