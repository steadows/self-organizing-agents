"""Tests for ttl_cache decorator."""

import threading
import time

import pytest

from ttl_cache import ttl_cache


def test_basic_cache_hit_and_miss():
    """First call is a miss, second call with same args is a hit."""
    call_count = 0

    @ttl_cache(maxsize=100, ttl=60.0)
    def add(a: int, b: int) -> int:
        nonlocal call_count
        call_count += 1
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    info = add.cache_info()
    assert info.hits == 1
    assert info.misses == 1
    assert info.currsize == 1
    assert call_count == 1


def test_cache_info_returns_named_tuple():
    """cache_info returns object with hits, misses, maxsize, currsize."""
    @ttl_cache(maxsize=50, ttl=10.0)
    def identity(x: int) -> int:
        return x

    identity(1)
    identity(2)
    identity(1)
    info = identity.cache_info()
    assert info.hits == 1
    assert info.misses == 2
    assert info.maxsize == 50
    assert info.currsize == 2


def test_cache_clear_resets_everything():
    """cache_clear empties cache and resets counters."""
    @ttl_cache(maxsize=100, ttl=60.0)
    def square(x: int) -> int:
        return x * x

    square(3)
    square(3)
    square.cache_clear()
    info = square.cache_info()
    assert info.hits == 0
    assert info.misses == 0
    assert info.currsize == 0


def test_ttl_expiration():
    """Entries expire after ttl seconds."""
    call_count = 0

    @ttl_cache(maxsize=100, ttl=0.1)
    def greet(name: str) -> str:
        nonlocal call_count
        call_count += 1
        return f"hello {name}"

    assert greet("world") == "hello world"
    assert call_count == 1

    time.sleep(0.15)

    assert greet("world") == "hello world"
    assert call_count == 2

    info = greet.cache_info()
    assert info.misses == 2
    assert info.currsize == 1


def test_lru_eviction():
    """Oldest entry is evicted when cache exceeds maxsize."""
    @ttl_cache(maxsize=2, ttl=60.0)
    def compute(x: int) -> int:
        return x * 10

    compute(1)
    compute(2)
    compute(3)  # Should evict entry for 1

    info = compute.cache_info()
    assert info.currsize == 2
    assert info.misses == 3

    # Access 1 again: should be a miss (evicted)
    compute(1)
    assert compute.cache_info().misses == 4


def test_lru_access_order():
    """Accessing an entry moves it to the end, protecting it from eviction."""
    call_count = 0

    @ttl_cache(maxsize=2, ttl=60.0)
    def fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x

    fn(1)  # miss
    fn(2)  # miss
    fn(1)  # hit -> moves 1 to end, 2 is now oldest
    fn(3)  # miss -> evicts 2

    assert fn.cache_info().currsize == 2
    # 1 should still be cached
    fn(1)
    assert fn.cache_info().hits == 2
    # 2 should have been evicted
    fn(2)
    assert fn.cache_info().misses == 4


def test_maxsize_zero_disables_caching():
    """maxsize=0 means every call executes the function."""
    call_count = 0

    @ttl_cache(maxsize=0, ttl=60.0)
    def double(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    assert double(5) == 10
    assert double(5) == 10
    assert call_count == 2

    info = double.cache_info()
    assert info.hits == 0
    assert info.misses == 2
    assert info.currsize == 0


def test_ttl_zero_disables_caching():
    """ttl=0 means every call executes the function."""
    call_count = 0

    @ttl_cache(maxsize=100, ttl=0)
    def triple(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 3

    assert triple(2) == 6
    assert triple(2) == 6
    assert call_count == 2

    info = triple.cache_info()
    assert info.hits == 0
    assert info.misses == 2


def test_negative_maxsize_raises():
    """maxsize < 0 raises ValueError at decoration time."""
    with pytest.raises(ValueError, match="maxsize must be >= 0"):
        @ttl_cache(maxsize=-1)
        def noop():
            pass


def test_negative_ttl_raises():
    """ttl < 0 raises ValueError at decoration time."""
    with pytest.raises(ValueError, match="ttl must be >= 0"):
        @ttl_cache(ttl=-1.0)
        def noop():
            pass


def test_unhashable_args_raise_type_error():
    """Passing unhashable arguments raises TypeError."""
    @ttl_cache()
    def process(x):
        return x

    with pytest.raises(TypeError):
        process([1, 2, 3])


def test_no_arguments_function():
    """Function with no args uses a single cache entry keyed to ()."""
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def get_value() -> str:
        nonlocal call_count
        call_count += 1
        return "result"

    assert get_value() == "result"
    assert get_value() == "result"
    assert call_count == 1
    assert get_value.cache_info().currsize == 1


def test_none_return_value_is_cached():
    """None is a valid cached return value."""
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def return_none() -> None:
        nonlocal call_count
        call_count += 1
        return None

    assert return_none() is None
    assert return_none() is None
    assert call_count == 1
    assert return_none.cache_info().hits == 1


def test_kwargs_are_part_of_cache_key():
    """Different kwargs produce different cache entries."""
    @ttl_cache(maxsize=10, ttl=60.0)
    def greet(name: str, greeting: str = "hello") -> str:
        return f"{greeting} {name}"

    assert greet("alice") == "hello alice"
    assert greet("alice", greeting="hi") == "hi alice"
    assert greet.cache_info().misses == 2
    assert greet.cache_info().currsize == 2


def test_sorted_kwargs_same_key():
    """Keyword args in different order produce the same cache key."""
    call_count = 0

    @ttl_cache(maxsize=10, ttl=60.0)
    def combine(a: int = 0, b: int = 0) -> int:
        nonlocal call_count
        call_count += 1
        return a + b

    assert combine(a=1, b=2) == 3
    assert combine(b=2, a=1) == 3
    assert call_count == 1
    assert combine.cache_info().hits == 1


def test_preserves_function_metadata():
    """Decorated function preserves original name and docstring."""
    @ttl_cache()
    def documented_func(x: int) -> int:
        """This is a docstring."""
        return x

    assert documented_func.__name__ == "documented_func"
    assert documented_func.__doc__ == "This is a docstring."


def test_thread_safety():
    """Cache is safe under concurrent access from multiple threads."""
    call_count = 0
    count_lock = threading.Lock()

    @ttl_cache(maxsize=100, ttl=60.0)
    def slow_square(x: int) -> int:
        nonlocal call_count
        with count_lock:
            call_count += 1
        time.sleep(0.01)
        return x * x

    threads = []
    results = []
    results_lock = threading.Lock()

    def worker(val: int) -> None:
        result = slow_square(val)
        with results_lock:
            results.append(result)

    for _ in range(10):
        for v in range(5):
            t = threading.Thread(target=worker, args=(v,))
            threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 50
    for v in range(5):
        assert v * v in results

    info = slow_square.cache_info()
    assert info.hits + info.misses == 50
    assert info.currsize == 5


def test_example_from_spec():
    """Verify the exact example from the task specification."""
    call_count = 0

    @ttl_cache(maxsize=100, ttl=60.0)
    def get_user(user_id: int) -> dict:
        nonlocal call_count
        call_count += 1
        return {"id": user_id, "name": f"user_{user_id}"}

    result = get_user(42)
    assert result == {"id": 42, "name": "user_42"}

    result = get_user(42)
    assert result == {"id": 42, "name": "user_42"}

    info = get_user.cache_info()
    assert info.hits == 1
    assert info.misses == 1
    assert info.currsize == 1
    assert info.maxsize == 100

    get_user.cache_clear()
    info = get_user.cache_info()
    assert info.hits == 0
    assert info.misses == 0
    assert info.currsize == 0
