"""Frozen acceptance tests for deep_merge().

Holdout task 002: Recursively merge two dictionaries where override values
take precedence, nested dicts are merged recursively, and lists are replaced
(not appended).

Spec:
    deep_merge(base: dict, override: dict) -> dict
"""

import sys
import os

# Allow importing from the output directory passed via environment variable
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

import copy

import pytest

from deep_merge import deep_merge


# --- No overlap ---


def test_disjoint_keys() -> None:
    """Non-overlapping keys are combined."""
    result = deep_merge({"a": 1}, {"b": 2})
    assert result == {"a": 1, "b": 2}


# --- Override scalar ---


def test_override_scalar() -> None:
    """Same key in override replaces base value."""
    result = deep_merge({"a": 1}, {"a": 2})
    assert result == {"a": 2}


# --- Recursive merge ---


def test_nested_dict_merge() -> None:
    """Nested dicts are merged recursively, not replaced."""
    base = {"db": {"host": "localhost", "port": 5432}}
    override = {"db": {"port": 3306, "name": "mydb"}}
    result = deep_merge(base, override)
    assert result == {"db": {"host": "localhost", "port": 3306, "name": "mydb"}}


def test_three_level_deep_merge() -> None:
    """Three levels of nesting merge correctly."""
    base = {"a": {"b": {"c": 1, "d": 2}}}
    override = {"a": {"b": {"d": 3, "e": 4}}}
    result = deep_merge(base, override)
    assert result == {"a": {"b": {"c": 1, "d": 3, "e": 4}}}


# --- Lists replaced, not appended ---


def test_list_replaced() -> None:
    """Lists in override replace base lists entirely."""
    result = deep_merge({"tags": [1, 2, 3]}, {"tags": [4, 5]})
    assert result == {"tags": [4, 5]}


def test_list_replaced_with_empty() -> None:
    """Override list can be empty, replacing a non-empty base list."""
    result = deep_merge({"items": [1, 2]}, {"items": []})
    assert result == {"items": []}


# --- None as regular value ---


def test_none_overrides_value() -> None:
    """None in override replaces a non-None base value."""
    result = deep_merge({"a": 1}, {"a": None})
    assert result == {"a": None}


def test_none_overridden_by_value() -> None:
    """A value in override replaces None in base."""
    result = deep_merge({"a": None}, {"a": 42})
    assert result == {"a": 42}


# --- Mixed types: dict + non-dict ---


def test_dict_overridden_by_scalar() -> None:
    """When base has a dict and override has a scalar, override wins."""
    result = deep_merge({"a": {"nested": True}}, {"a": "flat"})
    assert result == {"a": "flat"}


def test_scalar_overridden_by_dict() -> None:
    """When base has a scalar and override has a dict, override wins."""
    result = deep_merge({"a": "flat"}, {"a": {"nested": True}})
    assert result == {"a": {"nested": True}}


# --- Empty dicts ---


def test_both_empty() -> None:
    """Merging two empty dicts produces an empty dict."""
    result = deep_merge({}, {})
    assert result == {}


def test_empty_base() -> None:
    """Empty base returns a copy of override."""
    override = {"x": 1, "y": {"z": 2}}
    result = deep_merge({}, override)
    assert result == {"x": 1, "y": {"z": 2}}


def test_empty_override() -> None:
    """Empty override returns a copy of base."""
    base = {"x": 1, "y": {"z": 2}}
    result = deep_merge(base, {})
    assert result == {"x": 1, "y": {"z": 2}}


# --- No mutation of inputs ---


def test_base_not_mutated() -> None:
    """The base dict is not modified in place."""
    base = {"a": 1, "nested": {"b": 2}}
    base_snapshot = copy.deepcopy(base)
    deep_merge(base, {"a": 99, "nested": {"c": 3}})
    assert base == base_snapshot


def test_override_not_mutated() -> None:
    """The override dict is not modified in place."""
    override = {"a": 99, "nested": {"c": 3}}
    override_snapshot = copy.deepcopy(override)
    deep_merge({"a": 1, "nested": {"b": 2}}, override)
    assert override == override_snapshot


# --- Independent copies in result ---


def test_result_nested_dict_is_independent_copy() -> None:
    """Modifying a nested dict in the result does not affect the originals."""
    base = {"config": {"debug": False}}
    override = {"config": {"verbose": True}}
    result = deep_merge(base, override)

    # Mutate result
    result["config"]["debug"] = True
    result["config"]["verbose"] = False

    # Originals unchanged
    assert base["config"]["debug"] is False
    assert override["config"]["verbose"] is True


def test_result_list_is_independent_copy() -> None:
    """Modifying a list in the result does not affect the override source."""
    override = {"items": [1, 2, 3]}
    result = deep_merge({}, override)

    result["items"].append(999)
    assert override["items"] == [1, 2, 3]
