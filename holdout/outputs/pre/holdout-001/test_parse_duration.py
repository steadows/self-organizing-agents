"""Tests for parse_duration."""

import pytest

from parse_duration import parse_duration


# --- Happy path ---

def test_full_hms() -> None:
    assert parse_duration("2h30m10s") == 9010


def test_hours_only() -> None:
    assert parse_duration("1h") == 3600


def test_minutes_only() -> None:
    assert parse_duration("45m") == 2700


def test_seconds_only() -> None:
    assert parse_duration("90s") == 90


def test_zero_seconds() -> None:
    assert parse_duration("0s") == 0


def test_case_insensitive() -> None:
    assert parse_duration("1H30M") == 5400


def test_units_out_of_order() -> None:
    assert parse_duration("10s2h") == 7210


def test_all_zeros() -> None:
    assert parse_duration("0h0m0s") == 0


def test_large_minute_value() -> None:
    assert parse_duration("100m") == 6000


# --- Error cases ---

def test_empty_string() -> None:
    with pytest.raises(ValueError):
        parse_duration("")


def test_duplicate_unit() -> None:
    with pytest.raises(ValueError):
        parse_duration("2h2h")


def test_negative_value() -> None:
    with pytest.raises(ValueError):
        parse_duration("-5m")


def test_non_numeric_text() -> None:
    with pytest.raises(ValueError):
        parse_duration("abc")


def test_decimal_value() -> None:
    with pytest.raises(ValueError):
        parse_duration("2.5h")


def test_spaces_not_allowed() -> None:
    with pytest.raises(ValueError):
        parse_duration("2h 30m")


def test_unsupported_unit() -> None:
    with pytest.raises(ValueError):
        parse_duration("2d")


def test_hello_garbage() -> None:
    with pytest.raises(ValueError):
        parse_duration("hello")


# --- Additional edge cases ---

def test_bare_digits_no_unit() -> None:
    with pytest.raises(ValueError):
        parse_duration("123")


def test_unit_only_no_value() -> None:
    with pytest.raises(ValueError):
        parse_duration("h")


def test_mixed_case_full() -> None:
    assert parse_duration("1h30M10S") == 5410
