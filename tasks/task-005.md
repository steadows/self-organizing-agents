# Task 005: ttl_cache

## Function Signature

```python
def ttl_cache(maxsize: int = 128, ttl: float = 300.0):
    """Decorator that caches function results with LRU eviction and time-based expiration."""
    ...
```

## Description

A decorator factory that caches the return value of a function, keyed by its arguments. Entries expire after `ttl` seconds and are evicted in LRU order when the cache exceeds `maxsize`. The cache is thread-safe.

## Requirements

- Implement as a decorator factory: `@ttl_cache(maxsize=256, ttl=60.0)` decorates a function.
- Cache key is derived from the function's positional args and sorted keyword args. All arguments must be hashable; raise `TypeError` if they are not.
- Use `collections.OrderedDict` (or equivalent) for LRU ordering: move accessed entries to the end, evict from the front when size exceeds `maxsize`.
- Each cache entry stores the return value and the timestamp when it was inserted (use `time.monotonic()`).
- On cache hit, check if the entry has expired (`current_time - insertion_time > ttl`). If expired, remove it and treat as a cache miss.
- All cache reads and writes must be protected by a `threading.Lock`.
- Use `functools.wraps` to preserve the decorated function's metadata.
- Expose `cache_info()` on the decorated function, returning a named tuple or object with: `hits`, `misses`, `maxsize`, `currsize`.
- Expose `cache_clear()` on the decorated function, which empties the cache and resets hit/miss counters to 0.
- If `maxsize=0`: caching is disabled, every call executes the function (still track hits=0 and misses).
- If `ttl=0`: caching is disabled, every call executes the function.
- If `ttl < 0`: raise `ValueError("ttl must be >= 0")` at decoration time.
- If `maxsize < 0`: raise `ValueError("maxsize must be >= 0")` at decoration time.
- No external dependencies; use only `functools`, `collections`, `threading`, `time`.

## Edge Cases

- Unhashable arguments (e.g., passing a `list`): raise `TypeError` immediately, do not cache.
- `maxsize=0`: function always executes, `cache_info().currsize` is always `0`, `hits` is always `0`.
- `ttl=0`: function always executes, no entries are ever stored.
- Function with no arguments: cache has a single entry keyed to `()`.
- Concurrent access from multiple threads: all operations are safe under the lock.
- `cache_clear()` resets `hits` and `misses` to `0` and removes all entries.
- Function that returns `None`: `None` is a valid cached value.

## Examples

```python
@ttl_cache(maxsize=100, ttl=60.0)
def get_user(user_id: int) -> dict:
    """Look up a user by ID."""
    ...

# First call: miss, executes function
result = get_user(42)

# Second call with same args within TTL: hit, returns cached value
result = get_user(42)

# Check cache stats
info = get_user.cache_info()
assert info.hits == 1
assert info.misses == 1
assert info.currsize == 1
assert info.maxsize == 100

# Clear everything
get_user.cache_clear()
info = get_user.cache_info()
assert info.hits == 0
assert info.misses == 0
assert info.currsize == 0

# Unhashable args raise TypeError
@ttl_cache()
def bad(x):
    return x

bad([1, 2, 3])  # raises TypeError

# Disabled caching
@ttl_cache(maxsize=0)
def always_fresh(x: int) -> int:
    return x * 2
```

## Scope Boundary

- NO distributed or shared-memory caching.
- NO async / `asyncio` support.
- NO disk-backed or persistent cache.
- NO per-key TTL (all entries share the same TTL).
- NO cache warming or pre-population API.
- NO automatic background expiration (entries are only evicted on access or when space is needed).
