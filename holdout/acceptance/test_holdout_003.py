"""Frozen acceptance tests for bounded_pool().

Holdout task 003: An async context manager that provides a bounded worker pool
with backpressure. Work is submitted via pool.submit(coro_fn, *args, **kwargs)
and the pool limits both concurrency (max_workers) and queue depth (max_queue).

Spec:
    async with bounded_pool(max_workers=4, max_queue=16) as pool:
        pool.submit(coro_fn, *args, **kwargs)
"""

import sys
import os

# Allow importing from the output directory passed via environment variable
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

import asyncio

import pytest

from holdout_003 import bounded_pool


# --- Happy path ---


@pytest.mark.asyncio
async def test_basic_execution() -> None:
    """Submitted coroutines execute and complete."""
    results: list[int] = []

    async def worker(value: int) -> None:
        results.append(value)

    async with bounded_pool(max_workers=4, max_queue=16) as pool:
        for i in range(5):
            pool.submit(worker, i)

    assert sorted(results) == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_kwargs_forwarded() -> None:
    """Keyword arguments are forwarded to the coroutine."""
    results: list[str] = []

    async def worker(*, name: str) -> None:
        results.append(name)

    async with bounded_pool(max_workers=2, max_queue=8) as pool:
        pool.submit(worker, name="alice")
        pool.submit(worker, name="bob")

    assert sorted(results) == ["alice", "bob"]


# --- Backpressure ---


@pytest.mark.asyncio
async def test_backpressure_blocks_when_queue_full() -> None:
    """With a tiny queue, submit blocks until a slot opens."""
    started = asyncio.Event()
    gate = asyncio.Event()
    submitted_count = 0

    async def slow_worker() -> None:
        started.set()
        await gate.wait()

    async def submitter(pool: object) -> None:
        nonlocal submitted_count
        # First submit fills the worker slot
        pool.submit(slow_worker)
        submitted_count += 1
        # Wait for the worker to actually start
        await started.wait()
        # These submits should eventually block because queue is full
        for _ in range(2):
            pool.submit(slow_worker)
            submitted_count += 1
        # This would block if backpressure works — we set the gate
        # so everything can drain
        gate.set()

    async with bounded_pool(max_workers=1, max_queue=2) as pool:
        await asyncio.wait_for(submitter(pool), timeout=5.0)

    assert submitted_count == 3


# --- max_workers=1: serial execution ---


@pytest.mark.asyncio
async def test_serial_execution_with_one_worker() -> None:
    """With max_workers=1, tasks run one at a time."""
    running = 0
    max_concurrent = 0

    async def worker() -> None:
        nonlocal running, max_concurrent
        running += 1
        if running > max_concurrent:
            max_concurrent = running
        await asyncio.sleep(0.01)
        running -= 1

    async with bounded_pool(max_workers=1, max_queue=16) as pool:
        for _ in range(5):
            pool.submit(worker)

    assert max_concurrent == 1


# --- Concurrency respects max_workers ---


@pytest.mark.asyncio
async def test_concurrency_limited_to_max_workers() -> None:
    """Never more than max_workers coroutines run simultaneously."""
    sem = asyncio.Semaphore(0)
    running = 0
    max_concurrent = 0

    async def worker() -> None:
        nonlocal running, max_concurrent
        running += 1
        if running > max_concurrent:
            max_concurrent = running
        await asyncio.sleep(0.02)
        running -= 1

    async with bounded_pool(max_workers=3, max_queue=16) as pool:
        for _ in range(9):
            pool.submit(worker)

    assert max_concurrent <= 3


# --- Error propagation ---


@pytest.mark.asyncio
async def test_error_propagated_on_exit() -> None:
    """If a submitted coroutine raises, the error propagates on context exit."""

    async def failing() -> None:
        raise RuntimeError("task failed")

    with pytest.raises(RuntimeError, match="task failed"):
        async with bounded_pool(max_workers=2, max_queue=8) as pool:
            pool.submit(failing)


@pytest.mark.asyncio
async def test_error_does_not_prevent_other_tasks() -> None:
    """Other tasks still complete even if one raises."""
    results: list[int] = []

    async def good_worker(val: int) -> None:
        results.append(val)

    async def bad_worker() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        async with bounded_pool(max_workers=4, max_queue=16) as pool:
            pool.submit(good_worker, 1)
            pool.submit(bad_worker)
            pool.submit(good_worker, 2)

    # At least the good workers that were submitted should have run
    assert 1 in results


# --- ValueError for invalid arguments ---


@pytest.mark.asyncio
async def test_max_queue_zero_raises() -> None:
    """max_queue=0 is invalid."""
    with pytest.raises(ValueError):
        async with bounded_pool(max_workers=2, max_queue=0) as pool:
            pass


@pytest.mark.asyncio
async def test_max_workers_zero_raises() -> None:
    """max_workers=0 is invalid."""
    with pytest.raises(ValueError):
        async with bounded_pool(max_workers=0, max_queue=8) as pool:
            pass


# --- RuntimeError: submit after exit ---


@pytest.mark.asyncio
async def test_submit_after_exit_raises() -> None:
    """Calling submit after the context manager exits raises RuntimeError."""
    async with bounded_pool(max_workers=2, max_queue=8) as pool:
        pass  # exit immediately

    with pytest.raises(RuntimeError):
        pool.submit(asyncio.sleep, 0)


# --- Clean exit with no tasks ---


@pytest.mark.asyncio
async def test_clean_exit_no_tasks() -> None:
    """Exiting with no submitted tasks completes without error or hanging."""
    async with bounded_pool(max_workers=4, max_queue=16) as pool:
        pass  # no submits — should not hang or raise
