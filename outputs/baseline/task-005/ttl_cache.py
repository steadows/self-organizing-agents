"""TTL cache decorator with LRU eviction and time-based expiration."""

import functools
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, NamedTuple


class CacheInfo(NamedTuple):
    """Cache statistics."""

    hits: int
    misses: int
    maxsize: int
    currsize: int


def _make_key(args: tuple, kwargs: dict) -> tuple:
    """Build a hashable cache key from function arguments.

    Args:
        args: Positional arguments.
        kwargs: Keyword arguments.

    Returns:
        A hashable tuple representing the call signature.

    Raises:
        TypeError: If any argument is not hashable.
    """
    key: tuple = args
    if kwargs:
        sorted_items = tuple(sorted(kwargs.items()))
        key += sorted_items
    # Validate hashability by attempting to hash the key
    hash(key)
    return key


def ttl_cache(maxsize: int = 128, ttl: float = 300.0) -> Callable:
    """Decorator factory that caches function results with LRU eviction and TTL expiration.

    Args:
        maxsize: Maximum number of entries in the cache. 0 disables caching.
        ttl: Time-to-live in seconds for each cache entry. 0 disables caching.

    Returns:
        A decorator that wraps a function with caching behavior.

    Raises:
        ValueError: If maxsize < 0 or ttl < 0.
    """
    if maxsize < 0:
        raise ValueError("maxsize must be >= 0")
    if ttl < 0:
        raise ValueError("ttl must be >= 0")

    def decorator(func: Callable) -> Callable:
        cache: OrderedDict[tuple, tuple[Any, float]] = OrderedDict()
        lock = threading.Lock()
        hits = 0
        misses = 0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses

            # When caching is disabled, always execute
            if maxsize == 0 or ttl == 0:
                with lock:
                    misses += 1
                return func(*args, **kwargs)

            key = _make_key(args, kwargs)

            with lock:
                if key in cache:
                    value, timestamp = cache[key]
                    if time.monotonic() - timestamp <= ttl:
                        # Valid hit: move to end for LRU ordering
                        cache.move_to_end(key)
                        hits += 1
                        return value
                    # Expired entry: remove it
                    del cache[key]

                # Cache miss: execute the function outside the lock scope
                misses += 1

            result = func(*args, **kwargs)

            with lock:
                # Insert new entry
                cache[key] = (result, time.monotonic())
                cache.move_to_end(key)
                # Evict oldest entries if over capacity
                while len(cache) > maxsize:
                    cache.popitem(last=False)

            return result

        def cache_info() -> CacheInfo:
            """Return cache statistics.

            Returns:
                A CacheInfo named tuple with hits, misses, maxsize, and currsize.
            """
            with lock:
                return CacheInfo(
                    hits=hits,
                    misses=misses,
                    maxsize=maxsize,
                    currsize=len(cache),
                )

        def cache_clear() -> None:
            """Clear the cache and reset statistics."""
            nonlocal hits, misses
            with lock:
                cache.clear()
                hits = 0
                misses = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper

    return decorator
