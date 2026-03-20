"""Utility providing a retry_with_backoff decorator with exponential backoff and jitter."""

import functools
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 60.0


def retry_with_backoff(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator factory that retries the wrapped function with exponential backoff and jitter.

    On each retry attempt ``n`` (0-indexed), the delay is computed as
    ``min(base_delay * (2 ** n), max_delay)`` and then jittered by sampling
    uniformly from ``[0, delay]``.  The function is called at most
    ``max_retries + 1`` times.  If every attempt raises an exception listed in
    ``exceptions``, the last caught exception is re-raised.  Exceptions not in
    ``exceptions`` propagate immediately without retrying.

    Parameters
    ----------
    max_retries:
        Maximum number of retry attempts after the initial call.  Must be >= 0.
    base_delay:
        Base delay in seconds for the exponential backoff calculation.
    max_delay:
        Upper bound in seconds for the computed (pre-jitter) delay.
    exceptions:
        Tuple of exception types that should trigger a retry.  Any exception
        not in this tuple propagates immediately.

    Returns
    -------
    Callable[[Callable[..., T]], Callable[..., T]]
        A decorator that wraps the target function with retry logic.

    Raises
    ------
    ValueError
        If ``max_retries`` is negative.

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

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Wrap *func* with retry-with-backoff logic."""

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> T:
            """Invoke *func*, retrying on allowed exceptions with exponential backoff."""
            last_exc: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_retries:
                        delay = min(base_delay * (2**attempt), max_delay)
                        jittered = random.uniform(0, delay)
                        time.sleep(jittered)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
