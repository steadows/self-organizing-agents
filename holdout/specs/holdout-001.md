# Holdout Task 001: parse_duration

## Function Signature

```python
def parse_duration(text: str) -> int:
```

## Description

Parse a human-readable duration string like `"2h30m10s"` into a total number of integer seconds. The function supports hours (`h`), minutes (`m`), and seconds (`s`) unit suffixes in any order. Parsing is case-insensitive.

## Requirements

- Accept strings containing one or more `<integer><unit>` pairs, where unit is `h`, `m`, or `s`.
- Units can appear in any order (e.g., `"10s2h"` is valid and equals `7210`).
- Each unit may appear at most once. Duplicate units raise `ValueError`.
- Case-insensitive: `"2H30M"` is equivalent to `"2h30m"`.
- Only non-negative integer values are accepted for each component.
- Negative values (e.g., `"-1h"`) raise `ValueError`.
- Empty string raises `ValueError`.
- Strings with no valid `<integer><unit>` pairs raise `ValueError`.
- Non-numeric values before a unit suffix (e.g., `"abch"`) raise `ValueError`.
- Strings containing characters that are not digits or unit letters raise `ValueError`.
- Return type is always `int`.

## Edge Cases

- `"0s"` returns `0`.
- `"0h0m0s"` returns `0`.
- `"1h"` returns `3600` (missing units default to 0).
- `"90s"` returns `90` (values above 59 for seconds/minutes are allowed, no normalization).
- `""` raises `ValueError`.
- `"2h2h"` raises `ValueError` (duplicate unit).
- `"-5m"` raises `ValueError` (negative value).
- `"2.5h"` raises `ValueError` (decimal values not supported).
- `"hello"` raises `ValueError`.
- `"2h 30m"` raises `ValueError` (spaces are not allowed).
- `"2d"` raises `ValueError` (unsupported unit).

## Examples

```python
parse_duration("2h30m10s")   # => 9010
parse_duration("1h")         # => 3600
parse_duration("45m")        # => 2700
parse_duration("90s")        # => 90
parse_duration("0s")         # => 0
parse_duration("1H30M")      # => 5400
parse_duration("10s2h")      # => 7210
parse_duration("0h0m0s")     # => 0
parse_duration("100m")       # => 6000
parse_duration("")           # => ValueError
parse_duration("2h2h")       # => ValueError
parse_duration("-5m")        # => ValueError
parse_duration("abc")        # => ValueError
```

## Scope Boundary

- NO support for days, weeks, months, or years.
- NO decimal/float values (integers only).
- NO ISO 8601 duration format (e.g., `"PT2H30M"`).
- NO whitespace tolerance within the string.
- NO localization or alternate unit names (e.g., "hours", "min").
