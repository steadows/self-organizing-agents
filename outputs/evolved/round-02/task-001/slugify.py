"""Utility for converting arbitrary Unicode strings into URL-safe ASCII slugs."""

import re
import unicodedata


def slugify(text: str, separator: str = "-", max_length: int = 200) -> str:
    """Convert an arbitrary Unicode string into a URL-safe ASCII slug.

    Unicode characters are transliterated to their closest ASCII equivalents
    using NFKD normalization followed by ASCII encoding. All letters are
    lowercased, and runs of non-alphanumeric characters are collapsed into a
    single separator. The result is trimmed to ``max_length``, truncating at a
    word boundary when possible.

    Parameters
    ----------
    text:
        The input string to convert.
    separator:
        The character used to replace runs of non-alphanumeric characters.
        Defaults to ``"-"``.
    max_length:
        Maximum length of the returned slug. Must be non-negative. When the
        slug exceeds this length it is truncated at the last separator boundary
        within the limit; if no separator exists within the limit, a hard
        truncation at ``max_length`` is applied. Defaults to ``200``.

    Returns
    -------
    str
        A URL-safe ASCII slug, or an empty string when no valid slug characters
        are found or ``max_length`` is ``0``.

    Examples
    --------
    >>> slugify("Hello World!")
    'hello-world'
    >>> slugify("Héllo Wörld")
    'hello-world'
    >>> slugify("über cool café")
    'uber-cool-cafe'
    >>> slugify("  --foo--bar--baz--  ")
    'foo-bar-baz'
    >>> slugify("a-very-long-slug " * 20, max_length=20)
    'a-very-long-slug'
    """
    if max_length < 0:
        raise ValueError(f"max_length must be non-negative, got {max_length}")

    if max_length == 0:
        return ""

    # Transliterate Unicode to closest ASCII equivalents via NFKD decomposition.
    normalized = unicodedata.normalize("NFKD", text)
    ascii_bytes = normalized.encode("ascii", "ignore")
    ascii_text = ascii_bytes.decode("ascii")

    # Lowercase everything.
    lowered = ascii_text.lower()

    # Collapse runs of non-alphanumeric characters into a single separator.
    slug = re.sub(r"[^a-z0-9]+", separator, lowered)

    # Strip leading and trailing separators.
    slug = slug.strip(separator)

    if not slug:
        return ""

    # Truncate to max_length with word-boundary preference.
    if len(slug) > max_length:
        truncated = slug[:max_length]
        # Find the last separator within the truncated portion.
        last_sep = truncated.rfind(separator)
        if last_sep > 0:
            slug = truncated[:last_sep]
        else:
            slug = truncated
        # Strip any trailing separator left over after truncation.
        slug = slug.rstrip(separator)

    return slug
