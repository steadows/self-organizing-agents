"""Utility for converting arbitrary Unicode strings into URL-safe ASCII slugs."""

import re
import unicodedata


def slugify(text: str, separator: str = "-", max_length: int = 200) -> str:
    """Convert a Unicode string into a URL-safe ASCII slug.

    Unicode characters are transliterated to their closest ASCII equivalents
    via NFKD normalization, lowercased, and runs of non-alphanumeric characters
    are collapsed into a single separator. The result is trimmed to max_length,
    preferring truncation at a word boundary.

    Args:
        text: The input string to slugify.
        separator: Character(s) used to replace non-alphanumeric runs.
        max_length: Maximum length of the returned slug.

    Returns:
        A lowercased, ASCII-only slug string.
    """
    if max_length <= 0:
        return ""

    # Transliterate Unicode to ASCII approximations
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

    # Lowercase
    ascii_text = ascii_text.lower()

    # Replace runs of non-alphanumeric characters with a single separator
    slug = re.sub(r"[^a-z0-9]+", separator, ascii_text)

    # Strip leading/trailing separators
    slug = slug.strip(separator)

    if not slug:
        return ""

    # Truncate to max_length if needed
    if len(slug) > max_length:
        truncated = slug[:max_length]

        # If the cut lands mid-word (next char is not a separator),
        # prefer truncating at the last separator boundary within the limit
        if slug[max_length] != separator:
            last_sep = truncated.rfind(separator)
            if last_sep > 0:
                truncated = truncated[:last_sep]

        # Strip any trailing separator
        slug = truncated.rstrip(separator)

    return slug
