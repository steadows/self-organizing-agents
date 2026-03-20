"""Tests for the parse_duration utility function."""

import pytest

from parse_duration import parse_duration


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_full_hms():
    assert parse_duration("2h30m10s") == 9010


def test_hours_only():
    assert parse_duration("1h") == 3600


def test_minutes_only():
    assert parse_duration("45m") == 2700


def test_seconds_only():
    assert parse_duration("90s") == 90


def test_zero_seconds():
    assert parse_duration("0s") == 0


def test_all_zeros():
    assert parse_duration("0h0m0s") == 0


def test_case_insensitive_upper():
    assert parse_duration("1H30M") == 5400


def test_case_insensitive_mixed():
    assert parse_duration("2H30m10S") == 9010


def test_reversed_order():
    assert parse_duration("10s2h") == 7210


def test_large_minutes():
    assert parse_duration("100m") == 6000


def test_large_seconds_no_normalisation():
    assert parse_duration("3600s") == 3600


def test_minutes_and_seconds():
    assert parse_duration("5m30s") == 330


# ---------------------------------------------------------------------------
# Edge-case / boundary tests
# ---------------------------------------------------------------------------

def test_zero_value_each_unit():
    assert parse_duration("0h") == 0
    assert parse_duration("0m") == 0
    assert parse_duration("0s") == 0


def test_single_large_hour_value():
    assert parse_duration("100h") == 360000


# ---------------------------------------------------------------------------
# Error / failure-path tests
# ---------------------------------------------------------------------------

def test_empty_string_raises():
    with pytest.raises(ValueError):
        parse_duration("")


def test_duplicate_unit_raises():
    with pytest.raises(ValueError):
        parse_duration("2h2h")


def test_duplicate_unit_mixed_case_raises():
    with pytest.raises(ValueError):
        parse_duration("1H1h")


def test_negative_value_raises():
    with pytest.raises(ValueError):
        parse_duration("-5m")


def test_decimal_value_raises():
    with pytest.raises(ValueError):
        parse_duration("2.5h")


def test_unsupported_unit_raises():
    with pytest.raises(ValueError):
        parse_duration("2d")


def test_no_valid_pairs_raises():
    with pytest.raises(ValueError):
        parse_duration("hello")


def test_space_in_string_raises():
    with pytest.raises(ValueError):
        parse_duration("2h 30m")


def test_non_numeric_before_unit_raises():
    with pytest.raises(ValueError):
        parse_duration("abch")


def test_iso_8601_format_raises():
    with pytest.raises(ValueError):
        parse_duration("PT2H30M")


def test_digits_only_raises():
    with pytest.raises(ValueError):
        parse_duration("123")
