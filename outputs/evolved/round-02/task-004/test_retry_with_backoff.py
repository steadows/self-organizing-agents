"""Tests for retry_with_backoff decorator."""

from unittest.mock import MagicMock, call, patch

import pytest

from retry_with_backoff import retry_with_backoff


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_succeeds_on_first_call_no_retries():
    """Function that succeeds immediately is called exactly once."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.0)
    def succeed():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = succeed()
    assert result == "ok"
    assert call_count == 1


def test_returns_correct_value():
    """Return value from the wrapped function is preserved."""

    @retry_with_backoff(max_retries=2, base_delay=0.0)
    def add(a: int, b: int) -> int:
        return a + b

    assert add(3, 4) == 7


def test_succeeds_on_retry():
    """Function that fails then succeeds returns the successful result."""
    attempts = []

    @retry_with_backoff(max_retries=3, base_delay=0.0)
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ValueError("not yet")
        return "done"

    with patch("time.sleep"):
        result = flaky()

    assert result == "done"
    assert len(attempts) == 3


def test_retries_exact_max_retries_times():
    """Function is called max_retries + 1 times total before giving up."""
    call_count = 0

    @retry_with_backoff(max_retries=4, base_delay=0.0)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("fail")

    with patch("time.sleep"):
        with pytest.raises(RuntimeError):
            always_fails()

    assert call_count == 5  # 1 initial + 4 retries


def test_last_exception_is_reraised():
    """The exception raised on the final attempt is the one propagated."""
    counter = [0]

    @retry_with_backoff(max_retries=2, base_delay=0.0)
    def raises_sequenced():
        counter[0] += 1
        raise ValueError(f"attempt {counter[0]}")

    with patch("time.sleep"):
        with pytest.raises(ValueError, match="attempt 3"):
            raises_sequenced()


# ---------------------------------------------------------------------------
# Edge cases — max_retries boundaries
# ---------------------------------------------------------------------------


def test_max_retries_zero_success():
    """With max_retries=0, a succeeding function is called once and returns."""

    @retry_with_backoff(max_retries=0)
    def succeed():
        return 42

    assert succeed() == 42


def test_max_retries_zero_failure():
    """With max_retries=0, a failing function raises immediately."""

    @retry_with_backoff(max_retries=0)
    def fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        fail()


def test_max_retries_negative_raises_at_decoration_time():
    """Negative max_retries raises ValueError when the decorator is applied."""
    with pytest.raises(ValueError, match="max_retries must be >= 0"):

        @retry_with_backoff(max_retries=-1)
        def func():
            pass


# ---------------------------------------------------------------------------
# Exception filtering
# ---------------------------------------------------------------------------


def test_non_matching_exception_propagates_immediately():
    """An exception not in ``exceptions`` propagates without retry."""
    call_count = 0

    @retry_with_backoff(max_retries=5, base_delay=0.0, exceptions=(ConnectionError,))
    def raises_value_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("wrong type")

    with pytest.raises(ValueError):
        raises_value_error()

    assert call_count == 1


def test_matching_exception_triggers_retry():
    """An exception that matches ``exceptions`` triggers the retry logic."""
    call_count = 0

    @retry_with_backoff(
        max_retries=2, base_delay=0.0, exceptions=(ConnectionError, TimeoutError)
    )
    def raises_connection_error():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("refused")

    with patch("time.sleep"):
        with pytest.raises(ConnectionError):
            raises_connection_error()

    assert call_count == 3


def test_only_listed_exceptions_are_caught():
    """If the first exception matches but a later one does not, the later one propagates."""
    call_count = 0

    @retry_with_backoff(max_retries=5, base_delay=0.0, exceptions=(ConnectionError,))
    def mixed():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("first")
        raise TypeError("second — not in exceptions")

    with patch("time.sleep"):
        with pytest.raises(TypeError):
            mixed()

    assert call_count == 2


# ---------------------------------------------------------------------------
# Delay / backoff mechanics
# ---------------------------------------------------------------------------


def test_sleep_is_called_between_retries():
    """time.sleep is called exactly max_retries times (once before each retry)."""

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep") as mock_sleep, patch("random.uniform", return_value=0.5):
        with pytest.raises(RuntimeError):
            always_fails()

    assert mock_sleep.call_count == 3


def test_sleep_not_called_on_first_attempt_success():
    """time.sleep is never called when the function succeeds on the first try."""

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def succeed():
        return "good"

    with patch("time.sleep") as mock_sleep:
        succeed()

    mock_sleep.assert_not_called()


def test_exponential_backoff_delay_values():
    """Delay passed to random.uniform grows exponentially, capped at max_delay."""
    captured_upper_bounds = []

    def fake_uniform(low, high):
        captured_upper_bounds.append(high)
        return 0.0

    @retry_with_backoff(max_retries=4, base_delay=1.0, max_delay=5.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep"), patch("random.uniform", side_effect=fake_uniform):
        with pytest.raises(RuntimeError):
            always_fails()

    # attempt 0 → delay=min(1*1,5)=1; attempt 1 → min(1*2,5)=2;
    # attempt 2 → min(1*4,5)=4; attempt 3 → min(1*8,5)=5
    assert captured_upper_bounds == [1.0, 2.0, 4.0, 5.0]


def test_base_delay_zero_sleeps_zero():
    """When base_delay=0, random.uniform is called with (0, 0) so sleep is 0."""
    upper_bounds = []

    def fake_uniform(low, high):
        upper_bounds.append(high)
        return 0.0

    @retry_with_backoff(max_retries=2, base_delay=0.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep"), patch("random.uniform", side_effect=fake_uniform):
        with pytest.raises(RuntimeError):
            always_fails()

    assert all(b == 0.0 for b in upper_bounds)


def test_max_delay_less_than_base_delay_caps_immediately():
    """When max_delay < base_delay, the delay is capped at max_delay from attempt 0."""
    upper_bounds = []

    def fake_uniform(low, high):
        upper_bounds.append(high)
        return 0.0

    @retry_with_backoff(max_retries=3, base_delay=10.0, max_delay=2.0)
    def always_fails():
        raise RuntimeError("fail")

    with patch("time.sleep"), patch("random.uniform", side_effect=fake_uniform):
        with pytest.raises(RuntimeError):
            always_fails()

    assert all(b == 2.0 for b in upper_bounds)


# ---------------------------------------------------------------------------
# functools.wraps — metadata preservation
# ---------------------------------------------------------------------------


def test_wraps_preserves_name():
    """Decorated function retains its original __name__."""

    @retry_with_backoff(max_retries=1)
    def fetch_data(url: str) -> dict:
        """Fetch data from a remote API."""
        ...

    assert fetch_data.__name__ == "fetch_data"


def test_wraps_preserves_docstring():
    """Decorated function retains its original __doc__."""

    @retry_with_backoff(max_retries=1)
    def fetch_data(url: str) -> dict:
        """Fetch data from a remote API."""
        ...

    assert fetch_data.__doc__ == "Fetch data from a remote API."


# ---------------------------------------------------------------------------
# Failure simulation (I/O / external dependency)
# ---------------------------------------------------------------------------


def test_simulated_os_error_triggers_retry():
    """OSError (a common I/O failure) is retried when included in exceptions."""
    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0.0, exceptions=(OSError,))
    def read_file(path: str) -> str:
        nonlocal call_count
        call_count += 1
        raise OSError(f"cannot open {path}")

    with patch("time.sleep"):
        with pytest.raises(OSError):
            read_file("/tmp/missing.txt")

    assert call_count == 3


def test_simulated_network_failure_succeeds_after_retry():
    """Simulated network failures recover when the dependency eventually succeeds."""
    responses = [ConnectionError("timeout"), ConnectionError("timeout"), "data"]

    mock_client = MagicMock(side_effect=responses)

    @retry_with_backoff(max_retries=3, base_delay=0.0, exceptions=(ConnectionError,))
    def fetch(client):
        return client()

    with patch("time.sleep"):
        result = fetch(mock_client)

    assert result == "data"
    assert mock_client.call_count == 3
