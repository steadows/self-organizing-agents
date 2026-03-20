"""Tests for the deep_merge utility function."""

import pytest

from deep_merge import deep_merge


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_basic_no_overlap():
    assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_override_replaces_scalar():
    assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}


def test_recursive_dict_merge():
    result = deep_merge(
        {"db": {"host": "localhost", "port": 5432}},
        {"db": {"port": 3306, "name": "mydb"}},
    )
    assert result == {"db": {"host": "localhost", "port": 3306, "name": "mydb"}}


def test_three_level_deep_merge():
    result = deep_merge(
        {"a": {"b": {"c": 1, "d": 2}}},
        {"a": {"b": {"d": 3, "e": 4}}},
    )
    assert result == {"a": {"b": {"c": 1, "d": 3, "e": 4}}}


def test_lists_are_replaced_not_appended():
    assert deep_merge({"tags": [1, 2, 3]}, {"tags": [4, 5]}) == {"tags": [4, 5]}


def test_none_is_regular_value():
    assert deep_merge({"a": 1}, {"a": None}) == {"a": None}


def test_mixed_types_override_wins_dict_replaced_by_scalar():
    assert deep_merge({"a": {"nested": True}}, {"a": "flat_string"}) == {"a": "flat_string"}


def test_mixed_types_override_wins_scalar_replaced_by_dict():
    assert deep_merge({"a": "flat_string"}, {"a": {"nested": True}}) == {"a": {"nested": True}}


def test_key_only_in_base():
    assert deep_merge({"a": 1, "b": 2}, {}) == {"a": 1, "b": 2}


def test_key_only_in_override():
    assert deep_merge({}, {"a": 1, "b": 2}) == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_both_empty():
    assert deep_merge({}, {}) == {}


def test_base_empty_returns_deep_copy_of_override():
    override = {"a": {"nested": [1, 2, 3]}}
    result = deep_merge({}, override)
    assert result == override
    # Must be independent copy
    override["a"]["nested"].append(4)
    assert result == {"a": {"nested": [1, 2, 3]}}


def test_override_empty_returns_deep_copy_of_base():
    base = {"a": {"nested": [1, 2, 3]}}
    result = deep_merge(base, {})
    assert result == base
    # Must be independent copy
    base["a"]["nested"].append(4)
    assert result == {"a": {"nested": [1, 2, 3]}}


def test_result_independent_of_base():
    base = {"a": {"x": 1}}
    result = deep_merge(base, {"b": 2})
    result["a"]["x"] = 999
    assert base["a"]["x"] == 1


def test_result_independent_of_override():
    override = {"a": {"x": 1}}
    result = deep_merge({"b": 2}, override)
    result["a"]["x"] = 999
    assert override["a"]["x"] == 1


def test_base_not_mutated():
    base = {"a": 1, "b": {"c": 2}}
    deep_merge(base, {"b": {"c": 99, "d": 3}})
    assert base == {"a": 1, "b": {"c": 2}}


def test_override_not_mutated():
    override = {"b": {"c": 99, "d": 3}}
    deep_merge({"a": 1, "b": {"c": 2}}, override)
    assert override == {"b": {"c": 99, "d": 3}}


def test_override_key_set_to_none_does_not_delete():
    result = deep_merge({"a": 1, "b": 2}, {"a": None})
    assert result == {"a": None, "b": 2}


def test_int_overrides_dict():
    result = deep_merge({"x": {"nested": True}}, {"x": 42})
    assert result == {"x": 42}


def test_dict_overrides_int():
    result = deep_merge({"x": 42}, {"x": {"nested": True}})
    assert result == {"x": {"nested": True}}


# ---------------------------------------------------------------------------
# ValueError tests (simulating invalid-input "error path")
# ---------------------------------------------------------------------------


def test_raises_if_base_is_not_dict():
    with pytest.raises(ValueError, match="'base' must be a dict"):
        deep_merge("not a dict", {})  # type: ignore[arg-type]


def test_raises_if_override_is_not_dict():
    with pytest.raises(ValueError, match="'override' must be a dict"):
        deep_merge({}, [1, 2, 3])  # type: ignore[arg-type]


def test_raises_if_both_non_dict():
    with pytest.raises(ValueError):
        deep_merge(None, None)  # type: ignore[arg-type]
