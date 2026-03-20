"""Frozen acceptance tests for parse_duration().

Holdout task 001: Parse a human-readable duration string (e.g. "2h30m10s")
into total seconds as an integer.

Spec:
    parse_duration(text: str) -> int
"""

import sys
import os

# Allow importing from the output directory passed via environment variable
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

import pytest

from parse_duration import parse_duration


# --- Happy path ---


def test_full_hms() -> None:
    """Mixed hours, minutes, seconds parses correctly."""
    assert parse_duration("2h30m10s") == 9010


def test_hours_only() -> None:
    """Hours-only string returns seconds."""
    assert parse_duration("1h") == 3600


def test_minutes_only() -> None:
    """Minutes-only string returns seconds."""
    assert parse_duration("45m") == 2700


def test_seconds_only() -> None:
    """Seconds-only string returns seconds."""
    assert parse_duration("90s") == 90


# --- Zero values ---


def test_zero_seconds() -> None:
    """Zero seconds is valid."""
    assert parse_duration("0s") == 0


def test_all_zero() -> None:
    """All-zero components sum to zero."""
    assert parse_duration("0h0m0s") == 0


# --- Case insensitivity ---


def test_uppercase_units() -> None:
    """Unit letters are case-insensitive."""
    assert parse_duration("1H30M") == 5400


def test_mixed_case() -> None:
    """Mixed case in units works."""
    assert parse_duration("2H30m10S") == 9010


# --- Arbitrary order ---


def test_reversed_order() -> None:
    """Seconds before hours still works."""
    assert parse_duration("10s2h") == 7210


def test_minutes_then_hours() -> None:
    """Minutes before hours still works."""
    assert parse_duration("30m1h") == 5400


# --- Large values (no normalization) ---


def test_large_minutes() -> None:
    """100 minutes is kept as-is, no normalization to hours."""
    assert parse_duration("100m") == 6000


def test_large_seconds() -> None:
    """Large second values are not normalized."""
    assert parse_duration("3661s") == 3661


# --- Return type ---


def test_return_type_is_int() -> None:
    """Return value must be an int, not a float."""
    result = parse_duration("1h")
    assert isinstance(result, int)


# --- ValueError: empty string ---


def test_empty_string_raises() -> None:
    """Empty input is invalid."""
    with pytest.raises(ValueError):
        parse_duration("")


# --- ValueError: duplicate unit ---


def test_duplicate_unit_raises() -> None:
    """Repeating the same unit letter is invalid."""
    with pytest.raises(ValueError):
        parse_duration("2h2h")


def test_duplicate_minutes_raises() -> None:
    """Repeating minute unit is invalid."""
    with pytest.raises(ValueError):
        parse_duration("10m20m")


# --- ValueError: negative value ---


def test_negative_value_raises() -> None:
    """Negative numbers are invalid."""
    with pytest.raises(ValueError):
        parse_duration("-5m")


# --- ValueError: no valid pairs ---


def test_no_valid_pairs_raises() -> None:
    """Alphabetic-only string with no digit+unit pairs is invalid."""
    with pytest.raises(ValueError):
        parse_duration("abc")


# --- ValueError: decimal values ---


def test_decimal_raises() -> None:
    """Decimal/float values are not supported."""
    with pytest.raises(ValueError):
        parse_duration("2.5h")


# --- ValueError: spaces ---


def test_spaces_raises() -> None:
    """Spaces between components are not allowed."""
    with pytest.raises(ValueError):
        parse_duration("2h 30m")


# --- ValueError: unsupported unit ---


def test_unsupported_unit_raises() -> None:
    """Units beyond h/m/s (e.g. days) are not supported."""
    with pytest.raises(ValueError):
        parse_duration("2d")
