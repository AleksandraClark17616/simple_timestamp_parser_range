# simple_timestamp_parser_range

Parse ISO 8601 timestamps that include an explicit UTC offset, returning an
immutable `Timestamp` normalised to UTC.

```python
from simple_timestamp_parser_range import parse_timestamp

ts = parse_timestamp("2024-01-02T03:04:05.5+02:00")
print(ts.isoformat())  # 2024-01-02T01:04:05.500000Z
```

## Why this exists

Most timestamp parsers are either too permissive (accepting a bare date or a
time with no offset, then guessing a timezone) or too rigid (rejecting the
comma fractional separator that ISO 8601 explicitly allows).  This library
picks one strict interpretation: the string must name an instant, which means
it must carry a UTC offset.  A missing offset raises `ValueError` instead of
silently defaulting to local time.  The trade-off is that you cannot parse a
local wall-clock time with this function; if you need that, resolve the
ambiguity in your own code before calling `parse_timestamp`.

## API

- `parse_timestamp(value: str) -> Timestamp`
- `Timestamp.datetime` — the wrapped, timezone-aware `datetime`
- `Timestamp.utc` — the instant as a UTC-aware `datetime`
- `Timestamp.isoformat()` — canonical ISO 8601 string with a `Z` suffix

The accepted grammar is `YYYY-MM-DDTHH:MM:SS[.ffffff](Z|+HH:MM|-HH:MM)`.
Both `T`/`t` and `.`/`,` are accepted as separators, matching ISO 8601.
Fractional seconds beyond six digits are truncated, not rounded.

## Awkward edge

Equality and hashing are based on the instant, not the original offset, so
`2024-01-02T03:04:05Z` and `2024-01-02T05:04:05+02:00` compare equal.  If you
need to preserve the original offset, keep the input string alongside the
`Timestamp`.
