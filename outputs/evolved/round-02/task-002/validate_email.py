"""Utility for validating common email address formats.

Covers the practical subset of email formats seen in real-world usage:
a local part, an '@' symbol, and a domain with at least one dot and a
TLD of two or more alphabetic characters. Does not implement full RFC 5321
compliance.
"""

import re

# Maximum total length of a valid email address per common convention.
MAX_EMAIL_LENGTH = 254

# Pattern for the local part: alphanumeric plus . _ % + -
_LOCAL_ALLOWED = re.compile(r'^[A-Za-z0-9._%+\-]+$')

# Pattern for a single domain label: alphanumeric and hyphens, no leading/trailing hyphen
_LABEL_ALLOWED = re.compile(r'^[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]$|^[A-Za-z0-9]$')

# Pattern for the TLD: at least two alphabetic characters
_TLD_PATTERN = re.compile(r'^[A-Za-z]{2,}$')


def validate_email(email: str) -> bool:
    """Validate that a string looks like a common email address.

    Checks that the email has exactly one '@', a valid local part, and a
    valid domain. This is a practical validator covering common real-world
    formats, not a full RFC 5321 implementation.

    Parameters
    ----------
    email : str
        The string to validate.

    Returns
    -------
    bool
        True if the email matches the expected format, False otherwise.

    Examples
    --------
    >>> validate_email("user@example.com")
    True
    >>> validate_email("plainaddress")
    False
    >>> validate_email("user+tag@gmail.com")
    True
    >>> validate_email(".leading@example.com")
    False
    """
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False

    # Must have exactly one '@'
    parts = email.split('@')
    if len(parts) != 2:
        return False

    local, domain = parts

    if not _is_valid_local(local):
        return False

    if not _is_valid_domain(domain):
        return False

    return True


def _is_valid_local(local: str) -> bool:
    """Return True if the local part of an email address is valid."""
    if not local:
        return False

    if local.startswith('.') or local.endswith('.'):
        return False

    if '..' in local:
        return False

    return bool(_LOCAL_ALLOWED.match(local))


def _is_valid_domain(domain: str) -> bool:
    """Return True if the domain part of an email address is valid."""
    if not domain or '.' not in domain:
        return False

    labels = domain.split('.')

    # Each label must be non-empty and match the label pattern
    for label in labels:
        if not label:
            return False
        if not _LABEL_ALLOWED.match(label):
            return False

    # TLD is the last label and must be at least 2 alphabetic characters
    tld = labels[-1]
    return bool(_TLD_PATTERN.match(tld))
