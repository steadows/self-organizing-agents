"""Tests for the ttl_cache decorator."""

import threading
import time
from unittest.mock import patch

import pytest

from ttl_cache import ttl_cache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_counter_func():
    """Return a simple function that counts how many times it has been called."""
    call_count = [0]

    def fn(x):
        call_count[0] += 1
        return x * 2

    fn.call_count = call_count
    return fn


# ---------------------------------------------------------------------------
# Basic caching behaviour
# ---------------------------------------------------------------------------

def test_cache_miss_then_hit():
    fn = make_counter_func()
    cached = ttl_cache(maxsize=10, ttl=60.0)(fn)

    result1 = cached(5)
    result2 = cached(5)

    assert result1 == 10
    assert result2 == 10
    assert fn.call_count[0] == 1  # underlying function called only once

    info = cached.cache_info()
    assert info.hits == 1
    assert info.misses == 1
    assert info.currsize == 1
    assert info.maxsize == 10


def test_different_args_are_separate_entries():
    fn = make_counter_func()
    cached = ttl_cache(maxsize=10, ttl=60.0)(fn)

    cached(1)
    cached(2)
    cached(1)  # hit

    assert fn.call_count[0] == 2
    info = cached.cache_info()
    assert info.hits == 1
    assert info.misses == 2
    assert info.currsize == 2


def test_kwargs_are_cached():
    call_count = [0]

    @ttl_cache(maxsize=10, ttl=60.0)
    def fn(x, y=0):
        call_count[0] += 1
        return x + y

    fn(1, y=2)
    fn(1, y=2)  # hit

    assert call_count[0] == 1
    assert fn.cache_info().hits == 1


def test_no_args_function():
    call_count = [0]

    @ttl_cache(maxsize=10, ttl=60.0)
    def always_42():
        call_count[0] += 1
        return 42

    assert always_42() == 42
    assert always_42() == 42
    assert call_count[0] == 1
    assert always_42.cache_info().currsize == 1


def test_none_return_value_is_cached():
    call_count = [0]

    @ttl_cache(maxsize=10, ttl=60.0)
    def returns_none(x):
        call_count[0] += 1
        return None

    assert returns_none(1) is None
    assert returns_none(1) is None
    assert call_count[0] == 1
    assert returns_none.cache_info().hits == 1


# ---------------------------------------------------------------------------
# TTL expiration
# ---------------------------------------------------------------------------

def test_expired_entry_is_a_miss():
    call_count = [0]

    @ttl_cache(maxsize=10, ttl=1.0)
    def fn(x):
        call_count[0] += 1
        return x

    fn(7)
    assert call_count[0] == 1

    # Simulate time passing beyond TTL using monotonic time mock
    with patch("ttl_cache.time.monotonic", return_value=time.monotonic() + 2.0):
        fn(7)

    assert call_count[0] == 2
    assert fn.cache_info().misses == 2


def test_entry_within_ttl_is_a_hit():
    call_count = [0]

    @ttl_cache(maxsize=10, ttl=60.0)
    def fn(x):
        call_count[0] += 1
        return x

    fn(3)
    fn(3)  # still within TTL

    assert call_count[0] == 1
    assert fn.cache_info().hits == 1


def test_ttl_zero_disables_caching():
    call_count = [0]

    @ttl_cache(maxsize=10, ttl=0)
    def fn(x):
        call_count[0] += 1
        return x

    fn(1)
    fn(1)

    assert call_count[0] == 2
    info = fn.cache_info()
    assert info.hits == 0
    assert info.misses == 2
    assert info.currsize == 0


# ---------------------------------------------------------------------------
# maxsize behaviour
# ---------------------------------------------------------------------------

def test_maxsize_zero_disables_caching():
    call_count = [0]

    @ttl_cache(maxsize=0, ttl=60.0)
    def fn(x):
        call_count[0] += 1
        return x

    fn(1)
    fn(1)

    assert call_count[0] == 2
    info = fn.cache_info()
    assert info.hits == 0
    assert info.misses == 2
    assert info.currsize == 0


def test_lru_eviction():
    call_count = [0]

    @ttl_cache(maxsize=2, ttl=60.0)
    def fn(x):
        call_count[0] += 1
        return x

    fn(1)  # cache: {1}
    fn(2)  # cache: {1, 2}
    fn(1)  # hit — moves 1 to end; cache: {2, 1}
    fn(3)  # miss — evicts LRU (2); cache: {1, 3}

    assert fn.cache_info().currsize == 2

    # 2 was evicted, so calling it again should be a miss
    prev_misses = fn.cache_info().misses
    fn(2)
    assert fn.cache_info().misses == prev_misses + 1


# ---------------------------------------------------------------------------
# cache_clear
# ---------------------------------------------------------------------------

def test_cache_clear_resets_stats_and_entries():
    call_count = [0]

    @ttl_cache(maxsize=10, ttl=60.0)
    def fn(x):
        call_count[0] += 1
        return x

    fn(1)
    fn(1)  # hit

    fn.cache_clear()
    info = fn.cache_info()
    assert info.hits == 0
    assert info.misses == 0
    assert info.currsize == 0

    # Function should execute again after clear
    fn(1)
    assert call_count[0] == 2


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_unhashable_args_raise_type_error():
    @ttl_cache(maxsize=10, ttl=60.0)
    def fn(x):
        return x

    with pytest.raises(TypeError):
        fn([1, 2, 3])


def test_unhashable_kwargs_raise_type_error():
    @ttl_cache(maxsize=10, ttl=60.0)
    def fn(x=None):
        return x

    with pytest.raises(TypeError):
        fn(x=[1, 2, 3])


def test_negative_ttl_raises_value_error():
    with pytest.raises(ValueError, match="ttl must be >= 0"):
        @ttl_cache(maxsize=10, ttl=-1.0)
        def fn(x):
            return x


def test_negative_maxsize_raises_value_error():
    with pytest.raises(ValueError, match="maxsize must be >= 0"):
        @ttl_cache(maxsize=-1, ttl=60.0)
        def fn(x):
            return x


# ---------------------------------------------------------------------------
# functools.wraps metadata preservation
# ---------------------------------------------------------------------------

def test_wraps_preserves_metadata():
    @ttl_cache(maxsize=10, ttl=60.0)
    def my_function(x: int) -> int:
        """My docstring."""
        return x

    assert my_function.__name__ == "my_function"
    assert my_function.__doc__ == "My docstring."


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

def test_concurrent_access_is_safe():
    call_count = [0]
    errors = []

    @ttl_cache(maxsize=50, ttl=60.0)
    def fn(x):
        call_count[0] += 1
        return x * 2

    def worker(n):
        try:
            for _ in range(20):
                fn(n % 5)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Errors during concurrent access: {errors}"
    info = fn.cache_info()
    assert info.currsize <= 5  # only 5 distinct keys (0..4)
    assert info.hits + info.misses == 10 * 20


# ---------------------------------------------------------------------------
# Failure path: underlying function raises
# ---------------------------------------------------------------------------

def test_exception_from_underlying_function_propagates():
    @ttl_cache(maxsize=10, ttl=60.0)
    def fn(x):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        fn(1)

    # Failed call should not be cached
    info = fn.cache_info()
    assert info.currsize == 0
    assert info.misses == 1


def test_exception_does_not_increment_hits():
    @ttl_cache(maxsize=10, ttl=60.0)
    def fn(x):
        raise ValueError("error")

    with pytest.raises(ValueError):
        fn(1)

    info = fn.cache_info()
    assert info.hits == 0
