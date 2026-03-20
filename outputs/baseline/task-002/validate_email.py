"""Validate that a string looks like a common email address.

Covers the practical subset of email formats seen in real-world usage.
Not RFC 5321/5322 compliant. No support for quoted local parts, IP
address literals, comments, DNS verification, or internationalized
addresses.
"""

import re

# Maximum total length per RFC 5321 practical limit
MAX_EMAIL_LENGTH = 254

# Local part: ASCII alphanumeric, '.', '_', '%', '+', '-'
LOCAL_CHAR_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+$')

# Domain label: ASCII alphanumeric and hyphens
DOMAIN_LABEL_PATTERN = re.compile(r'^[a-zA-Z0-9-]+$')

# TLD: at least 2 alphabetic characters
TLD_PATTERN = re.compile(r'^[a-zA-Z]{2,}$')


def validate_email(email: str) -> bool:
    """Validate that a string looks like a common email address.

    Checks for a local part, exactly one '@', and a domain with at least
    one dot and a TLD of two or more alphabetic characters.

    Args:
        email: The string to validate.

    Returns:
        True if the string matches common email format, False otherwise.
    """
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False

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
        local: The portion before the '@'.

    Returns:
        True if valid, False otherwise.
    """
    if not local:
        return False

    if not LOCAL_CHAR_PATTERN.match(local):
        return False

    if local.startswith('.') or local.endswith('.'):
        return False

    if '..' in local:
        return False

    return True


def _validate_domain(domain: str) -> bool:
    """Validate the domain part of an email address.

    Args:
        domain: The portion after the '@'.

    Returns:
        True if valid, False otherwise.
    """
    if not domain or '.' not in domain:
        return False

    labels = domain.split('.')

    for label in labels:
        if not label:
            return False
        if not DOMAIN_LABEL_PATTERN.match(label):
            return False
        if label.startswith('-') or label.endswith('-'):
            return False

    tld = labels[-1]
    if not TLD_PATTERN.match(tld):
        return False

    return True
