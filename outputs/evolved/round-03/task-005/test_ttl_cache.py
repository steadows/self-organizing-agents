"""Tests for the ttl_cache decorator."""

import threading
import time
from unittest.mock import patch, MagicMock

import pytest

from ttl_cache import ttl_cache


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_basic_hit_and_miss() -> None:
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def compute(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    assert compute(5) == 10
    assert compute(5) == 10
    assert call_count == 1

    info = compute.cache_info()
    assert info.hits == 1
    assert info.misses == 1
    assert info.currsize == 1
    assert info.maxsize == 10


def test_different_args_are_distinct_entries() -> None:
    @ttl_cache(maxsize=10, ttl=60.0)
    def identity(x: int) -> int:
        return x

    identity(1)
    identity(2)
    identity(1)

    info = identity.cache_info()
    assert info.hits == 1
    assert info.misses == 2
    assert info.currsize == 2


def test_kwargs_order_independent() -> None:
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def add(a: int, b: int) -> int:
        nonlocal call_count
        call_count += 1
        return a + b

    add(a=1, b=2)
    add(b=2, a=1)

    assert call_count == 1
    assert add.cache_info().hits == 1


def test_returns_none_is_cached() -> None:
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def returns_none() -> None:
        nonlocal call_count
        call_count += 1

    returns_none()
    returns_none()

    assert call_count == 1
    assert returns_none.cache_info().hits == 1


def test_no_args_function() -> None:
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def constant() -> int:
        nonlocal call_count
        call_count += 1
        return 42

    assert constant() == 42
    assert constant() == 42
    assert call_count == 1
    assert constant.cache_info().currsize == 1


# ---------------------------------------------------------------------------
# TTL expiration
# ---------------------------------------------------------------------------


def test_entry_expires_after_ttl() -> None:
    call_count = 0

    @ttl_cache(maxsize=10, ttl=0.05)
    def value() -> int:
        nonlocal call_count
        call_count += 1
        return 1

    value()
    time.sleep(0.1)
    value()

    assert call_count == 2
    assert value.cache_info().misses == 2
    assert value.cache_info().hits == 0


def test_entry_within_ttl_is_hit() -> None:
    @ttl_cache(maxsize=10, ttl=60.0)
    def value() -> int:
        return 1

    value()
    value()

    assert value.cache_info().hits == 1


# ---------------------------------------------------------------------------
# LRU eviction
# ---------------------------------------------------------------------------


def test_lru_eviction_when_maxsize_exceeded() -> None:
    @ttl_cache(maxsize=3, ttl=60.0)
    def f(x: int) -> int:
        return x

    f(1)
    f(2)
    f(3)
    # Access 1 to make it recently used; 2 is now LRU
    f(1)
    # Insert 4 — should evict 2 (LRU)
    f(4)

    info = f.cache_info()
    assert info.currsize == 3


# ---------------------------------------------------------------------------
# Disabled caching: maxsize=0 and ttl=0
# ---------------------------------------------------------------------------


def test_maxsize_zero_disables_caching() -> None:
    call_count = 0

    @ttl_cache(maxsize=0, ttl=60.0)
    def f(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x

    f(1)
    f(1)

    assert call_count == 2
    info = f.cache_info()
    assert info.hits == 0
    assert info.currsize == 0


def test_ttl_zero_disables_caching() -> None:
    call_count = 0

    @ttl_cache(maxsize=10, ttl=0)
    def f(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x

    f(1)
    f(1)

    assert call_count == 2
    info = f.cache_info()
    assert info.hits == 0
    assert info.currsize == 0


# ---------------------------------------------------------------------------
# cache_clear
# ---------------------------------------------------------------------------


def test_cache_clear_resets_state() -> None:
    @ttl_cache(maxsize=10, ttl=60.0)
    def f(x: int) -> int:
        return x

    f(1)
    f(1)

    f.cache_clear()

    info = f.cache_info()
    assert info.hits == 0
    assert info.misses == 0
    assert info.currsize == 0

    # After clear, next call is a miss again
    f(1)
    assert f.cache_info().misses == 1


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_negative_maxsize_raises_at_decoration() -> None:
    with pytest.raises(ValueError, match="maxsize must be >= 0"):

        @ttl_cache(maxsize=-1, ttl=60.0)
        def f() -> None:
            pass


def test_negative_ttl_raises_at_decoration() -> None:
    with pytest.raises(ValueError, match="ttl must be >= 0"):

        @ttl_cache(maxsize=10, ttl=-1.0)
        def f() -> None:
            pass


def test_unhashable_args_raise_type_error() -> None:
    @ttl_cache(maxsize=10, ttl=60.0)
    def f(x: object) -> object:
        return x

    with pytest.raises(TypeError):
        f([1, 2, 3])  # list is not hashable


def test_unhashable_kwargs_raise_type_error() -> None:
    @ttl_cache(maxsize=10, ttl=60.0)
    def f(x: object) -> object:
        return x

    with pytest.raises(TypeError):
        f(x={"key": "value"})  # dict is not hashable


# ---------------------------------------------------------------------------
# Metadata preservation
# ---------------------------------------------------------------------------


def test_functools_wraps_preserves_metadata() -> None:
    @ttl_cache(maxsize=10, ttl=60.0)
    def documented_function(x: int) -> int:
        """My docstring."""
        return x

    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "My docstring."


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


def test_concurrent_access_is_thread_safe() -> None:
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def slow_fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        time.sleep(0.01)
        return x

    results: list[int] = []
    errors: list[Exception] = []

    def worker() -> None:
        try:
            results.append(slow_fn(1))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert all(r == 1 for r in results)
    assert len(results) == 20


# ---------------------------------------------------------------------------
# Simulated time / monotonic mock tests
# ---------------------------------------------------------------------------


def test_expiry_uses_monotonic_time() -> None:
    """Verify that expiry logic consults time.monotonic, not wall clock."""
    fake_time = 1000.0

    def mock_monotonic() -> float:
        return fake_time

    with patch("ttl_cache.time.monotonic", side_effect=mock_monotonic):
        call_count = 0

        @ttl_cache(maxsize=10, ttl=10.0)
        def f() -> int:
            nonlocal call_count
            call_count += 1
            return 7

        f()  # miss, inserted at t=1000
        f()  # hit, t=1000 (age=0)

        assert call_count == 1
        assert f.cache_info().hits == 1

    # Advance time past TTL and verify expiry in a new decorated function.
    # Call-by-call monotonic() usage:
    #   g() #1 (cold miss): no existing entry to check, one write  → 1 call  (t=1000)
    #   g() #2 (expired):   read existing entry at t=1011 (age>ttl), then write → 2 calls (t=1011, t=1022)
    times = iter([1000.0, 1011.0, 1022.0])

    with patch("ttl_cache.time.monotonic", side_effect=times):
        call_count2 = [0]

        @ttl_cache(maxsize=10, ttl=10.0)
        def g() -> int:
            call_count2[0] += 1
            return 8

        g()  # cold miss — write at t=1000
        g()  # expired miss — read at t=1011 (age=11 > ttl=10), write at t=1022

        assert call_count2[0] == 2
        assert g.cache_info().misses == 2
        assert g.cache_info().hits == 0
