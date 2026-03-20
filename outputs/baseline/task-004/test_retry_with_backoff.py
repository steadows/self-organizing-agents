"""Tests for retry_with_backoff decorator."""

from unittest.mock import patch

import pytest

from retry_with_backoff import retry_with_backoff


def test_succeeds_on_first_call() -> None:
    """Function that succeeds immediately returns result with no retries."""
    @retry_with_backoff(max_retries=3, base_delay=0.0)
    def succeed() -> str:
        return "ok"

    assert succeed() == "ok"


def test_succeeds_on_retry() -> None:
    """Function that fails then succeeds returns the successful result."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.0)
    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("not yet")
        return "done"

    assert flaky() == "done"
    assert call_count == 3


def test_raises_after_all_retries_exhausted() -> None:
    """After max_retries failed attempts, the last exception is re-raised."""
    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0.0)
    def always_fails() -> None:
        nonlocal call_count
        call_count += 1
        raise RuntimeError(f"fail {call_count}")

    with pytest.raises(RuntimeError, match="fail 3"):
        always_fails()

    assert call_count == 3  # 1 initial + 2 retries


def test_max_retries_zero_no_retry() -> None:
    """With max_retries=0, function is called once; exception propagates."""
    call_count = 0

    @retry_with_backoff(max_retries=0, base_delay=0.0)
    def fail_once() -> None:
        nonlocal call_count
        call_count += 1
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        fail_once()

    assert call_count == 1


def test_negative_max_retries_raises_valueerror() -> None:
    """Negative max_retries raises ValueError at decoration time."""
    with pytest.raises(ValueError, match="max_retries must be >= 0"):
        @retry_with_backoff(max_retries=-1)
        def noop() -> None:
            pass


def test_only_catches_specified_exceptions() -> None:
    """Exceptions not in the exceptions tuple propagate immediately."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.0, exceptions=(ValueError,))
    def raises_type_error() -> None:
        nonlocal call_count
        call_count += 1
        raise TypeError("wrong type")

    with pytest.raises(TypeError, match="wrong type"):
        raises_type_error()

    assert call_count == 1  # No retry for TypeError


def test_preserves_function_metadata() -> None:
    """Decorated function preserves __name__ and __doc__."""
    @retry_with_backoff(max_retries=1)
    def my_func() -> None:
        """My docstring."""
        pass

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "My docstring."


def test_exponential_backoff_with_cap() -> None:
    """Verify delay computation uses exponential backoff capped at max_delay."""
    sleep_calls: list[float] = []

    @retry_with_backoff(max_retries=5, base_delay=1.0, max_delay=5.0)
    def always_fails() -> None:
        raise RuntimeError("fail")

    with patch("retry_with_backoff.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
        with patch("retry_with_backoff.random.uniform", side_effect=lambda a, b: b):
            with pytest.raises(RuntimeError):
                always_fails()

    # With jitter returning max (uniform returning b), delays should be:
    # attempt 0: min(1*2^0, 5) = 1.0
    # attempt 1: min(1*2^1, 5) = 2.0
    # attempt 2: min(1*2^2, 5) = 4.0
    # attempt 3: min(1*2^3, 5) = 5.0 (capped)
    # attempt 4: min(1*2^4, 5) = 5.0 (capped)
    assert sleep_calls == [1.0, 2.0, 4.0, 5.0, 5.0]


def test_base_delay_zero_retries_immediately() -> None:
    """With base_delay=0, all delays are 0."""
    sleep_calls: list[float] = []
    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0.0)
    def fails() -> None:
        nonlocal call_count
        call_count += 1
        raise RuntimeError("fail")

    with patch("retry_with_backoff.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
        with pytest.raises(RuntimeError):
            fails()

    assert call_count == 3
    # uniform(0, 0) == 0 for all retries
    for delay in sleep_calls:
        assert delay == 0.0


def test_max_delay_less_than_base_delay() -> None:
    """When max_delay < base_delay, delay is capped at max_delay from the first retry."""
    sleep_calls: list[float] = []

    @retry_with_backoff(max_retries=2, base_delay=10.0, max_delay=1.0)
    def fails() -> None:
        raise RuntimeError("fail")

    with patch("retry_with_backoff.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
        with patch("retry_with_backoff.random.uniform", side_effect=lambda a, b: b):
            with pytest.raises(RuntimeError):
                fails()

    # min(10*2^0, 1) = 1.0 for all attempts
    assert sleep_calls == [1.0, 1.0]


def test_passes_args_and_kwargs() -> None:
    """Arguments and keyword arguments are forwarded to the wrapped function."""
    @retry_with_backoff(max_retries=0)
    def add(a: int, b: int, offset: int = 0) -> int:
        """Add numbers."""
        return a + b + offset

    assert add(1, 2) == 3
    assert add(1, 2, offset=10) == 13
