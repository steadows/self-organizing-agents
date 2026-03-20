"""Parse human-readable duration strings into total seconds."""

import re

UNIT_MULTIPLIERS: dict[str, int] = {
    "h": 3600,
    "m": 60,
    "s": 1,
}

_VALID_CHARS = re.compile(r"^[0-9hmsHMS]+$")
_TOKEN_PATTERN = re.compile(r"(\d+)([hmsHMS])")


def parse_duration(text: str) -> int:
    """Parse a duration string like '2h30m10s' into total seconds.

    Accepts strings containing one or more ``<integer><unit>`` pairs where
    unit is ``h`` (hours), ``m`` (minutes), or ``s`` (seconds).  Units may
    appear in any order and parsing is case-insensitive.

    Args:
        text: The duration string to parse (e.g. ``"2h30m10s"``).

    Returns:
        Total number of seconds as an integer.

    Raises:
        ValueError: If *text* is empty, contains invalid characters,
            duplicate units, negative/decimal values, or unsupported units.
    """
    if not text:
        raise ValueError("Duration string must not be empty")

    # Reject strings with spaces, negative signs, decimals, or other invalid chars
    if not _VALID_CHARS.match(text):
        raise ValueError(f"Invalid characters in duration string: {text!r}")

    tokens = _TOKEN_PATTERN.findall(text)
    if not tokens:
        raise ValueError(f"No valid <integer><unit> pairs found in: {text!r}")

    # Verify the tokens fully consume the input (no leftover chars like bare digits)
    reconstructed = "".join(value + unit for value, unit in tokens)
    if reconstructed.lower() != text.lower():
        raise ValueError(f"Unexpected content in duration string: {text!r}")

    seen_units: set[str] = set()
    total_seconds = 0

    for value_str, unit in tokens:
        unit_lower = unit.lower()
        if unit_lower in seen_units:
            raise ValueError(f"Duplicate unit '{unit_lower}' in: {text!r}")
        seen_units.add(unit_lower)
        total_seconds += int(value_str) * UNIT_MULTIPLIERS[unit_lower]

    return total_seconds
