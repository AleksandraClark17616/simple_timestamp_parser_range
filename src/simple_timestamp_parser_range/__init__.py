"""Public API for simple_timestamp_parser_range.

Only :func:`parse_timestamp` and :class:`Timestamp` are exported; the
implementation lives in :mod:`simple_timestamp_parser_range.core` so the
package namespace stays small and stable.
"""

from .core import Timestamp, parse_timestamp

__all__ = ["Timestamp", "parse_timestamp"]
