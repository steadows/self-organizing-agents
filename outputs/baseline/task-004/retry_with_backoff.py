"""Decorator that retries a function call with exponential backoff and jitter."""

import functools
import random
import time
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
) -> Callable[[F], F]:
    """Decorator factory that retries the wrapped function with exponential backoff and jitter.

    Args:
        max_retries: Maximum number of retry attempts after the initial call.
            Must be >= 0. If 0, the function is called once with no retry.
        base_delay: Base delay in seconds for exponential backoff calculation.
        max_delay: Maximum delay cap in seconds.
        exceptions: Tuple of exception types to catch and retry on.
            Other exceptions propagate immediately.

    Returns:
        A decorator that wraps the target function with retry logic.

    Raises:
        ValueError: If max_retries is negative.
    """
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: BaseException | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        jittered_delay = random.uniform(0, delay)
                        time.sleep(jittered_delay)

            raise last_exception  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator
