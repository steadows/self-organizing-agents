"""Utility for recursively merging two dictionaries without mutation."""

import copy
from typing import Any


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge two dictionaries, with override taking precedence.

    Produces a new dictionary where values from ``override`` take precedence
    over ``base``. When both dictionaries contain a dict at the same key, the
    merge recurses into those sub-dicts. Neither input dictionary is mutated.

    Args:
        base: The base dictionary providing default values.
        override: The dictionary whose values take precedence.

    Returns:
        A new, fully independent dictionary containing the merged result.
    """
    result: dict[str, Any] = {}

    for key in base:
        if key in override:
            base_val = base[key]
            override_val = override[key]
            if isinstance(base_val, dict) and isinstance(override_val, dict):
                result[key] = deep_merge(base_val, override_val)
            else:
                result[key] = copy.deepcopy(override_val)
        else:
            result[key] = copy.deepcopy(base[key])

    for key in override:
        if key not in base:
            result[key] = copy.deepcopy(override[key])

    return result
