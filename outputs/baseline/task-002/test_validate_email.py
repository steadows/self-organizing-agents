"""Tests for validate_email utility."""

import pytest

from validate_email import validate_email


# --- Valid emails ---

@pytest.mark.parametrize("email", [
    "user@example.com",
    "first.last@sub.domain.co.uk",
    "user+tag@gmail.com",
    "a@b.co",
    "test_user%special@my-domain.org",
    "123@456.com",
])
def test_valid_emails(email: str) -> None:
    """Spec-listed valid emails should return True."""
    assert validate_email(email) is True


# --- Invalid emails ---

@pytest.mark.parametrize("email", [
    "",
    "plainaddress",
    "@no-local.com",
    "user@.leading-dot.com",
    ".leading@example.com",
    "trailing.@example.com",
    "double..dot@example.com",
    "user@-hyphen-start.com",
    "user@domain.c",
    "user@@double.com",
])
def test_invalid_emails(email: str) -> None:
    """Spec-listed invalid emails should return False."""
    assert validate_email(email) is False


# --- Edge cases ---

def test_multiple_at_signs() -> None:
    """Multiple '@' characters should be rejected."""
    assert validate_email("a@b@c.com") is False


def test_empty_domain_label() -> None:
    """Empty label from consecutive dots in domain should be rejected."""
    assert validate_email("user@example..com") is False


def test_domain_label_ends_with_hyphen() -> None:
    """Domain label ending with hyphen should be rejected."""
    assert validate_email("user@domain-.com") is False


def test_tld_with_digits() -> None:
    """TLD containing digits should be rejected (must be alpha only)."""
    assert validate_email("user@example.c0m") is False


def test_max_length_email_valid() -> None:
    """Email at exactly 254 characters should be accepted."""
    # local@domain.com  ->  local = 254 - 1(@) - len(domain.com)
    # domain.com = 10 chars, so local = 254 - 1 - 10 = 243
    local = "a" * 243
    email = f"{local}@domain.com"
    assert len(email) == 254
    assert validate_email(email) is True


def test_exceeding_max_length() -> None:
    """Email exceeding 254 characters should be rejected."""
    local = "a" * 244
    email = f"{local}@domain.com"
    assert len(email) == 255
    assert validate_email(email) is False


def test_local_with_all_allowed_specials() -> None:
    """Local part using all allowed special characters."""
    assert validate_email("a.b_c%d+e-f@example.com") is True


def test_disallowed_char_in_local() -> None:
    """Characters outside the allowed set in local part should be rejected."""
    assert validate_email("user!name@example.com") is False


def test_single_char_local_and_minimal_domain() -> None:
    """Minimal valid email: single-char local and shortest domain."""
    assert validate_email("x@y.ab") is True
