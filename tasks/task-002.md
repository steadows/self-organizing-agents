# Task 002: validate_email

## Function Signature

```python
def validate_email(email: str) -> bool:
```

## Description

Validate that a string looks like a common email address. This covers the practical subset of email formats seen in real-world usage: a local part, an `@` symbol, and a domain with at least one dot and a TLD of two or more characters. It intentionally does not cover the full RFC 5321 specification.

## Requirements

- The input must contain exactly one `@` character, splitting the string into a local part and a domain part.
- **Local part rules:**
  - Allowed characters: ASCII alphanumeric, `.`, `_`, `%`, `+`, `-`.
  - Must be at least 1 character long.
  - Cannot start or end with a dot (`.`).
  - Cannot contain consecutive dots (`..`).
- **Domain part rules:**
  - Allowed characters: ASCII alphanumeric and hyphens (`-`).
  - Must contain at least one dot (`.`) separating labels.
  - Each label must be at least 1 character long.
  - No label may start or end with a hyphen.
  - The TLD (final label after the last dot) must be at least 2 alphabetic characters.
- Return `True` if valid, `False` otherwise.
- No external dependencies; use only the `re` module or plain string operations.

## Edge Cases

- Empty string `""` returns `False`.
- Missing `@` returns `False`.
- Multiple `@` characters returns `False`.
- Local part is empty (e.g., `"@example.com"`) returns `False`.
- Domain has no dot (e.g., `"user@localhost"`) returns `False`.
- TLD is a single character (e.g., `"user@example.c"`) returns `False`.
- Very long but valid email (254 chars total) returns `True`.
- Email exceeding 254 characters returns `False`.

## Examples

### Valid

| Input | Result |
|---|---|
| `"user@example.com"` | `True` |
| `"first.last@sub.domain.co.uk"` | `True` |
| `"user+tag@gmail.com"` | `True` |
| `"a@b.co"` | `True` |
| `"test_user%special@my-domain.org"` | `True` |
| `"123@456.com"` | `True` |

### Invalid

| Input | Result |
|---|---|
| `""` | `False` |
| `"plainaddress"` | `False` |
| `"@no-local.com"` | `False` |
| `"user@.leading-dot.com"` | `False` |
| `".leading@example.com"` | `False` |
| `"trailing.@example.com"` | `False` |
| `"double..dot@example.com"` | `False` |
| `"user@-hyphen-start.com"` | `False` |
| `"user@domain.c"` | `False` |
| `"user@@double.com"` | `False` |

## Scope Boundary

- NOT an RFC 5321 or RFC 5322 compliant validator.
- NO support for quoted local parts (e.g., `"user name"@example.com`).
- NO support for IP address literals in the domain (e.g., `user@[192.168.1.1]`).
- NO support for comments in the address.
- NO DNS or MX record verification.
- NO internationalized email addresses (EAI/RFC 6531).
