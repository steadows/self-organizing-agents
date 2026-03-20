"""Tests for the slugify utility function."""

import pytest

from slugify import slugify


def test_basic_ascii_words():
    assert slugify("Hello World!") == "hello-world"


def test_unicode_transliteration():
    assert slugify("Héllo Wörld") == "hello-world"


def test_consecutive_separators_collapse():
    assert slugify("  --foo--bar--baz--  ") == "foo-bar-baz"


def test_empty_string_returns_empty():
    assert slugify("") == ""


def test_only_special_characters_returns_empty():
    assert slugify("@#$%^&*()") == ""


def test_only_whitespace_returns_empty():
    assert slugify("   ") == ""


def test_spanish_characters():
    assert slugify("Ñoño año español") == "nono-ano-espanol"


def test_umlaut_and_accent():
    assert slugify("über cool café") == "uber-cool-cafe"


def test_max_length_truncates_at_word_boundary():
    # The spec example: slugify("a-very-long-slug " * 20, max_length=20)
    # Expected: truncated at a word boundary within max_length=20,
    # no trailing separator, result is <= 20 chars and ends on a full word.
    result = slugify("a-very-long-slug " * 20, max_length=20)
    assert len(result) <= 20
    assert not result.endswith("-")
    # Every segment should be a complete token (no partial words mid-separator)
    # The slug is all repetitions of "a-very-long-slug"; valid boundaries are
    # at indices 16 ("a-very-long-slug") or 18 ("a-very-long-slug-a").
    assert result in ("a-very-long-slug", "a-very-long-slug-a")


def test_max_length_zero_returns_empty():
    assert slugify("hello world", max_length=0) == ""


def test_single_word_no_surrounding_separators():
    assert slugify("python") == "python"


def test_already_slug_safe_returned_lowercased():
    assert slugify("already-slug-safe") == "already-slug-safe"
    assert slugify("UPPERCASE") == "uppercase"


def test_hard_truncate_when_no_separator_within_limit():
    # A single long word with no separator — must hard-truncate
    result = slugify("abcdefghijklmnopqrstuvwxyz", max_length=10)
    assert result == "abcdefghij"
    assert len(result) == 10


def test_max_length_exact_fit():
    result = slugify("hello-world", max_length=11)
    assert result == "hello-world"


def test_max_length_strips_trailing_separator_after_truncation():
    # "hello-" would be 6 chars; truncation should strip trailing separator
    result = slugify("hello world", max_length=6)
    assert not result.endswith("-")


def test_numbers_preserved():
    assert slugify("python3 rocks") == "python3-rocks"


def test_custom_separator():
    assert slugify("hello world", separator="_") == "hello_world"


def test_mixed_unicode_and_numbers():
    assert slugify("Ünit 42 tëst") == "unit-42-test"
