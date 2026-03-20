"""Tests for the ttl_cache decorator."""

import threading
import time

import pytest

from ttl_cache import ttl_cache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_counter_func(maxsize: int = 128, ttl: float = 300.0):
    """Return a decorated function and a call-count list for introspection."""
    call_count = [0]

    @ttl_cache(maxsize=maxsize, ttl=ttl)
    def func(x: int, y: int = 0) -> int:
        call_count[0] += 1
        return x + y

    return func, call_count


# ---------------------------------------------------------------------------
# Basic hit / miss behaviour
# ---------------------------------------------------------------------------

def test_first_call_is_a_miss():
    func, calls = make_counter_func()
    func(1)
    info = func.cache_info()
    assert info.misses == 1
    assert info.hits == 0
    assert calls[0] == 1


def test_repeated_call_is_a_hit():
    func, calls = make_counter_func()
    func(1)
    func(1)
    info = func.cache_info()
    assert info.hits == 1
    assert info.misses == 1
    assert calls[0] == 1  # underlying function called only once


def test_different_args_are_separate_cache_entries():
    func, calls = make_counter_func()
    func(1)
    func(2)
    info = func.cache_info()
    assert info.misses == 2
    assert info.currsize == 2
    assert calls[0] == 2


def test_kwargs_are_part_of_key():
    func, calls = make_counter_func()
    func(1, y=0)
    func(1, y=1)
    assert calls[0] == 2


def test_kwargs_order_does_not_matter():
    """Sorted kwargs should produce the same key regardless of order."""

    @ttl_cache()
    def multi(**kwargs):
        return sum(kwargs.values())

    multi(a=1, b=2)
    multi(b=2, a=1)
    info = multi.cache_info()
    assert info.hits == 1
    assert info.misses == 1


def test_no_args_function_cached_under_empty_key():
    call_count = [0]

    @ttl_cache()
    def constant() -> int:
        call_count[0] += 1
        return 42

    assert constant() == 42
    assert constant() == 42
    assert call_count[0] == 1
    assert constant.cache_info().hits == 1


def test_none_return_value_is_cached():
    call_count = [0]

    @ttl_cache()
    def returns_none(x: int):
        call_count[0] += 1
        return None

    assert returns_none(1) is None
    assert returns_none(1) is None
    assert call_count[0] == 1
    assert returns_none.cache_info().hits == 1


# ---------------------------------------------------------------------------
# TTL expiration
# ---------------------------------------------------------------------------

def test_entry_expires_after_ttl():
    func, calls = make_counter_func(ttl=0.05)
    func(1)
    time.sleep(0.1)
    func(1)
    assert calls[0] == 2
    info = func.cache_info()
    assert info.misses == 2
    assert info.hits == 0


def test_entry_still_valid_before_ttl():
    func, calls = make_counter_func(ttl=5.0)
    func(1)
    func(1)
    assert calls[0] == 1


def test_ttl_zero_disables_caching():
    func, calls = make_counter_func(ttl=0)
    func(1)
    func(1)
    assert calls[0] == 2
    info = func.cache_info()
    assert info.hits == 0
    assert info.currsize == 0


# ---------------------------------------------------------------------------
# LRU eviction
# ---------------------------------------------------------------------------

def test_lru_eviction_when_maxsize_exceeded():
    func, calls = make_counter_func(maxsize=2)
    func(1)  # cache: {1}
    func(2)  # cache: {1, 2}
    func(3)  # cache: {2, 3} — 1 evicted (LRU)
    func(1)  # miss — 1 was evicted
    assert func.cache_info().currsize == 2
    assert calls[0] == 4


def test_access_refreshes_lru_order():
    func, calls = make_counter_func(maxsize=2)
    func(1)  # cache: {1}
    func(2)  # cache: {1, 2}
    func(1)  # hit — 1 moved to end; order: {2, 1}
    func(3)  # 2 evicted (now LRU), cache: {1, 3}
    func(2)  # miss — 2 was evicted
    assert calls[0] == 4  # 1, 2, 3, 2 → 4 real calls


def test_maxsize_zero_disables_caching():
    func, calls = make_counter_func(maxsize=0)
    func(1)
    func(1)
    assert calls[0] == 2
    info = func.cache_info()
    assert info.hits == 0
    assert info.currsize == 0


# ---------------------------------------------------------------------------
# cache_info and cache_clear
# ---------------------------------------------------------------------------

def test_cache_info_fields():
    func, _ = make_counter_func(maxsize=10, ttl=60.0)
    func(1)
    func(1)
    info = func.cache_info()
    assert info.hits == 1
    assert info.misses == 1
    assert info.maxsize == 10
    assert info.currsize == 1


def test_cache_clear_resets_everything():
    func, calls = make_counter_func()
    func(1)
    func(1)
    func.cache_clear()
    info = func.cache_info()
    assert info.hits == 0
    assert info.misses == 0
    assert info.currsize == 0
    # Function should execute again after clear
    func(1)
    assert calls[0] == 2


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_unhashable_args_raise_type_error():
    @ttl_cache()
    def bad(x):
        return x

    with pytest.raises(TypeError):
        bad([1, 2, 3])


def test_unhashable_kwargs_raise_type_error():
    @ttl_cache()
    def bad(**kwargs):
        return kwargs

    with pytest.raises(TypeError):
        bad(x=[1, 2])


def test_negative_ttl_raises_value_error():
    with pytest.raises(ValueError, match="ttl must be >= 0"):
        ttl_cache(ttl=-1.0)


def test_negative_maxsize_raises_value_error():
    with pytest.raises(ValueError, match="maxsize must be >= 0"):
        ttl_cache(maxsize=-1)


# ---------------------------------------------------------------------------
# functools.wraps — metadata preservation
# ---------------------------------------------------------------------------

def test_wraps_preserves_function_name():
    @ttl_cache()
    def my_special_function(x: int) -> int:
        """My docstring."""
        return x

    assert my_special_function.__name__ == "my_special_function"
    assert my_special_function.__doc__ == "My docstring."


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

def test_concurrent_access_is_safe():
    """Multiple threads hitting the cache simultaneously should not corrupt state."""
    call_count = [0]
    lock = threading.Lock()

    @ttl_cache(maxsize=32, ttl=10.0)
    def expensive(n: int) -> int:
        with lock:
            call_count[0] += 1
        time.sleep(0.01)
        return n * 2

    errors: list[Exception] = []

    def worker():
        try:
            for _ in range(5):
                expensive(1)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread errors: {errors}"
    info = expensive.cache_info()
    # hits + misses should equal total calls (50), with currsize <= 32
    assert info.hits + info.misses == 50
    assert info.currsize <= 32
