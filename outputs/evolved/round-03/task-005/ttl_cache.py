"""TTL-aware LRU cache decorator for Python functions.

Provides a decorator factory that caches function return values with
LRU eviction and time-based (TTL) expiration. Thread-safe.
"""

import time
import threading
import functools
from collections import OrderedDict, namedtuple
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])


def ttl_cache(maxsize: int = 128, ttl: float = 300.0) -> Callable[[F], F]:
    """Decorator that caches function results with LRU eviction and time-based expiration.

    Parameters:
        maxsize: Maximum number of entries to keep in the cache. When exceeded,
            the least recently used entry is evicted. If 0, caching is disabled.
        ttl: Time-to-live in seconds for each cache entry. Entries older than
            this are treated as misses and removed on access. If 0, caching
            is disabled. Must be >= 0.

    Returns:
        A decorator that wraps the target function with caching behaviour.
        The wrapped function exposes two additional attributes:
            - ``cache_info()`` — returns a ``CacheInfo`` named tuple with
              ``hits``, ``misses``, ``maxsize``, and ``currsize``.
            - ``cache_clear()`` — empties the cache and resets counters.

    Raises:
        ValueError: If ``maxsize < 0`` or ``ttl < 0``.
        TypeError: At call time if any argument is not hashable.

    Examples:
        >>> @ttl_cache(maxsize=100, ttl=60.0)
        ... def get_user(user_id: int) -> dict:
        ...     return {"id": user_id}
        >>> get_user(1)
        {'id': 1}
        >>> get_user(1)  # cache hit
        {'id': 1}
        >>> info = get_user.cache_info()
        >>> info.hits
        1
        >>> info.misses
        1
    """
    if maxsize < 0:
        raise ValueError("maxsize must be >= 0")
    if ttl < 0:
        raise ValueError("ttl must be >= 0")

    def decorator(func: F) -> F:
        """Wrap *func* with TTL-aware LRU caching."""
        cache: OrderedDict[tuple[Any, ...], tuple[Any, float]] = OrderedDict()
        lock = threading.Lock()
        hits = 0
        misses = 0

        # Caching is disabled when maxsize == 0 or ttl == 0
        caching_enabled = maxsize > 0 and ttl > 0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses

            cache_key = _make_key(args, kwargs)

            if caching_enabled:
                with lock:
                    entry = cache.get(cache_key)
                    if entry is not None:
                        value, insert_time = entry
                        if time.monotonic() - insert_time <= ttl:
                            # Valid hit — move to most-recently-used end
                            cache.move_to_end(cache_key)
                            hits += 1
                            return value
                        # Expired — remove and fall through to miss
                        del cache[cache_key]

                    misses += 1

                result = func(*args, **kwargs)

                with lock:
                    # Another thread may have populated the same key; overwrite.
                    cache[cache_key] = (result, time.monotonic())
                    cache.move_to_end(cache_key)
                    # Evict LRU entry if over capacity
                    if len(cache) > maxsize:
                        cache.popitem(last=False)

                return result

            # Caching disabled path
            with lock:
                misses += 1
            return func(*args, **kwargs)

        def cache_info() -> CacheInfo:
            """Return a snapshot of the current cache statistics.

            Returns a ``CacheInfo`` named tuple with fields:
            ``hits``, ``misses``, ``maxsize``, ``currsize``.
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

        return wrapper  # type: ignore[return-value]

    return decorator


def _make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Any, ...]:
    """Build a hashable cache key from positional and keyword arguments.

    Keyword arguments are sorted by name so that ``f(a=1, b=2)`` and
    ``f(b=2, a=1)`` produce the same key.

    Raises:
        TypeError: If any argument is not hashable.
    """
    key: tuple[Any, ...] = args + tuple(sorted(kwargs.items()))
    # Validate hashability eagerly so the caller gets a clear TypeError.
    hash(key)
    return key
