"""Tests for retry_with_backoff decorator."""

import time
from unittest.mock import MagicMock, patch

import pytest

from retry_with_backoff import retry_with_backoff


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_succeeds_on_first_call_no_retries():
    """Function that never raises should return immediately without sleeping."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def always_succeeds() -> str:
        nonlocal call_count
        call_count += 1
        return "ok"

    with patch("time.sleep") as mock_sleep:
        result = always_succeeds()

    assert result == "ok"
    assert call_count == 1
    mock_sleep.assert_not_called()


def test_succeeds_on_retry_returns_result():
    """Function that fails once then succeeds should return the successful result."""
    attempts = []

    @retry_with_backoff(max_retries=3, base_delay=0.0)
    def flaky() -> str:
        attempts.append(1)
        if len(attempts) < 2:
            raise ValueError("not ready")
        return "ready"

    with patch("time.sleep"):
        result = flaky()

    assert result == "ready"
    assert len(attempts) == 2


def test_retries_correct_number_of_times_before_raising():
    """Should attempt max_retries + 1 times total then re-raise."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.0)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("boom")

    with patch("time.sleep"):
        with pytest.raises(RuntimeError, match="boom"):
            always_fails()

    assert call_count == 4  # 1 initial + 3 retries


def test_re_raises_last_exception():
    """The exception re-raised after exhausting retries should be the last one."""
    counter = [0]

    @retry_with_backoff(max_retries=2, base_delay=0.0)
    def cycling_errors():
        counter[0] += 1
        raise ValueError(f"attempt {counter[0]}")

    with patch("time.sleep"):
        with pytest.raises(ValueError, match="attempt 3"):
            cycling_errors()


# ---------------------------------------------------------------------------
# Backoff and jitter tests
# ---------------------------------------------------------------------------


def test_sleep_called_between_retries_not_after_last():
    """time.sleep should be called max_retries times (not after the last attempt)."""
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep") as mock_sleep, patch("random.uniform", return_value=0.5):
        with pytest.raises(RuntimeError):
            always_fails()

    assert mock_sleep.call_count == 3


def test_exponential_backoff_delay_computation():
    """Delays passed to sleep should follow exponential backoff capped at max_delay."""
    recorded_delays = []

    def fake_uniform(lo, hi):
        recorded_delays.append(hi)
        return hi

    @retry_with_backoff(max_retries=4, base_delay=1.0, max_delay=5.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep"), patch("random.uniform", side_effect=fake_uniform):
        with pytest.raises(RuntimeError):
            always_fails()

    # Attempt 0 → delay = min(1*1, 5) = 1
    # Attempt 1 → delay = min(1*2, 5) = 2
    # Attempt 2 → delay = min(1*4, 5) = 4
    # Attempt 3 → delay = min(1*8, 5) = 5
    assert recorded_delays == [1.0, 2.0, 4.0, 5.0]


def test_max_delay_caps_computed_delay():
    """max_delay less than base_delay should cap from the first retry."""
    recorded_hi = []

    def fake_uniform(lo, hi):
        recorded_hi.append(hi)
        return hi

    @retry_with_backoff(max_retries=3, base_delay=10.0, max_delay=2.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep"), patch("random.uniform", side_effect=fake_uniform):
        with pytest.raises(RuntimeError):
            always_fails()

    assert all(d == 2.0 for d in recorded_hi)


def test_base_delay_zero_sleeps_for_zero():
    """With base_delay=0, all sleep durations should be 0."""
    sleep_durations = []

    @retry_with_backoff(max_retries=2, base_delay=0.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep", side_effect=lambda t: sleep_durations.append(t)), \
         patch("random.uniform", side_effect=lambda lo, hi: hi):
        with pytest.raises(RuntimeError):
            always_fails()

    assert sleep_durations == [0.0, 0.0]


# ---------------------------------------------------------------------------
# Exception filtering tests
# ---------------------------------------------------------------------------


def test_non_matching_exception_propagates_immediately():
    """Exceptions not in the exceptions tuple should propagate without retry."""
    call_count = 0

    @retry_with_backoff(max_retries=5, base_delay=0.0, exceptions=(ConnectionError,))
    def raises_value_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("unexpected")

    with patch("time.sleep"):
        with pytest.raises(ValueError):
            raises_value_error()

    assert call_count == 1


def test_matching_exception_triggers_retry():
    """Only matching exceptions should trigger retries."""
    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0.0, exceptions=(ConnectionError,))
    def raises_connection_error():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("lost")

    with patch("time.sleep"):
        with pytest.raises(ConnectionError):
            raises_connection_error()

    assert call_count == 3


def test_multiple_exception_types():
    """Both exception types in the tuple should trigger retries."""
    results = []

    @retry_with_backoff(
        max_retries=3, base_delay=0.0, exceptions=(ConnectionError, TimeoutError)
    )
    def alternating():
        results.append(len(results))
        if len(results) % 2 == 1:
            raise ConnectionError("conn")
        raise TimeoutError("timeout")

    with patch("time.sleep"):
        with pytest.raises((ConnectionError, TimeoutError)):
            alternating()

    assert len(results) == 4


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_max_retries_zero_calls_once_then_raises():
    """max_retries=0 means one call; exception should propagate immediately."""
    call_count = 0

    @retry_with_backoff(max_retries=0)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("once")

    with patch("time.sleep") as mock_sleep:
        with pytest.raises(RuntimeError):
            always_fails()

    assert call_count == 1
    mock_sleep.assert_not_called()


def test_max_retries_zero_success():
    """max_retries=0 with a succeeding function should return normally."""

    @retry_with_backoff(max_retries=0)
    def fine() -> int:
        return 42

    assert fine() == 42


def test_negative_max_retries_raises_value_error_at_decoration():
    """Negative max_retries should raise ValueError when the decorator is applied."""
    with pytest.raises(ValueError, match="max_retries must be >= 0"):

        @retry_with_backoff(max_retries=-1)
        def func():
            pass


# ---------------------------------------------------------------------------
# Metadata preservation
# ---------------------------------------------------------------------------


def test_functools_wraps_preserves_name():
    """Decorated function should retain its __name__."""

    @retry_with_backoff(max_retries=1)
    def my_function():
        """My docstring."""

    assert my_function.__name__ == "my_function"


def test_functools_wraps_preserves_doc():
    """Decorated function should retain its __doc__."""

    @retry_with_backoff(max_retries=1)
    def my_function():
        """My docstring."""

    assert my_function.__doc__ == "My docstring."
