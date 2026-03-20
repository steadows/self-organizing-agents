"""Utility for validating common email address formats.

Covers the practical subset of email formats seen in real-world usage.
Does NOT implement full RFC 5321/5322 compliance.
"""

import re

MAX_EMAIL_LENGTH = 254

_LOCAL_PATTERN = re.compile(r'^[a-zA-Z0-9_%+\-]+(\.[a-zA-Z0-9_%+\-]+)*$')
_LABEL_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?$')
_TLD_PATTERN = re.compile(r'^[a-zA-Z]{2,}$')


def _is_valid_local(local: str) -> bool:
    """Return True if the local part of an email address is valid."""
    if not local:
        return False
    return bool(_LOCAL_PATTERN.match(local))


def _is_valid_domain(domain: str) -> bool:
    """Return True if the domain part of an email address is valid."""
    if not domain or '.' not in domain:
        return False
    labels = domain.split('.')
    tld = labels[-1]
    if not _TLD_PATTERN.match(tld):
        return False
    for label in labels[:-1]:
        if not label:
            return False
        if not _LABEL_PATTERN.match(label):
            return False
    return True


def validate_email(email: str) -> bool:
    """Validate that a string looks like a common email address.

    Checks for a local part, exactly one ``@`` separator, and a domain with
    at least one dot and an alphabetic TLD of two or more characters.  This
    covers practical real-world formats and intentionally does not implement
    full RFC 5321/5322 compliance.

    Parameters
    ----------
    email:
        The string to validate.

    Returns
    -------
    bool
        ``True`` if the string matches expected email format, ``False``
        otherwise.

    Examples
    --------
    >>> validate_email("user@example.com")
    True
    >>> validate_email("plainaddress")
    False
    """
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False

    parts = email.split('@')
    if len(parts) != 2:
        return False

    local, domain = parts
    return _is_valid_local(local) and _is_valid_domain(domain)
