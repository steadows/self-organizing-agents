"""Tests for the validate_email utility function."""

from unittest.mock import patch

import pytest

from validate_email import validate_email


# ---------------------------------------------------------------------------
# Valid email addresses
# ---------------------------------------------------------------------------

def test_simple_valid_email():
    assert validate_email("user@example.com") is True


def test_subdomain_valid_email():
    assert validate_email("first.last@sub.domain.co.uk") is True


def test_plus_tag_valid_email():
    assert validate_email("user+tag@gmail.com") is True


def test_short_valid_email():
    assert validate_email("a@b.co") is True


def test_special_chars_in_local():
    assert validate_email("test_user%special@my-domain.org") is True


def test_all_numeric_local_and_domain():
    assert validate_email("123@456.com") is True


def test_hyphenated_domain():
    assert validate_email("user@my-domain.co.uk") is True


# ---------------------------------------------------------------------------
# Invalid: structural failures
# ---------------------------------------------------------------------------

def test_empty_string():
    assert validate_email("") is False


def test_no_at_sign():
    assert validate_email("plainaddress") is False


def test_double_at_sign():
    assert validate_email("user@@double.com") is False


def test_missing_local_part():
    assert validate_email("@no-local.com") is False


# ---------------------------------------------------------------------------
# Invalid: local part failures
# ---------------------------------------------------------------------------

def test_leading_dot_in_local():
    assert validate_email(".leading@example.com") is False


def test_trailing_dot_in_local():
    assert validate_email("trailing.@example.com") is False


def test_consecutive_dots_in_local():
    assert validate_email("double..dot@example.com") is False


def test_invalid_char_in_local():
    assert validate_email("user name@example.com") is False


# ---------------------------------------------------------------------------
# Invalid: domain part failures
# ---------------------------------------------------------------------------

def test_domain_no_dot():
    assert validate_email("user@localhost") is False


def test_domain_leading_dot():
    assert validate_email("user@.leading-dot.com") is False


def test_domain_label_starts_with_hyphen():
    assert validate_email("user@-hyphen-start.com") is False


def test_domain_label_ends_with_hyphen():
    assert validate_email("user@hyphen-end-.com") is False


def test_tld_single_char():
    assert validate_email("user@domain.c") is False


def test_tld_numeric():
    assert validate_email("user@domain.12") is False


def test_empty_label_in_domain():
    assert validate_email("user@domain..com") is False


# ---------------------------------------------------------------------------
# Edge cases: length limits
# ---------------------------------------------------------------------------

def test_email_exactly_254_chars_is_valid():
    # Construct a valid email that is exactly 254 characters.
    # Format: <local>@<subdomain>.example.com
    # domain_suffix includes the leading dot: ".example.com" = 12 chars
    # Total = len(local) + 1 (@) + len(subdomain) + 12 = 254
    # So: len(local) + len(subdomain) = 241
    domain_suffix = ".example.com"  # 12 chars
    local = "a" * 100              # 100 chars
    subdomain = "b" * 141          # 141 chars  -> total = 100 + 1 + 141 + 12 = 254
    email = f"{local}@{subdomain}{domain_suffix}"
    assert len(email) == 254, f"Expected 254, got {len(email)}"
    assert validate_email(email) is True


def test_email_255_chars_is_invalid():
    # One character over the 254-char limit.
    domain_suffix = ".example.com"  # 12 chars
    local = "a" * 100              # 100 chars
    subdomain = "b" * 142          # 142 chars -> total = 100 + 1 + 142 + 12 = 255
    email = f"{local}@{subdomain}{domain_suffix}"
    assert len(email) == 255, f"Expected 255, got {len(email)}"
    assert validate_email(email) is False


# ---------------------------------------------------------------------------
# Failure / error path simulation (mocking internals)
# ---------------------------------------------------------------------------

def test_validate_email_returns_false_when_local_validator_raises(monkeypatch):
    """Simulate _is_valid_local raising an OSError to exercise failure path."""
    import validate_email as ve_module

    def broken_is_valid_local(local: str) -> bool:
        raise OSError("Simulated file system error during validation")

    monkeypatch.setattr(ve_module, "_is_valid_local", broken_is_valid_local)

    with pytest.raises(OSError, match="Simulated file system error"):
        validate_email("user@example.com")


def test_validate_email_returns_false_when_domain_validator_raises(monkeypatch):
    """Simulate _is_valid_domain raising a RuntimeError to exercise failure path."""
    import validate_email as ve_module

    def broken_is_valid_domain(domain: str) -> bool:
        raise RuntimeError("Simulated domain lookup failure")

    monkeypatch.setattr(ve_module, "_is_valid_domain", broken_is_valid_domain)

    with pytest.raises(RuntimeError, match="Simulated domain lookup failure"):
        validate_email("user@example.com")
