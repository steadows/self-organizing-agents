# Task 001: slugify

## Function Signature

```python
def slugify(text: str, separator: str = "-", max_length: int = 200) -> str:
```

## Description

Convert an arbitrary Unicode string into a URL-safe ASCII slug. Unicode characters are transliterated to their closest ASCII equivalents (e.g., `u` for `ü`, `n` for `ñ`), all letters are lowercased, and runs of non-alphanumeric characters are collapsed into a single separator. The result is trimmed to `max_length`, truncating at a word boundary when possible.

## Requirements

- Use `unicodedata.normalize("NFKD", text)` and encode to ASCII with `"ignore"` to transliterate Unicode characters to ASCII approximations.
- Lowercase the entire string.
- Replace any run of one or more non-alphanumeric characters with a single `separator`.
- Strip leading and trailing separators from the result.
- If the result exceeds `max_length`, truncate. Prefer truncating at the last separator boundary within the limit; if no separator exists within the limit, hard-truncate at `max_length`.
- After truncation, strip any trailing separator.
- No external dependencies beyond the Python standard library (`unicodedata`, `re`).

## Edge Cases

- Empty string input `""` returns `""`.
- Input containing only special characters (e.g., `"@#$%^&*"`) returns `""`.
- Input containing only whitespace returns `""`.
- A single valid word returns that word lowercased with no surrounding separators.
- `max_length=0` returns `""`.
- Input already ASCII and slug-safe is returned as-is (lowercased).
- Multiple consecutive separators in the input collapse to one.

## Examples

| Input | Output |
|---|---|
| `"Hello World!"` | `"hello-world"` |
| `"Héllo Wörld"` | `"hello-world"` |
| `"  --foo--bar--baz--  "` | `"foo-bar-baz"` |
| `""` | `""` |
| `"@#$%^&*()"` | `""` |
| `"Ñoño año español"` | `"nono-ano-espanol"` |
| `"über cool café"` | `"uber-cool-cafe"` |
| `slugify("a-very-long-slug " * 20, max_length=20)` | `"a-very-long-slug"` (truncated at word boundary, 16 chars) |

## Scope Boundary

- NO full ICU/CLDR transliteration (e.g., `ß` → `ss` is NOT required; NFKD decomposition is sufficient).
- NO custom character mapping tables.
- NO support for non-default separators beyond the parameter (the experiment uses `"-"` only).
- NO language-specific transliteration rules.
