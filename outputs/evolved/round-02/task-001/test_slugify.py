"""Tests for the slugify utility function."""

import pytest

from slugify import slugify


# ---------------------------------------------------------------------------
# Happy path tests
# ---------------------------------------------------------------------------

def test_basic_ascii_with_space():
    assert slugify("Hello World!") == "hello-world"


def test_unicode_umlaut_and_accented():
    assert slugify("Héllo Wörld") == "hello-world"


def test_leading_trailing_and_inner_separators():
    assert slugify("  --foo--bar--baz--  ") == "foo-bar-baz"


def test_spanish_tilde_characters():
    assert slugify("Ñoño año español") == "nono-ano-espanol"


def test_german_umlaut_transliteration():
    assert slugify("über cool café") == "uber-cool-cafe"


def test_already_slug_safe_input():
    assert slugify("hello-world") == "hello-world"


def test_already_ascii_lowercased():
    assert slugify("simple") == "simple"


def test_mixed_case_ascii():
    assert slugify("CamelCaseWord") == "camelcaseword"


def test_numbers_preserved():
    assert slugify("python3 is great") == "python3-is-great"


def test_custom_separator():
    assert slugify("Hello World", separator="_") == "hello_world"


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

def test_empty_string_returns_empty():
    assert slugify("") == ""


def test_only_special_characters_returns_empty():
    assert slugify("@#$%^&*") == ""


def test_only_whitespace_returns_empty():
    assert slugify("   ") == ""


def test_single_word_no_surrounding_separators():
    assert slugify("Python") == "python"


def test_max_length_zero_returns_empty():
    assert slugify("hello-world", max_length=0) == ""


def test_max_length_truncates_at_word_boundary():
    # "a-very-long-slug " * 20 expands to "a-very-long-slug-a-very-long-slug-..."
    # slug[:20] == "a-very-long-slug-a-v"; last separator at index 18 → "a-very-long-slug-a"
    result = slugify("a-very-long-slug " * 20, max_length=20)
    # Must be within max_length and must not end with a separator.
    assert len(result) <= 20
    assert not result.endswith("-")
    # Must be a clean word-boundary truncation (no partial words).
    assert result == "a-very-long-slug-a"


def test_max_length_hard_truncate_when_no_separator():
    # A single long word with no separator — must hard-truncate.
    result = slugify("abcdefghijklmnopqrstuvwxyz", max_length=10)
    assert result == "abcdefghij"
    assert len(result) == 10


def test_max_length_no_trailing_separator_after_truncation():
    # Construct input where truncation would land on a separator.
    result = slugify("foo bar baz", max_length=4)
    # "foo-bar-baz"[:4] == "foo-", last sep at index 3 → truncate to "foo"
    assert not result.endswith("-")


def test_multiple_consecutive_separators_collapse():
    assert slugify("foo---bar") == "foo-bar"


def test_max_length_negative_raises_value_error():
    with pytest.raises(ValueError, match="max_length must be non-negative"):
        slugify("hello", max_length=-1)


def test_result_does_not_exceed_max_length():
    long_input = "Hello World! " * 50
    result = slugify(long_input, max_length=30)
    assert len(result) <= 30


def test_result_never_starts_or_ends_with_separator():
    result = slugify("!!hello world!!", separator="-")
    assert not result.startswith("-")
    assert not result.endswith("-")


def test_unicode_only_non_transliterable_returns_empty():
    # Characters that have no ASCII equivalent after NFKD (e.g., pure CJK).
    result = slugify("日本語")
    assert result == ""


def test_max_length_exact_fit_no_truncation():
    slug = slugify("hello-world")  # 11 chars
    result = slugify("hello-world", max_length=11)
    assert result == slug


def test_max_length_one_less_than_slug_truncates_at_boundary():
    # "hello-world" is 11 chars; max_length=10 → last sep at 5 → "hello"
    result = slugify("hello-world", max_length=10)
    assert result == "hello"
