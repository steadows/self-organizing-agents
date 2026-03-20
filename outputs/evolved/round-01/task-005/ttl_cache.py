"""TTL-aware LRU cache decorator using only standard library components."""

import functools
import threading
import time
from collections import OrderedDict, namedtuple
from typing import Any, Callable


CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

_SENTINEL = object()


def ttl_cache(maxsize: int = 128, ttl: float = 300.0) -> Callable:
    """Decorator that caches function results with LRU eviction and time-based expiration.

    Parameters
    ----------
    maxsize:
        Maximum number of entries to keep in the cache. If 0, caching is disabled
        and every call executes the function directly.
    ttl:
        Time-to-live in seconds for each cache entry. If 0, caching is disabled.
        Must be >= 0.

    Returns
    -------
    Callable
        A decorator that wraps the target function with caching behaviour.

    Raises
    ------
    ValueError
        If ``ttl < 0`` or ``maxsize < 0``.
    """
    if ttl < 0:
        raise ValueError("ttl must be >= 0")
    if maxsize < 0:
        raise ValueError("maxsize must be >= 0")

    def decorator(func: Callable) -> Callable:
        cache: OrderedDict[Any, tuple[Any, float]] = OrderedDict()
        lock = threading.Lock()
        hits = 0
        misses = 0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses

            # Build cache key — raises TypeError for unhashable args
            try:
                key = (args, tuple(sorted(kwargs.items())))
                hash(key)
            except TypeError:
                raise TypeError(
                    f"Arguments to {func.__name__!r} are not hashable and cannot be cached"
                )

            # Caching disabled when maxsize=0 or ttl=0
            if maxsize == 0 or ttl == 0:
                with lock:
                    misses += 1
                return func(*args, **kwargs)

            now = time.monotonic()

            with lock:
                entry = cache.get(key, _SENTINEL)
                if entry is not _SENTINEL:
                    value, insert_time = entry
                    if now - insert_time <= ttl:
                        # Valid hit — move to end (most recently used)
                        cache.move_to_end(key)
                        hits += 1
                        return value
                    else:
                        # Expired — remove and treat as miss
                        del cache[key]

                misses += 1

            # Compute outside the lock to avoid holding it during potentially
            # expensive function execution.
            result = func(*args, **kwargs)

            with lock:
                # Another thread may have populated the key while we were
                # computing; overwrite with our fresh result.
                cache[key] = (result, time.monotonic())
                cache.move_to_end(key)

                # Evict LRU entries until we are within maxsize
                while len(cache) > maxsize:
                    cache.popitem(last=False)

            return result

        def cache_info() -> CacheInfo:
            """Return a snapshot of current cache statistics."""
            with lock:
                return CacheInfo(
                    hits=hits,
                    misses=misses,
                    maxsize=maxsize,
                    currsize=len(cache),
                )

        def cache_clear() -> None:
            """Clear all cached entries and reset hit/miss counters."""
            nonlocal hits, misses
            with lock:
                cache.clear()
                hits = 0
                misses = 0

        wrapper.cache_info = cache_info  # type: ignore[attr-defined]
        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        return wrapper

    return decorator
