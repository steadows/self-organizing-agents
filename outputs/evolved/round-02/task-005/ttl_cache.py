"""TTL-aware LRU cache decorator for Python functions.

Provides a decorator factory that caches function return values with both
LRU (Least Recently Used) eviction and time-based expiration. The cache
is thread-safe and exposes cache_info() and cache_clear() on decorated functions.
"""

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
    maxsize : int
        Maximum number of entries to store. When exceeded, the least recently
        used entry is evicted. If 0, caching is disabled and the function is
        always called. Must be >= 0.
    ttl : float
        Time-to-live in seconds for each cached entry. Entries accessed after
        this interval are treated as cache misses. If 0, caching is disabled.
        Must be >= 0.

    Returns
    -------
    Callable
        A decorator that wraps a function with TTL-aware LRU caching.

    Raises
    ------
    ValueError
        If ``ttl < 0`` or ``maxsize < 0``.

    Examples
    --------
    >>> @ttl_cache(maxsize=100, ttl=60.0)
    ... def get_user(user_id: int) -> dict:
    ...     return {"id": user_id}
    >>> result = get_user(42)
    >>> info = get_user.cache_info()
    >>> info.misses
    1
    >>> result2 = get_user(42)
    >>> get_user.cache_info().hits
    1
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

            # Build cache key — raises TypeError if args are unhashable
            try:
                key = (args, tuple(sorted(kwargs.items())))
                hash(key)
            except TypeError:
                raise TypeError(
                    "All arguments must be hashable to use ttl_cache"
                )

            # Caching fully disabled
            if maxsize == 0 or ttl == 0:
                with lock:
                    misses += 1
                return func(*args, **kwargs)

            now = time.monotonic()

            with lock:
                entry = cache.get(key, _SENTINEL)
                if entry is not _SENTINEL:
                    value, inserted_at = entry
                    if now - inserted_at <= ttl:
                        # Valid hit — move to end (most recently used)
                        cache.move_to_end(key)
                        hits += 1
                        return value
                    # Expired — remove stale entry
                    del cache[key]

                misses += 1

            # Call outside lock to avoid holding it during potentially slow I/O
            result = func(*args, **kwargs)

            with lock:
                # Another thread may have populated the same key while we were
                # computing; prefer the freshest write (ours).
                cache[key] = (result, time.monotonic())
                cache.move_to_end(key)
                # Evict LRU entries if over capacity
                while len(cache) > maxsize:
                    cache.popitem(last=False)

            return result

        def cache_info() -> CacheInfo:
            """Return a snapshot of the cache statistics.

            Returns
            -------
            CacheInfo
                Named tuple with fields: hits, misses, maxsize, currsize.
            """
            with lock:
                return CacheInfo(
                    hits=hits,
                    misses=misses,
                    maxsize=maxsize,
                    currsize=len(cache),
                )

        def cache_clear() -> None:
            """Empty the cache and reset hit/miss counters to zero."""
            nonlocal hits, misses
            with lock:
                cache.clear()
                hits = 0
                misses = 0

        wrapper.cache_info = cache_info  # type: ignore[attr-defined]
        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        return wrapper

    return decorator
