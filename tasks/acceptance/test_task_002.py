"""Acceptance tests for task-002: validate_email()

Tests the contract:
  validate_email(email: str) -> bool

Returns True if the given string is a syntactically valid email address
per common RFC 5321/5322 rules, False otherwise.

These tests are FROZEN ground truth. Implementations must pass all of them.
"""

import os
import sys

# Allow importing from the output directory passed via environment variable
# or default to the current directory
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

from validate_email import validate_email


# ── Valid emails ────────────────────────────────────────────────────────────

def test_validate_email_valid_basic() -> None:
    assert validate_email("user@example.com") is True


def test_validate_email_valid_subdomain() -> None:
    assert validate_email("first.last@sub.domain.co.uk") is True


def test_validate_email_valid_plus_tag() -> None:
    assert validate_email("user+tag@gmail.com") is True


def test_validate_email_valid_short() -> None:
    assert validate_email("a@b.co") is True


def test_validate_email_valid_numeric() -> None:
    assert validate_email("123@456.com") is True


def test_validate_email_valid_hyphen_in_domain() -> None:
    assert validate_email("user@my-domain.com") is True


def test_validate_email_valid_underscore_in_local() -> None:
    assert validate_email("user_name@example.com") is True


def test_validate_email_return_type() -> None:
    """Return value is always a bool."""
    result = validate_email("user@example.com")
    assert isinstance(result, bool)

    result2 = validate_email("invalid")
    assert isinstance(result2, bool)


# ── Invalid emails ──────────────────────────────────────────────────────────

def test_validate_email_empty_string() -> None:
    assert validate_email("") is False


def test_validate_email_plain_address() -> None:
    assert validate_email("plainaddress") is False


def test_validate_email_no_local_part() -> None:
    assert validate_email("@no-local.com") is False


def test_validate_email_leading_dot() -> None:
    assert validate_email(".leading@example.com") is False


def test_validate_email_trailing_dot_local() -> None:
    assert validate_email("trailing.@example.com") is False


def test_validate_email_double_dot_local() -> None:
    assert validate_email("double..dot@example.com") is False


def test_validate_email_hyphen_start_domain() -> None:
    assert validate_email("user@-hyphen-start.com") is False


def test_validate_email_single_char_tld() -> None:
    """TLD must be at least 2 characters."""
    assert validate_email("user@domain.c") is False


def test_validate_email_double_at() -> None:
    assert validate_email("user@@double.com") is False


def test_validate_email_no_at_sign() -> None:
    assert validate_email("userdomain.com") is False


def test_validate_email_multiple_at_signs() -> None:
    assert validate_email("user@domain@other.com") is False


def test_validate_email_space_in_address() -> None:
    assert validate_email("user @example.com") is False


def test_validate_email_missing_domain() -> None:
    assert validate_email("user@") is False


def test_validate_email_missing_tld() -> None:
    assert validate_email("user@domain") is False


# ── Length edge cases ───────────────────────────────────────────────────────

def test_validate_email_max_length_254_valid() -> None:
    """An email at exactly 254 chars should be valid."""
    # Build a 254-char email: local@domain.com
    # local part: variable, domain: "d" * N + ".com"
    # Total = len(local) + 1 (@) + len(domain)
    # We need total == 254
    domain = "d" * 63 + "." + "d" * 63 + ".com"  # 63 + 1 + 63 + 4 = 131
    local_len = 254 - 1 - len(domain)  # 254 - 1 - 131 = 122
    # Local part max is 64 per RFC, but we test total length here
    # Use a shorter approach: pad the domain
    local_part = "a" * 64
    # domain needs to be 254 - 64 - 1 = 189 chars
    # Build with labels: max label is 63 chars
    # 63.63.63.com = 63+1+63+1+63+1+3 = 195 — too long
    # 63.63.59.com = 63+1+63+1+59+1+3 = 191 — too long
    # Let's just do: 254 - 65 = 189 domain chars
    # 63.63.55.com = 63+1+63+1+55+1+3 = 187 — close
    # Actually, let's construct precisely:
    remaining = 254 - 65  # 189 chars for domain
    # domain = "d"*63 + "." + "d"*63 + "." + "d"*(189-63-1-63-1-3) + ".com"
    #        = "d"*63 + "." + "d"*63 + "." + "d"*55 + ".com"
    #        = 63 + 1 + 63 + 1 + 55 + 1 + 3 = 187... need 189
    # Adjust: "d"*63 + "." + "d"*63 + "." + "d"*57 + ".com"
    #        = 63+1+63+1+57+1+3 = 189 ✓
    domain = "d" * 63 + "." + "d" * 63 + "." + "d" * 57 + ".com"
    email = local_part + "@" + domain
    assert len(email) == 254
    assert validate_email(email) is True


def test_validate_email_over_254_invalid() -> None:
    """An email over 254 chars should be invalid."""
    local_part = "a" * 64
    domain = "d" * 63 + "." + "d" * 63 + "." + "d" * 58 + ".com"
    email = local_part + "@" + domain
    assert len(email) > 254
    assert validate_email(email) is False
