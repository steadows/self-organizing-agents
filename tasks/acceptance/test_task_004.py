"""Acceptance tests for task-004: retry_with_backoff()

Tests the contract:
  @retry_with_backoff(max_retries=3, base_delay=0.5, exceptions=(Exception,))
  def some_function(...): ...

Decorator factory that retries a function on failure with exponential backoff.
Uses functools.wraps to preserve decorated function metadata.

These tests are FROZEN ground truth. Implementations must pass all of them.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Allow importing from the output directory passed via environment variable
# or default to the current directory
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

from retry_with_backoff import retry_with_backoff


# ── Succeeds first try ─────────────────────────────────────────────────────

@patch("time.sleep")
def test_retry_succeeds_first_try(mock_sleep: MagicMock) -> None:
    """If the function succeeds on the first call, no retries or delays."""

    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def succeed() -> str:
        return "ok"

    result = succeed()
    assert result == "ok"
    mock_sleep.assert_not_called()


# ── Succeeds on retry ─────────────────────────────────────────────────────

@patch("time.sleep")
def test_retry_succeeds_on_second_attempt(mock_sleep: MagicMock) -> None:
    """Fails once, then succeeds — returns the successful result."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("transient")
        return "recovered"

    result = flaky()
    assert result == "recovered"
    assert call_count == 2
    assert mock_sleep.call_count == 1


@patch("time.sleep")
def test_retry_succeeds_on_last_attempt(mock_sleep: MagicMock) -> None:
    """Fails max_retries times, succeeds on the final allowed attempt."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count <= 3:
            raise RuntimeError("not yet")
        return "finally"

    result = flaky()
    assert result == "finally"
    assert call_count == 4  # 1 initial + 3 retries


# ── Exhausts retries ──────────────────────────────────────────────────────

@patch("time.sleep")
def test_retry_exhausted_raises_last_exception(mock_sleep: MagicMock) -> None:
    """After all retries exhausted, the last exception propagates."""
    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0.1)
    def always_fails() -> None:
        nonlocal call_count
        call_count += 1
        raise ValueError(f"attempt {call_count}")

    with pytest.raises(ValueError, match="attempt 3"):
        always_fails()

    assert call_count == 3  # 1 initial + 2 retries


# ── Preserves metadata ────────────────────────────────────────────────────

def test_retry_preserves_name() -> None:
    """Decorated function preserves __name__."""

    @retry_with_backoff(max_retries=1, base_delay=0.0)
    def my_special_function() -> None:
        """My docstring."""

    assert my_special_function.__name__ == "my_special_function"


def test_retry_preserves_docstring() -> None:
    """Decorated function preserves __doc__."""

    @retry_with_backoff(max_retries=1, base_delay=0.0)
    def documented() -> None:
        """This is the docstring."""

    assert documented.__doc__ == "This is the docstring."


# ── Exception filtering ───────────────────────────────────────────────────

@patch("time.sleep")
def test_retry_only_catches_specified_exceptions(mock_sleep: MagicMock) -> None:
    """Unspecified exceptions propagate immediately without retry."""
    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.1, exceptions=(ValueError,))
    def raises_type_error() -> None:
        nonlocal call_count
        call_count += 1
        raise TypeError("wrong type")

    with pytest.raises(TypeError):
        raises_type_error()

    assert call_count == 1  # No retries for TypeError
    mock_sleep.assert_not_called()


@patch("time.sleep")
def test_retry_catches_specified_exception_subclass(mock_sleep: MagicMock) -> None:
    """Subclasses of specified exceptions are also caught."""
    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0.1, exceptions=(OSError,))
    def raises_file_not_found() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise FileNotFoundError("gone")
        return "found"

    result = raises_file_not_found()
    assert result == "found"
    assert call_count == 3


# ── max_retries=0 ─────────────────────────────────────────────────────────

@patch("time.sleep")
def test_retry_max_retries_zero_no_retry(mock_sleep: MagicMock) -> None:
    """max_retries=0 means the function is called once with no retry."""
    call_count = 0

    @retry_with_backoff(max_retries=0, base_delay=0.1)
    def fails_once() -> None:
        nonlocal call_count
        call_count += 1
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        fails_once()

    assert call_count == 1
    mock_sleep.assert_not_called()


@patch("time.sleep")
def test_retry_max_retries_zero_succeeds(mock_sleep: MagicMock) -> None:
    """max_retries=0 still allows the function to succeed."""

    @retry_with_backoff(max_retries=0, base_delay=0.1)
    def succeeds() -> str:
        return "ok"

    assert succeeds() == "ok"


# ── max_retries < 0 ───────────────────────────────────────────────────────

def test_retry_negative_max_retries_raises_value_error() -> None:
    """Negative max_retries raises ValueError at decoration time."""
    with pytest.raises(ValueError):

        @retry_with_backoff(max_retries=-1, base_delay=0.1)
        def nope() -> None:
            pass


# ── base_delay=0 ──────────────────────────────────────────────────────────

@patch("time.sleep")
def test_retry_base_delay_zero(mock_sleep: MagicMock) -> None:
    """base_delay=0 means retries happen without delay (sleep(0) or no sleep)."""
    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0)
    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise RuntimeError("oops")
        return "ok"

    result = flaky()
    assert result == "ok"
    # Either sleep is not called or called with 0
    for call in mock_sleep.call_args_list:
        assert call[0][0] == 0 or call[0][0] == 0.0


# ── Return value passthrough ──────────────────────────────────────────────

@patch("time.sleep")
def test_retry_returns_none(mock_sleep: MagicMock) -> None:
    """A function returning None has that None returned."""

    @retry_with_backoff(max_retries=1, base_delay=0.0)
    def returns_none() -> None:
        return None

    assert returns_none() is None


@patch("time.sleep")
def test_retry_returns_complex_value(mock_sleep: MagicMock) -> None:
    """Complex return values pass through unmodified."""

    @retry_with_backoff(max_retries=1, base_delay=0.0)
    def returns_dict() -> dict:
        return {"key": [1, 2, 3]}

    assert returns_dict() == {"key": [1, 2, 3]}


# ── Arguments passthrough ─────────────────────────────────────────────────

@patch("time.sleep")
def test_retry_passes_args_and_kwargs(mock_sleep: MagicMock) -> None:
    """Positional and keyword arguments are forwarded correctly."""

    @retry_with_backoff(max_retries=1, base_delay=0.0)
    def add(a: int, b: int, extra: int = 0) -> int:
        return a + b + extra

    assert add(1, 2, extra=10) == 13
