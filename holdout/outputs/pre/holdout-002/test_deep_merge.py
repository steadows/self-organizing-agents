"""Tests for deep_merge utility."""

from deep_merge import deep_merge


def test_basic_merge_no_overlap() -> None:
    assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_override_replaces_scalar() -> None:
    assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}


def test_recursive_dict_merge() -> None:
    base = {"db": {"host": "localhost", "port": 5432}}
    override = {"db": {"port": 3306, "name": "mydb"}}
    expected = {"db": {"host": "localhost", "port": 3306, "name": "mydb"}}
    assert deep_merge(base, override) == expected


def test_three_level_deep_merge() -> None:
    base = {"a": {"b": {"c": 1, "d": 2}}}
    override = {"a": {"b": {"d": 3, "e": 4}}}
    expected = {"a": {"b": {"c": 1, "d": 3, "e": 4}}}
    assert deep_merge(base, override) == expected


def test_lists_replaced_not_appended() -> None:
    assert deep_merge({"tags": [1, 2, 3]}, {"tags": [4, 5]}) == {"tags": [4, 5]}


def test_none_is_regular_value() -> None:
    assert deep_merge({"a": 1}, {"a": None}) == {"a": None}


def test_mixed_types_override_wins_dict_to_scalar() -> None:
    assert deep_merge({"a": {"nested": True}}, {"a": "flat_string"}) == {"a": "flat_string"}


def test_mixed_types_override_wins_scalar_to_dict() -> None:
    assert deep_merge({"a": "flat"}, {"a": {"nested": True}}) == {"a": {"nested": True}}


def test_empty_base() -> None:
    assert deep_merge({}, {"a": 1}) == {"a": 1}


def test_empty_override() -> None:
    assert deep_merge({"a": 1}, {}) == {"a": 1}


def test_both_empty() -> None:
    assert deep_merge({}, {}) == {}


def test_no_mutation_of_base() -> None:
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}
    result = deep_merge(base, override)
    assert result == {"a": {"b": 1, "c": 2}}
    assert base == {"a": {"b": 1}}


def test_no_mutation_of_override() -> None:
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}
    result = deep_merge(base, override)
    assert override == {"a": {"c": 2}}


def test_result_is_independent_copy() -> None:
    base = {"a": {"b": [1, 2]}}
    override = {"c": {"d": [3, 4]}}
    result = deep_merge(base, override)
    result["a"]["b"].append(99)
    result["c"]["d"].append(99)
    assert base == {"a": {"b": [1, 2]}}
    assert override == {"c": {"d": [3, 4]}}


def test_nested_dict_in_result_is_independent() -> None:
    base = {"a": {"b": {"c": 1}}}
    override = {"a": {"b": {"d": 2}}}
    result = deep_merge(base, override)
    result["a"]["b"]["c"] = 999
    assert base["a"]["b"]["c"] == 1


def test_override_none_does_not_delete_key() -> None:
    result = deep_merge({"a": 1, "b": 2}, {"a": None})
    assert result == {"a": None, "b": 2}
    assert "a" in result
