"""Utility for recursively merging two dictionaries."""

import copy
from typing import Any


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge two dictionaries, with override values taking precedence.

    Produces a new dictionary containing all keys from both `base` and `override`.
    When both contain a dict at the same key, the merge recurses into those sub-dicts.
    Neither input dictionary is mutated. The result is a fully independent copy.

    Parameters
    ----------
    base:
        The base dictionary supplying default values.
    override:
        The dictionary whose values take precedence over `base`.

    Returns
    -------
    dict
        A new merged dictionary independent of both inputs.

    Raises
    ------
    ValueError
        If either `base` or `override` is not a dict.

    Examples
    --------
    >>> deep_merge({"a": 1}, {"b": 2})
    {'a': 1, 'b': 2}

    >>> deep_merge(
    ...     {"db": {"host": "localhost", "port": 5432}},
    ...     {"db": {"port": 3306, "name": "mydb"}},
    ... )
    {'db': {'host': 'localhost', 'port': 3306, 'name': 'mydb'}}
    """
    if not isinstance(base, dict):
        raise ValueError(f"'base' must be a dict, got {type(base).__name__}")
    if not isinstance(override, dict):
        raise ValueError(f"'override' must be a dict, got {type(override).__name__}")

    result: dict[str, Any] = copy.deepcopy(base)

    for key, override_value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(override_value, dict):
            result[key] = deep_merge(result[key], override_value)
        else:
            result[key] = copy.deepcopy(override_value)

    return result
