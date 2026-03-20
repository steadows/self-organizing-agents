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

    On each retry attempt n (0-indexed), the delay is computed as
    ``min(base_delay * (2 ** n), max_delay)``, then jitter is applied by
    selecting a random value uniformly between 0 and that delay.

    Args:
        max_retries: Maximum number of retry attempts after the initial call.
            Must be >= 0.  A value of 0 means the function is called exactly
            once with no retry.
        base_delay: Starting delay in seconds for the first retry.
        max_delay: Upper bound on the delay (before jitter) in seconds.
        exceptions: Tuple of exception types that should trigger a retry.
            Any other exception propagates immediately.

    Returns:
        A decorator that wraps the target function with retry logic.

    Raises:
        ValueError: If ``max_retries`` is negative, raised at decoration time.
    """
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: BaseException | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        jittered = random.uniform(0, delay)
                        time.sleep(jittered)

            raise last_exception  # type: ignore[misc]

        return wrapper

    return decorator
