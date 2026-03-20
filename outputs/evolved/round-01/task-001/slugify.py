"""Utility for converting arbitrary Unicode strings into URL-safe ASCII slugs."""

import re
import unicodedata


def slugify(text: str, separator: str = "-", max_length: int = 200) -> str:
    """Convert an arbitrary Unicode string into a URL-safe ASCII slug.

    Unicode characters are transliterated to their closest ASCII equivalents
    via NFKD normalization. The result is lowercased, with runs of
    non-alphanumeric characters collapsed into a single separator.

    Args:
        text: The input string to slugify.
        separator: Character used to replace non-alphanumeric runs. Defaults to "-".
        max_length: Maximum length of the returned slug. Truncates at a word
            boundary when possible. Defaults to 200.

    Returns:
        A URL-safe ASCII slug string, or "" if no valid characters remain.
    """
    if not text or max_length == 0:
        return ""

    # Transliterate Unicode to ASCII via NFKD decomposition
    normalized = unicodedata.normalize("NFKD", text)
    ascii_bytes = normalized.encode("ascii", "ignore")
    ascii_text = ascii_bytes.decode("ascii")

    # Lowercase
    ascii_text = ascii_text.lower()

    # Collapse runs of non-alphanumeric characters into the separator
    escaped_sep = re.escape(separator)
    slug = re.sub(r"[^a-z0-9]+", separator, ascii_text)

    # Strip leading and trailing separators
    slug = slug.strip(separator)

    if not slug:
        return ""

    # Truncate to max_length
    if len(slug) > max_length:
        truncated = slug[:max_length]
        # Find the last separator within the limit for a clean word boundary
        last_sep = truncated.rfind(separator)
        if last_sep > 0:
            truncated = truncated[:last_sep]
        # Strip any trailing separator left after truncation
        slug = truncated.rstrip(separator)

    return slug
