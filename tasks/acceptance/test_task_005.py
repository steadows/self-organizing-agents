"""Acceptance tests for task-005: ttl_cache()

Tests the contract:
  @ttl_cache(maxsize=128, ttl=300.0)
  def some_function(...): ...

Decorator factory that adds LRU caching with time-to-live expiry.
Provides cache_info() and cache_clear() on the wrapped function.

These tests are FROZEN ground truth. Implementations must pass all of them.
"""

import os
import sys
import threading
from unittest.mock import patch

import pytest

# Allow importing from the output directory passed via environment variable
# or default to the current directory
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

from ttl_cache import ttl_cache


# ── Cache hit ──────────────────────────────────────────────────────────────

def test_cache_hit_same_args() -> None:
    """Same arguments return cached value; function called only once."""
    call_count = 0

    @ttl_cache(maxsize=128, ttl=300.0)
    def expensive(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    assert expensive(5) == 10
    assert expensive(5) == 10
    assert call_count == 1


# ── Cache miss ─────────────────────────────────────────────────────────────

def test_cache_miss_different_args() -> None:
    """Different arguments trigger a new function call."""
    call_count = 0

    @ttl_cache(maxsize=128, ttl=300.0)
    def expensive(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    assert expensive(1) == 2
    assert expensive(2) == 4
    assert call_count == 2


# ── TTL expiry ─────────────────────────────────────────────────────────────

def test_cache_ttl_expiry() -> None:
    """After TTL elapses, the cached entry is stale and function is re-called."""
    call_count = 0
    fake_time = [0.0]

    with patch("time.monotonic", side_effect=lambda: fake_time[0]):

        @ttl_cache(maxsize=128, ttl=10.0)
        def compute(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        # First call at t=0
        assert compute(1) == 1
        assert call_count == 1

        # Same call at t=5 (within TTL) — cached
        fake_time[0] = 5.0
        assert compute(1) == 1
        assert call_count == 1

        # Same call at t=11 (past TTL) — re-computed
        fake_time[0] = 11.0
        assert compute(1) == 1
        assert call_count == 2


def test_cache_ttl_expiry_refreshes_timestamp() -> None:
    """After re-computation, the TTL timer resets."""
    call_count = 0
    fake_time = [0.0]

    with patch("time.monotonic", side_effect=lambda: fake_time[0]):

        @ttl_cache(maxsize=128, ttl=10.0)
        def compute(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        compute(1)  # t=0, call_count=1
        fake_time[0] = 11.0
        compute(1)  # t=11, expired, call_count=2
        fake_time[0] = 15.0
        compute(1)  # t=15, within new TTL (11+10=21), still cached
        assert call_count == 2


# ── LRU eviction ──────────────────────────────────────────────────────────

def test_cache_lru_eviction() -> None:
    """When maxsize is exceeded, the least recently used entry is evicted."""
    call_count = 0

    @ttl_cache(maxsize=2, ttl=300.0)
    def compute(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x

    compute(1)  # cache: {1}
    compute(2)  # cache: {1, 2}
    compute(3)  # cache: {2, 3} — 1 evicted

    call_count = 0
    compute(1)  # should miss — was evicted
    assert call_count == 1

    call_count = 0
    compute(3)  # should hit — still cached
    assert call_count == 0


# ── cache_info() ───────────────────────────────────────────────────────────

def test_cache_info_exists() -> None:
    """Decorated function has a cache_info() method."""

    @ttl_cache(maxsize=128, ttl=300.0)
    def func(x: int) -> int:
        return x

    assert hasattr(func, "cache_info")
    assert callable(func.cache_info)


def test_cache_info_values() -> None:
    """cache_info() returns hits, misses, maxsize, currsize."""

    @ttl_cache(maxsize=128, ttl=300.0)
    def func(x: int) -> int:
        return x

    func(1)  # miss
    func(1)  # hit
    func(2)  # miss

    info = func.cache_info()
    assert info.hits == 1
    assert info.misses == 2
    assert info.maxsize == 128
    assert info.currsize == 2


# ── cache_clear() ─────────────────────────────────────────────────────────

def test_cache_clear_exists() -> None:
    """Decorated function has a cache_clear() method."""

    @ttl_cache(maxsize=128, ttl=300.0)
    def func(x: int) -> int:
        return x

    assert hasattr(func, "cache_clear")
    assert callable(func.cache_clear)


def test_cache_clear_empties_cache() -> None:
    """cache_clear() removes all entries and resets counters."""
    call_count = 0

    @ttl_cache(maxsize=128, ttl=300.0)
    def func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x

    func(1)
    func(2)
    assert func.cache_info().currsize == 2

    func.cache_clear()
    info = func.cache_info()
    assert info.currsize == 0
    assert info.hits == 0
    assert info.misses == 0

    # Calling again should miss
    call_count = 0
    func(1)
    assert call_count == 1


# ── Thread safety ─────────────────────────────────────────────────────────

def test_cache_thread_safety() -> None:
    """Concurrent access from multiple threads doesn't corrupt the cache."""

    @ttl_cache(maxsize=128, ttl=300.0)
    def compute(x: int) -> int:
        return x * 2

    errors: list[str] = []

    def worker(value: int) -> None:
        try:
            for _ in range(100):
                result = compute(value)
                if result != value * 2:
                    errors.append(f"Expected {value * 2}, got {result}")
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"Thread safety errors: {errors}"


# ── maxsize=0 (caching disabled) ──────────────────────────────────────────

def test_cache_maxsize_zero_disables_caching() -> None:
    """maxsize=0 means every call executes the function."""
    call_count = 0

    @ttl_cache(maxsize=0, ttl=300.0)
    def func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x

    func(1)
    func(1)
    func(1)
    assert call_count == 3


# ── ttl=0 (caching disabled) ──────────────────────────────────────────────

def test_cache_ttl_zero_disables_caching() -> None:
    """ttl=0 means entries expire immediately — every call re-executes."""
    call_count = 0

    @ttl_cache(maxsize=128, ttl=0)
    def func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x

    func(1)
    func(1)
    assert call_count == 2


# ── Validation errors ─────────────────────────────────────────────────────

def test_cache_negative_ttl_raises_value_error() -> None:
    """ttl < 0 raises ValueError."""
    with pytest.raises(ValueError):

        @ttl_cache(maxsize=128, ttl=-1.0)
        def func() -> None:
            pass


def test_cache_negative_maxsize_raises_value_error() -> None:
    """maxsize < 0 raises ValueError."""
    with pytest.raises(ValueError):

        @ttl_cache(maxsize=-1, ttl=300.0)
        def func() -> None:
            pass


# ── Unhashable args ───────────────────────────────────────────────────────

def test_cache_unhashable_args_raises_type_error() -> None:
    """Unhashable arguments (e.g., list) raise TypeError."""

    @ttl_cache(maxsize=128, ttl=300.0)
    def func(x: list) -> list:
        return x

    with pytest.raises(TypeError):
        func([1, 2, 3])


# ── None return value ─────────────────────────────────────────────────────

def test_cache_none_return_is_cached() -> None:
    """A function returning None has that None value cached."""
    call_count = 0

    @ttl_cache(maxsize=128, ttl=300.0)
    def returns_none(x: int) -> None:
        nonlocal call_count
        call_count += 1
        return None

    result1 = returns_none(1)
    result2 = returns_none(1)
    assert result1 is None
    assert result2 is None
    assert call_count == 1
