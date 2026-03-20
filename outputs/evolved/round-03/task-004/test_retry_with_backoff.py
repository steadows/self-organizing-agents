"""Tests for the retry_with_backoff decorator."""

from unittest.mock import MagicMock, call, patch

import pytest

from retry_with_backoff import retry_with_backoff


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_succeeds_on_first_call_returns_result() -> None:
    """Function that never raises should return its result immediately."""

    @retry_with_backoff(max_retries=3, base_delay=0.0)
    def always_ok() -> str:
        return "success"

    assert always_ok() == "success"


def test_no_sleep_when_first_call_succeeds() -> None:
    """time.sleep must not be called when the first attempt succeeds."""
    with patch("retry_with_backoff.time.sleep") as mock_sleep:

        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def ok() -> int:
            return 42

        result = ok()

    assert result == 42
    mock_sleep.assert_not_called()


def test_retries_and_succeeds_on_second_attempt() -> None:
    """Function that fails once then succeeds should return the successful result."""
    attempts: list[int] = []

    with patch("retry_with_backoff.time.sleep"):

        @retry_with_backoff(max_retries=3, base_delay=0.0)
        def flaky() -> str:
            attempts.append(1)
            if len(attempts) < 2:
                raise ValueError("temporary failure")
            return "recovered"

        result = flaky()

    assert result == "recovered"
    assert len(attempts) == 2


def test_sleep_called_between_retries() -> None:
    """time.sleep should be called once per retry (not after the final failure)."""
    side_effects = [RuntimeError("fail")] * 3 + [None]
    mock_func = MagicMock(side_effect=side_effects)
    mock_func.__name__ = "mock_func"
    mock_func.__doc__ = None
    mock_func.__wrapped__ = None

    with patch("retry_with_backoff.time.sleep") as mock_sleep, patch(
        "retry_with_backoff.random.uniform", return_value=0.5
    ):
        decorated = retry_with_backoff(max_retries=3, base_delay=1.0)(mock_func)
        decorated()

    assert mock_sleep.call_count == 3


def test_exponential_backoff_delay_computation() -> None:
    """Delays passed to sleep should follow exponential backoff (pre-jitter)."""
    recorded_uniform_calls: list[tuple[float, float]] = []

    def capture_uniform(lo: float, hi: float) -> float:
        """Record arguments and return zero for determinism."""
        recorded_uniform_calls.append((lo, hi))
        return 0.0

    side_effects = [RuntimeError()] * 4 + ["ok"]
    mock_func = MagicMock(side_effect=side_effects)
    mock_func.__name__ = "f"
    mock_func.__doc__ = None
    mock_func.__wrapped__ = None

    with patch("retry_with_backoff.time.sleep"), patch(
        "retry_with_backoff.random.uniform", side_effect=capture_uniform
    ):
        decorated = retry_with_backoff(max_retries=4, base_delay=2.0, max_delay=60.0)(
            mock_func
        )
        decorated()

    # Delays for attempts 0..3: min(2*(2**n), 60) = 2, 4, 8, 16
    expected = [(0, 2.0), (0, 4.0), (0, 8.0), (0, 16.0)]
    assert recorded_uniform_calls == expected


def test_max_delay_caps_computed_delay() -> None:
    """Delay should never exceed max_delay."""
    captured: list[float] = []

    def capture_uniform(lo: float, hi: float) -> float:
        """Capture upper bound and return 0."""
        captured.append(hi)
        return 0.0

    side_effects = [RuntimeError()] * 5 + ["ok"]
    mock_func = MagicMock(side_effect=side_effects)
    mock_func.__name__ = "f"
    mock_func.__doc__ = None
    mock_func.__wrapped__ = None

    with patch("retry_with_backoff.time.sleep"), patch(
        "retry_with_backoff.random.uniform", side_effect=capture_uniform
    ):
        decorated = retry_with_backoff(
            max_retries=5, base_delay=10.0, max_delay=15.0
        )(mock_func)
        decorated()

    assert all(d <= 15.0 for d in captured)


# ---------------------------------------------------------------------------
# Exception handling
# ---------------------------------------------------------------------------


def test_reraises_after_max_retries_exhausted() -> None:
    """After max_retries+1 failed calls, the last exception must be re-raised."""
    with patch("retry_with_backoff.time.sleep"):

        @retry_with_backoff(max_retries=2, base_delay=0.0)
        def always_fails() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            always_fails()


def test_total_call_count_equals_max_retries_plus_one() -> None:
    """Function should be called exactly max_retries + 1 times before giving up."""
    mock_func = MagicMock(side_effect=RuntimeError("err"))
    mock_func.__name__ = "f"
    mock_func.__doc__ = None
    mock_func.__wrapped__ = None

    with patch("retry_with_backoff.time.sleep"):
        decorated = retry_with_backoff(max_retries=4, base_delay=0.0)(mock_func)
        with pytest.raises(RuntimeError):
            decorated()

    assert mock_func.call_count == 5


def test_non_matching_exception_propagates_immediately() -> None:
    """Exceptions not listed in ``exceptions`` must propagate without retry."""
    call_count = 0

    with patch("retry_with_backoff.time.sleep"):

        @retry_with_backoff(max_retries=5, base_delay=0.0, exceptions=(TypeError,))
        def raises_value_error() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("not retried")

        with pytest.raises(ValueError):
            raises_value_error()

    assert call_count == 1


def test_matching_exception_type_triggers_retry() -> None:
    """Only the specified exception types should trigger retries."""
    attempts: list[int] = []

    with patch("retry_with_backoff.time.sleep"):

        @retry_with_backoff(
            max_retries=3, base_delay=0.0, exceptions=(ConnectionError,)
        )
        def intermittent() -> str:
            attempts.append(1)
            if len(attempts) < 3:
                raise ConnectionError("retry me")
            return "done"

        result = intermittent()

    assert result == "done"
    assert len(attempts) == 3


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_max_retries_zero_calls_function_once_on_failure() -> None:
    """With max_retries=0, a failing function raises without any sleep."""
    with patch("retry_with_backoff.time.sleep") as mock_sleep:

        @retry_with_backoff(max_retries=0, base_delay=1.0)
        def fail() -> None:
            raise RuntimeError("no retry")

        with pytest.raises(RuntimeError):
            fail()

    mock_sleep.assert_not_called()


def test_max_retries_zero_calls_function_once_on_success() -> None:
    """With max_retries=0, a succeeding function returns normally."""

    @retry_with_backoff(max_retries=0)
    def ok() -> int:
        return 7

    assert ok() == 7


def test_negative_max_retries_raises_value_error() -> None:
    """Negative max_retries must raise ValueError at decoration time."""
    with pytest.raises(ValueError, match="max_retries must be >= 0"):

        @retry_with_backoff(max_retries=-1)
        def fn() -> None:
            pass


def test_base_delay_zero_all_sleeps_are_zero() -> None:
    """With base_delay=0, all jittered delays are 0."""
    sleep_durations: list[float] = []

    with patch("retry_with_backoff.time.sleep", side_effect=sleep_durations.append):

        @retry_with_backoff(max_retries=3, base_delay=0.0)
        def always_fails() -> None:
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            always_fails()

    assert all(d == 0.0 for d in sleep_durations)


def test_max_delay_less_than_base_delay_caps_from_first_retry() -> None:
    """When max_delay < base_delay, the first retry delay is capped at max_delay."""
    captured: list[float] = []

    def capture_uniform(lo: float, hi: float) -> float:
        """Capture upper bound."""
        captured.append(hi)
        return 0.0

    with patch("retry_with_backoff.time.sleep"), patch(
        "retry_with_backoff.random.uniform", side_effect=capture_uniform
    ):

        @retry_with_backoff(max_retries=3, base_delay=10.0, max_delay=3.0)
        def always_fails() -> None:
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            always_fails()

    assert all(d <= 3.0 for d in captured)


# ---------------------------------------------------------------------------
# Metadata preservation
# ---------------------------------------------------------------------------


def test_functools_wraps_preserves_name_and_doc() -> None:
    """Decorated function must preserve __name__ and __doc__."""

    @retry_with_backoff(max_retries=2)
    def fetch_data(url: str) -> dict:
        """Fetch data from a remote API."""
        return {}

    assert fetch_data.__name__ == "fetch_data"
    assert fetch_data.__doc__ == "Fetch data from a remote API."


def test_functools_wraps_preserves_wrapped_attribute() -> None:
    """__wrapped__ should point to the original function."""

    def original() -> None:
        """Original docstring."""

    decorated = retry_with_backoff(max_retries=1)(original)
    assert decorated.__wrapped__ is original  # type: ignore[attr-defined]
