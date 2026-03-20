"""Utility for parsing human-readable duration strings into total seconds."""

import re

UNIT_SECONDS = {"h": 3600, "m": 60, "s": 1}
VALID_PATTERN = re.compile(r"^(\d+[hmsHMS])+$")
TOKEN_PATTERN = re.compile(r"(\d+)([hmsHMS])")


def parse_duration(text: str) -> int:
    """Parse a human-readable duration string into a total number of seconds.

    Accepts strings containing one or more ``<integer><unit>`` pairs where unit
    is ``h`` (hours), ``m`` (minutes), or ``s`` (seconds).  Units may appear in
    any order and the string is parsed case-insensitively.

    Parameters
    ----------
    text:
        Duration string such as ``"2h30m10s"`` or ``"10s2h"``.

    Returns
    -------
    int
        Total duration expressed in seconds.

    Raises
    ------
    ValueError
        If *text* is empty, contains unsupported characters, uses unsupported
        units, contains duplicate units, contains negative values, or has no
        valid ``<integer><unit>`` pairs.

    Examples
    --------
    >>> parse_duration("2h30m10s")
    9010
    >>> parse_duration("1H30M")
    5400
    >>> parse_duration("90s")
    90
    """
    if not text:
        raise ValueError("Duration string must not be empty.")

    if not VALID_PATTERN.match(text):
        raise ValueError(
            f"Invalid duration string {text!r}. "
            "Only digits and unit letters h, m, s are allowed (no spaces, "
            "decimals, or unsupported units)."
        )

    tokens = TOKEN_PATTERN.findall(text)
    seen_units: set[str] = set()
    total = 0

    for raw_value, raw_unit in tokens:
        unit = raw_unit.lower()
        if unit in seen_units:
            raise ValueError(
                f"Duplicate unit {raw_unit!r} found in duration string {text!r}."
            )
        seen_units.add(unit)
        total += int(raw_value) * UNIT_SECONDS[unit]

    return total
