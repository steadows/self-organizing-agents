"""Acceptance tests for task-001: slugify()

Tests the contract:
  slugify(text: str, separator: str = "-", max_length: int = 200) -> str

Converts arbitrary text into a URL-safe slug by lowercasing, transliterating
unicode, collapsing separators, and optionally truncating at word boundaries.

These tests are FROZEN ground truth. Implementations must pass all of them.
"""

import os
import sys

# Allow importing from the output directory passed via environment variable
# or default to the current directory
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

from slugify import slugify


# ── Happy path ──────────────────────────────────────────────────────────────

def test_slugify_basic_text() -> None:
    """Simple English text with punctuation."""
    assert slugify("Hello World!") == "hello-world"


def test_slugify_accented_characters() -> None:
    """Accented latin characters are transliterated."""
    assert slugify("Héllo Wörld") == "hello-world"


def test_slugify_return_type() -> None:
    """Return value is always a str."""
    result = slugify("anything")
    assert isinstance(result, str)


def test_slugify_already_clean() -> None:
    """Input that is already a valid slug passes through unchanged."""
    assert slugify("already-clean") == "already-clean"


# ── Edge cases ──────────────────────────────────────────────────────────────

def test_slugify_empty_string() -> None:
    assert slugify("") == ""


def test_slugify_all_punctuation() -> None:
    assert slugify("!@#$%^&*()") == ""


def test_slugify_only_whitespace() -> None:
    assert slugify("   \t\n  ") == ""


def test_slugify_max_length_zero() -> None:
    assert slugify("Hello World", max_length=0) == ""


# ── Separator behaviour ────────────────────────────────────────────────────

def test_slugify_collapses_repeated_separators() -> None:
    """Runs of separators are collapsed to a single one."""
    assert slugify("--foo--bar--") == "foo-bar"


def test_slugify_custom_separator() -> None:
    """A custom separator replaces the default hyphen."""
    assert slugify("Hello World!", separator="_") == "hello_world"


def test_slugify_custom_separator_collapsing() -> None:
    """Custom separators are also collapsed."""
    assert slugify("__foo__bar__", separator="_") == "foo_bar"


def test_slugify_strips_leading_trailing_separators() -> None:
    """No leading or trailing separator in the output."""
    result = slugify("  --hello--  ")
    assert not result.startswith("-")
    assert not result.endswith("-")
    assert result == "hello"


# ── Truncation ──────────────────────────────────────────────────────────────

def test_slugify_truncation_respects_max_length() -> None:
    """Output never exceeds max_length."""
    long_text = "this is a really long sentence that should be truncated"
    result = slugify(long_text, max_length=20)
    assert len(result) <= 20


def test_slugify_truncation_at_word_boundary() -> None:
    """Truncation should not cut a word in half."""
    text = "hello world foo bar baz"
    result = slugify(text, max_length=12)
    assert len(result) <= 12
    # Should not end with a partial word or a separator
    assert not result.endswith("-")


def test_slugify_truncation_no_trailing_separator() -> None:
    """After truncation, no trailing separator."""
    text = "aaa bbb ccc ddd eee"
    result = slugify(text, max_length=8)
    assert not result.endswith("-")


def test_slugify_max_length_default() -> None:
    """Default max_length is 200."""
    text = "a " * 300  # 600 chars before slugify
    result = slugify(text)
    assert len(result) <= 200


# ── Unicode transliteration ─────────────────────────────────────────────────

def test_slugify_spanish_unicode() -> None:
    assert slugify("Ñoño año español") == "nono-ano-espanol"


def test_slugify_german_unicode() -> None:
    assert slugify("über cool café") == "uber-cool-cafe"


def test_slugify_mixed_unicode_and_numbers() -> None:
    result = slugify("Ärtikel №5 — Pro")
    # Should transliterate and keep numbers
    assert "5" in result
    assert result.startswith("artikel")


def test_slugify_cjk_or_non_latin_produces_string() -> None:
    """Non-transliterable characters may be dropped but result is still valid."""
    result = slugify("你好世界")
    assert isinstance(result, str)
    # Result should contain only slug-safe characters
    import re
    assert re.fullmatch(r"[a-z0-9-]*", result) is not None
