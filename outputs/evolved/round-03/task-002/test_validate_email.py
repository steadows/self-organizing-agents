"""Tests for the validate_email utility function."""

import pytest

from validate_email import validate_email


# ---------------------------------------------------------------------------
# Valid emails — happy path
# ---------------------------------------------------------------------------

def test_simple_valid_email():
    assert validate_email("user@example.com") is True


def test_subdomain_valid_email():
    assert validate_email("first.last@sub.domain.co.uk") is True


def test_plus_tag_valid_email():
    assert validate_email("user+tag@gmail.com") is True


def test_minimal_valid_email():
    assert validate_email("a@b.co") is True


def test_special_chars_valid_email():
    assert validate_email("test_user%special@my-domain.org") is True


def test_numeric_local_and_domain():
    assert validate_email("123@456.com") is True


# ---------------------------------------------------------------------------
# Invalid emails — spec edge cases
# ---------------------------------------------------------------------------

def test_empty_string_returns_false():
    assert validate_email("") is False


def test_no_at_sign_returns_false():
    assert validate_email("plainaddress") is False


def test_no_local_part_returns_false():
    assert validate_email("@no-local.com") is False


def test_leading_dot_in_local_returns_false():
    assert validate_email(".leading@example.com") is False


def test_trailing_dot_in_local_returns_false():
    assert validate_email("trailing.@example.com") is False


def test_consecutive_dots_in_local_returns_false():
    assert validate_email("double..dot@example.com") is False


def test_domain_leading_dot_returns_false():
    assert validate_email("user@.leading-dot.com") is False


def test_domain_no_dot_returns_false():
    assert validate_email("user@localhost") is False


def test_tld_single_char_returns_false():
    assert validate_email("user@domain.c") is False


def test_multiple_at_signs_returns_false():
    assert validate_email("user@@double.com") is False


def test_hyphen_start_label_returns_false():
    assert validate_email("user@-hyphen-start.com") is False


# ---------------------------------------------------------------------------
# Length boundary edge cases
# ---------------------------------------------------------------------------

def test_email_exactly_254_chars_returns_true():
    # Construct a valid email of exactly 254 characters.
    # domain = "b.co" (4 chars), @ = 1 char → local must be 249 chars.
    local = "a" * 249
    email = f"{local}@b.co"
    assert len(email) == 254
    assert validate_email(email) is True


def test_email_exceeding_254_chars_returns_false():
    local = "a" * 250
    email = f"{local}@b.co"
    assert len(email) == 255
    assert validate_email(email) is False


# ---------------------------------------------------------------------------
# Additional structural edge cases
# ---------------------------------------------------------------------------

def test_tld_numeric_only_returns_false():
    assert validate_email("user@example.123") is False


def test_domain_label_ends_with_hyphen_returns_false():
    assert validate_email("user@domain-.com") is False


def test_domain_empty_label_between_dots_returns_false():
    assert validate_email("user@domain..com") is False
