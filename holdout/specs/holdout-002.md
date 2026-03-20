# Holdout Task 002: deep_merge

## Function Signature

```python
def deep_merge(base: dict, override: dict) -> dict:
```

## Description

Recursively merge two dictionaries, producing a new dictionary where values from `override` take precedence over `base`. When both `base` and `override` contain a dict at the same key, the merge recurses into those sub-dicts. Neither input dictionary is mutated.

## Requirements

- Return a new dictionary containing all keys from both `base` and `override`.
- When a key exists only in `base`, its value appears in the result.
- When a key exists only in `override`, its value appears in the result.
- When a key exists in both and both values are dicts, merge them recursively.
- When a key exists in both and the values are NOT both dicts, the `override` value wins (regardless of types).
- Lists are replaced wholesale by `override`, never appended or merged element-wise.
- `None` is treated as a regular value, not as a sentinel for "missing" or "delete".
- Neither `base` nor `override` may be mutated. The result must be a fully independent copy.
- Nested dicts in the result must also be independent copies (not references to input sub-dicts).

## Edge Cases

- Both inputs are empty dicts: returns `{}`.
- `base` is empty: returns a deep copy of `override`.
- `override` is empty: returns a deep copy of `base`.
- `override` sets a key to `None`: result has `None` at that key (does not delete or skip).
- `base` has a dict at key `"x"` and `override` has a non-dict (e.g., `int`) at key `"x"`: the `int` from `override` wins.
- `base` has a non-dict at key `"x"` and `override` has a dict at key `"x"`: the dict from `override` wins.
- Nested merge at 3+ levels deep works correctly.
- Lists at the same key are replaced, not concatenated.

## Examples

```python
# Basic merge, no overlap
deep_merge({"a": 1}, {"b": 2})
# => {"a": 1, "b": 2}

# Override replaces scalar
deep_merge({"a": 1}, {"a": 2})
# => {"a": 2}

# Recursive dict merge
deep_merge(
    {"db": {"host": "localhost", "port": 5432}},
    {"db": {"port": 3306, "name": "mydb"}}
)
# => {"db": {"host": "localhost", "port": 3306, "name": "mydb"}}

# 3-level deep merge
deep_merge(
    {"a": {"b": {"c": 1, "d": 2}}},
    {"a": {"b": {"d": 3, "e": 4}}}
)
# => {"a": {"b": {"c": 1, "d": 3, "e": 4}}}

# Lists are replaced, not appended
deep_merge({"tags": [1, 2, 3]}, {"tags": [4, 5]})
# => {"tags": [4, 5]}

# None is a regular value
deep_merge({"a": 1}, {"a": None})
# => {"a": None}

# Mixed types at same key — override wins
deep_merge({"a": {"nested": True}}, {"a": "flat_string"})
# => {"a": "flat_string"}

# Empty dicts
deep_merge({}, {"a": 1})
# => {"a": 1}

# No mutation — original base unchanged
base = {"a": {"b": 1}}
override = {"a": {"c": 2}}
result = deep_merge(base, override)
# result => {"a": {"b": 1, "c": 2}}
# base   => {"a": {"b": 1}}  (unchanged)
```

## Scope Boundary

- NO list merging strategies (lists are always replaced).
- NO special handling of `None` (it is a normal value).
- NO circular reference detection.
- NO support for merging non-dict types at the top level (both inputs must be dicts).
- NO deep merge of objects other than plain dicts (e.g., dataclasses, custom mappings).
