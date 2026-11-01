"""Parse ISO 8601 timestamps with optional fractional seconds and UTC offset.

The parser is deliberately strict: it accepts the subset of ISO 8601 that
unambiguously denotes an instant, and rejects everything else.  Ambiguous
strings (such as a bare date, or a time without an offset) raise
:class:`ValueError` rather than silently guessing a timezone, because a
silent guess is the kind of bug that only shows up in production.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final

__all__ = ["Timestamp", "parse_timestamp"]

# The grammar is intentionally narrow.  We require:
#   * a four-digit year, two-digit month and two-digit day
#   * a 'T' separator (case-insensitive)
#   * two-digit hour, minute and second
#   * an optional fractional part introduced by '.' or ','
#   * a mandatory UTC designator: 'Z' or +/-HH:MM
#
# We do not accept a missing offset because that makes the string ambiguous:
# the same wall-clock time means different instants in different zones.
_TIMESTAMP_RE: Final = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"[Tt]"
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?:[.,](?P<fraction>\d+))?"
    r"(?P<offset>Z|[+-]\d{2}:\d{2})$"
)


def _parse_offset(raw: str) -> timezone:
    """Turn the offset capture group into a :class:`datetime.timezone`.

    ``Z`` is handled explicitly because it is the only named zone we accept;
    numeric offsets are parsed by hand so we can validate the minute range
    ourselves (the regex only checks the shape).
    """
    if raw == "Z":
        return timezone.utc

    sign = 1 if raw[0] == "+" else -1
    hours = int(raw[1:3])
    minutes = int(raw[4:6])
    if hours > 23 or minutes > 59:
        raise ValueError(f"invalid UTC offset: {raw!r}")
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


def _parse_fraction(raw: str | None) -> int:
    """Convert a fractional-second string to microseconds.

    ISO 8601 allows an arbitrary number of digits, but Python's
    :class:`datetime` only stores microseconds.  We truncate rather than
    round: truncation is the behaviour of most timestamp libraries and is
    the only choice that is monotonic with respect to the input string.
    """
    if raw is None:
        return 0
    # Pad or truncate to exactly six digits.
    digits = (raw + "000000")[:6]
    return int(digits)


@dataclass(frozen=True)
class Timestamp:
    """An immutable instant parsed from an ISO 8601 string.

    Wrapping :class:`datetime.datetime` gives callers a stable type to
    annotate against, and keeps the parsing helpers private.  The wrapped
    datetime is always timezone-aware and normalised to UTC, so comparisons
    and arithmetic between two :class:`Timestamp` values are unambiguous.
    """

    datetime: datetime

    def __post_init__(self) -> None:
        if self.datetime.tzinfo is None:
            raise ValueError("Timestamp requires a timezone-aware datetime")

    @property
    def utc(self) -> datetime:
        """Return the instant as a UTC-aware :class:`datetime.datetime`."""
        return self.datetime.astimezone(timezone.utc)

    def isoformat(self) -> str:
        """Return the instant in canonical ISO 8601 form (UTC, 'Z' suffix)."""
        return self.utc.isoformat().replace("+00:00", "Z")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timestamp):
            return NotImplemented
        return self.utc == other.utc

    def __hash__(self) -> int:
        return hash(self.utc)


def parse_timestamp(value: str) -> Timestamp:
    """Parse an ISO 8601 timestamp into a :class:`Timestamp`.

    The accepted form is ``YYYY-MM-DDTHH:MM:SS[.ffffff](Z|+HH:MM|-HH:MM)``.
    Both ``T`` and ``t`` are accepted as the date/time separator, and both
    ``.`` and ``,`` are accepted as the fractional-second separator, matching
    the ISO 8601 standard.  Anything else raises :class:`ValueError`.

    The returned object is normalised to UTC; callers that need the original
    offset should keep the input string.
    """
    if not isinstance(value, str):
        raise ValueError(f"timestamp must be a string, got {type(value).__name__}")

    match = _TIMESTAMP_RE.match(value)
    if match is None:
        raise ValueError(f"not an ISO 8601 timestamp: {value!r}")

    parts = match.groupdict()
    try:
        year = int(parts["year"])
        month = int(parts["month"])
        day = int(parts["day"])
        hour = int(parts["hour"])
        minute = int(parts["minute"])
        second = int(parts["second"])
        microsecond = _parse_fraction(parts["fraction"])
        tz = _parse_offset(parts["offset"])
        dt = datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=tz
        )
    except ValueError as exc:
        # Re-raise with the original string so the caller can see what failed.
        raise ValueError(f"invalid timestamp {value!r}: {exc}") from exc

    return Timestamp(dt)
