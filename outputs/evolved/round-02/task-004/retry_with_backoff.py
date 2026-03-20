"""Decorator factory that retries a function with exponential backoff and jitter."""

import functools
import random
import time


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
):
    """Decorator that retries the wrapped function with exponential backoff and jitter.

    On each retry attempt n (0-indexed), the delay is computed as:
        delay = min(base_delay * (2 ** n), max_delay)
    then jitter is applied by selecting a random value uniformly in [0, delay].

    After max_retries failed attempts (max_retries + 1 total calls), the last
    exception is re-raised. Exceptions not listed in ``exceptions`` propagate
    immediately without retry.

    Parameters
    ----------
    max_retries:
        Maximum number of retry attempts after the initial call. Must be >= 0.
    base_delay:
        Base delay in seconds for the exponential backoff calculation.
    max_delay:
        Upper bound on the computed delay (before jitter) in seconds.
    exceptions:
        Tuple of exception types that trigger a retry. All other exceptions
        propagate immediately.

    Returns
    -------
    Callable
        A decorator that wraps the target function with retry logic.

    Raises
    ------
    ValueError
        If ``max_retries`` is negative, raised at decoration time.

    Examples
    --------
    >>> call_count = 0
    >>> @retry_with_backoff(max_retries=2, base_delay=0.0)
    ... def always_succeeds() -> str:
    ...     return "ok"
    >>> always_succeeds()
    'ok'
    """
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        sleep_time = random.uniform(0, delay)
                        time.sleep(sleep_time)
            raise last_exception

        return wrapper

    return decorator
