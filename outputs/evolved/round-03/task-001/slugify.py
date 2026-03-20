"""Utility for converting arbitrary Unicode strings into URL-safe ASCII slugs."""

import re
import unicodedata


def slugify(text: str, separator: str = "-", max_length: int = 200) -> str:
    """Convert an arbitrary Unicode string into a URL-safe ASCII slug.

    Unicode characters are transliterated to their closest ASCII equivalents
    via NFKD normalization. All letters are lowercased, and runs of
    non-alphanumeric characters are collapsed into a single separator.
    The result is trimmed to ``max_length``, truncating at a word boundary
    when possible.

    Parameters
    ----------
    text:
        The input string to slugify.
    separator:
        The character used to replace runs of non-alphanumeric characters.
        Defaults to ``"-"``.
    max_length:
        Maximum number of characters in the returned slug. Must be >= 0.
        Defaults to ``200``.

    Returns
    -------
    str
        A URL-safe ASCII slug, or an empty string when no valid characters
        remain after transliteration.

    Raises
    ------
    ValueError
        If ``max_length`` is negative.

    Examples
    --------
    >>> slugify("Hello World!")
    'hello-world'
    >>> slugify("Héllo Wörld")
    'hello-world'
    >>> slugify("über cool café")
    'uber-cool-cafe'
    >>> slugify("a-very-long-slug " * 20, max_length=20)
    'a-very-long-slug'
    """
    if max_length < 0:
        raise ValueError(f"max_length must be >= 0, got {max_length}")

    if max_length == 0:
        return ""

    # Transliterate Unicode to closest ASCII equivalents via NFKD decomposition.
    normalized = unicodedata.normalize("NFKD", text)
    ascii_bytes = normalized.encode("ascii", "ignore")
    ascii_text = ascii_bytes.decode("ascii")

    # Lowercase.
    lowered = ascii_text.lower()

    # Replace runs of non-alphanumeric characters with the separator.
    slug = re.sub(r"[^a-z0-9]+", separator, lowered)

    # Strip leading/trailing separators.
    slug = slug.strip(separator)

    if not slug:
        return ""

    # Truncate to max_length, preferring a word boundary.
    if len(slug) > max_length:
        slug = _truncate_at_boundary(slug, separator, max_length)

    return slug


def _truncate_at_boundary(slug: str, separator: str, max_length: int) -> str:
    """Truncate a slug to ``max_length``, preferring the last separator boundary.

    Parameters
    ----------
    slug:
        The slug string to truncate (already stripped of leading/trailing
        separators).
    separator:
        The separator character used in the slug.
    max_length:
        Maximum allowed length for the returned string.

    Returns
    -------
    str
        The truncated slug, with any trailing separator removed.
    """
    candidate = slug[:max_length]
    boundary = candidate.rfind(separator)
    if boundary > 0:
        candidate = candidate[:boundary]
    # Strip trailing separator in case hard-truncation left one.
    return candidate.rstrip(separator)
