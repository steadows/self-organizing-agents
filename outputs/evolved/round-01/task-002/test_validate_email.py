"""Tests for the validate_email utility function."""

import pytest

from validate_email import validate_email


# ---------------------------------------------------------------------------
# Valid email addresses
# ---------------------------------------------------------------------------

def test_simple_valid_email():
    assert validate_email("user@example.com") is True


def test_subdomain_and_country_tld():
    assert validate_email("first.last@sub.domain.co.uk") is True


def test_plus_tag_in_local():
    assert validate_email("user+tag@gmail.com") is True


def test_minimal_valid_email():
    assert validate_email("a@b.co") is True


def test_special_chars_in_local():
    assert validate_email("test_user%special@my-domain.org") is True


def test_numeric_local_and_domain():
    assert validate_email("123@456.com") is True


def test_hyphen_in_domain_label():
    assert validate_email("user@my-domain.net") is True


def test_long_valid_email_254_chars():
    # Construct an email that is exactly 254 characters
    # local(63) + @ + domain_label(63) + . + tld(2) = 63 + 1 + 63 + 1 + 2 = 130 — pad local further
    local = "a" * 63
    domain_label = "b" * 63
    tld = "co"
    # Build up to 254: local + @ + domain_label + . + tld
    base = f"{local}@{domain_label}.{tld}"
    # Pad local to hit exactly 254
    needed = 254 - len(base)
    padded_local = "a" * (63 + needed)
    email = f"{padded_local}@{domain_label}.{tld}"
    assert len(email) == 254
    assert validate_email(email) is True


# ---------------------------------------------------------------------------
# Invalid email addresses — structural
# ---------------------------------------------------------------------------

def test_empty_string_returns_false():
    assert validate_email("") is False


def test_no_at_sign_returns_false():
    assert validate_email("plainaddress") is False


def test_empty_local_part_returns_false():
    assert validate_email("@no-local.com") is False


def test_multiple_at_signs_returns_false():
    assert validate_email("user@@double.com") is False


def test_domain_with_no_dot_returns_false():
    assert validate_email("user@localhost") is False


# ---------------------------------------------------------------------------
# Invalid email addresses — local part rules
# ---------------------------------------------------------------------------

def test_local_leading_dot_returns_false():
    assert validate_email(".leading@example.com") is False


def test_local_trailing_dot_returns_false():
    assert validate_email("trailing.@example.com") is False


def test_local_consecutive_dots_returns_false():
    assert validate_email("double..dot@example.com") is False


def test_local_invalid_char_returns_false():
    assert validate_email("user name@example.com") is False


def test_local_bracket_invalid_returns_false():
    assert validate_email("user[tag]@example.com") is False


# ---------------------------------------------------------------------------
# Invalid email addresses — domain part rules
# ---------------------------------------------------------------------------

def test_domain_leading_dot_returns_false():
    assert validate_email("user@.leading-dot.com") is False


def test_domain_trailing_dot_returns_false():
    assert validate_email("user@example.com.") is False


def test_domain_label_leading_hyphen_returns_false():
    assert validate_email("user@-hyphen-start.com") is False


def test_domain_label_trailing_hyphen_returns_false():
    assert validate_email("user@hyphen-end-.com") is False


def test_tld_single_char_returns_false():
    assert validate_email("user@domain.c") is False


def test_tld_numeric_returns_false():
    assert validate_email("user@domain.12") is False


def test_domain_consecutive_dots_returns_false():
    assert validate_email("user@domain..com") is False


# ---------------------------------------------------------------------------
# Edge cases — length
# ---------------------------------------------------------------------------

def test_email_exceeding_254_chars_returns_false():
    local = "a" * 200
    domain = "b" * 60
    email = f"{local}@{domain}.com"
    assert len(email) > 254
    assert validate_email(email) is False
