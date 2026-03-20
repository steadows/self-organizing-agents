"""Tests for the slugify utility function."""

from slugify import slugify


def test_basic_ascii_string() -> None:
    assert slugify("Hello World!") == "hello-world"


def test_unicode_transliteration() -> None:
    assert slugify("Héllo Wörld") == "hello-world"


def test_strips_surrounding_separators() -> None:
    assert slugify("  --foo--bar--baz--  ") == "foo-bar-baz"


def test_empty_string() -> None:
    assert slugify("") == ""


def test_only_special_characters() -> None:
    assert slugify("@#$%^&*()") == ""


def test_spanish_unicode() -> None:
    assert slugify("Ñoño año español") == "nono-ano-espanol"


def test_german_and_french_unicode() -> None:
    assert slugify("über cool café") == "uber-cool-cafe"


def test_max_length_truncation_at_word_boundary() -> None:
    # "a-very-long-slug " * 20 -> "a-very-long-slug-a-very-long-slug-..."
    # Truncated to 20: "a-very-long-slug-a-v", last sep at 18
    # -> "a-very-long-slug-a" (18 chars, clean word boundary)
    result = slugify("a-very-long-slug " * 20, max_length=20)
    assert result == "a-very-long-slug-a"
    assert len(result) <= 20


def test_max_length_truncation_clean_boundary() -> None:
    # When max_length falls exactly after a separator + complete word
    result = slugify("hello world foo bar baz", max_length=15)
    assert result == "hello-world-foo"
    assert len(result) <= 15


def test_max_length_zero() -> None:
    assert slugify("hello", max_length=0) == ""


def test_only_whitespace() -> None:
    assert slugify("   ") == ""


def test_single_word() -> None:
    assert slugify("Hello") == "hello"


def test_already_slug_safe() -> None:
    assert slugify("already-safe") == "already-safe"


def test_consecutive_separators_collapse() -> None:
    assert slugify("foo---bar___baz") == "foo-bar-baz"


def test_hard_truncate_no_separator() -> None:
    """When no separator exists within max_length, hard-truncate."""
    result = slugify("abcdefghijklmnopqrstuvwxyz", max_length=10)
    assert result == "abcdefghij"
    assert len(result) == 10


def test_max_length_exact_fit() -> None:
    assert slugify("hello-world", max_length=11) == "hello-world"


def test_custom_separator() -> None:
    assert slugify("Hello World!", separator="_") == "hello_world"


def test_numeric_input() -> None:
    assert slugify("123 456") == "123-456"
