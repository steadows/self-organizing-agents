# Task 004: retry_with_backoff

## Function Signature

```python
import functools

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
):
    """Decorator that retries the wrapped function with exponential backoff and jitter."""
    ...
```

## Description

A decorator factory that retries a function call when it raises a specified exception. Each retry waits with exponential backoff plus random jitter. After all retries are exhausted, the last exception is re-raised.

## Requirements

- Implement as a decorator factory: `@retry_with_backoff(max_retries=5)` decorates a function.
- On each retry attempt `n` (0-indexed), compute the delay as `min(base_delay * (2 ** n), max_delay)`, then apply jitter by selecting a random value uniformly between `0` and the computed delay (use `random.uniform(0, delay)`).
- Sleep for the jittered delay between retries (use `time.sleep`).
- Only catch exceptions that are instances of the types listed in `exceptions`. All other exceptions propagate immediately.
- After `max_retries` failed attempts (i.e., `max_retries + 1` total calls including the initial attempt), re-raise the last caught exception.
- Use `functools.wraps` to preserve the decorated function's `__name__`, `__doc__`, and signature.
- If `max_retries` is `0`, the function is called exactly once with no retry.
- If `max_retries` is negative, raise `ValueError` at decoration time.
- No external dependencies; use only `functools`, `time`, `random`.

## Edge Cases

- `max_retries=0`: function is called once; if it raises, the exception propagates immediately.
- `max_retries < 0`: raise `ValueError("max_retries must be >= 0")` when the decorator is applied.
- Function succeeds on the first call: no retries, no delay, return result immediately.
- Function succeeds on a retry: return the successful result, stop retrying.
- Function raises an exception not in `exceptions`: exception propagates immediately, no retry.
- `base_delay=0`: all delays are 0 (retries happen immediately).
- `max_delay` less than `base_delay`: delay is capped at `max_delay` from the first retry.

## Examples

```python
# Basic usage
@retry_with_backoff(max_retries=3, base_delay=0.5)
def fetch_data(url: str) -> dict:
    """Fetch data from a remote API."""
    ...

# Retry only on specific exceptions
@retry_with_backoff(max_retries=5, exceptions=(ConnectionError, TimeoutError))
def connect(host: str) -> None:
    ...

# No retries
@retry_with_backoff(max_retries=0)
def fragile() -> None:
    ...

# Decorated function preserves metadata
assert fetch_data.__name__ == "fetch_data"
assert fetch_data.__doc__ == "Fetch data from a remote API."
```

## Scope Boundary

- NO circuit breaker pattern.
- NO retry budgets or global retry counters.
- NO async / `asyncio` support.
- NO logging (the caller is responsible for logging).
- NO callback hooks (on_retry, on_success, on_failure).
- NO per-exception backoff strategies.
