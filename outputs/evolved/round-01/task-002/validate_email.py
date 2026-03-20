"""Utility for validating common email address formats.

Covers the practical subset of email formats seen in real-world usage.
Does NOT implement full RFC 5321/5322 compliance.
"""

import re

# Maximum total email length per RFC 5321
MAX_EMAIL_LENGTH = 254

# Regex for the local part: alphanumeric plus . _ % + -
_LOCAL_ALLOWED = re.compile(r'^[A-Za-z0-9._+%\-]+$')

# Regex for a single domain label: alphanumeric and hyphens
_LABEL_ALLOWED = re.compile(r'^[A-Za-z0-9\-]+$')

# Regex for the TLD: at least 2 alphabetic characters
_TLD_PATTERN = re.compile(r'^[A-Za-z]{2,}$')


def validate_email(email: str) -> bool:
    """Validate that a string looks like a common email address.

    Checks for a local part, exactly one '@', and a domain with at least one
    dot and a TLD of two or more alphabetic characters.

    Args:
        email: The string to validate.

    Returns:
        True if the email matches common real-world email format, False otherwise.
    """
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False

    # Must contain exactly one '@'
    parts = email.split('@')
    if len(parts) != 2:
        return False

    local, domain = parts

    if not _validate_local(local):
        return False

    if not _validate_domain(domain):
        return False

    return True


def _validate_local(local: str) -> bool:
    """Validate the local part of an email address.

    Args:
        local: The local part (before '@').

    Returns:
        True if valid, False otherwise.
    """
    if not local:
        return False

    if not _LOCAL_ALLOWED.match(local):
        return False

    if local.startswith('.') or local.endswith('.'):
        return False

    if '..' in local:
        return False

    return True


def _validate_domain(domain: str) -> bool:
    """Validate the domain part of an email address.

    Args:
        domain: The domain part (after '@').

    Returns:
        True if valid, False otherwise.
    """
    if not domain or '.' not in domain:
        return False

    labels = domain.split('.')

    # Each label must be non-empty, match allowed chars, and not start/end with hyphen
    for label in labels:
        if not label:
            return False
        if not _LABEL_ALLOWED.match(label):
            return False
        if label.startswith('-') or label.endswith('-'):
            return False

    # TLD is the final label and must be at least 2 alphabetic characters
    tld = labels[-1]
    if not _TLD_PATTERN.match(tld):
        return False

    return True
