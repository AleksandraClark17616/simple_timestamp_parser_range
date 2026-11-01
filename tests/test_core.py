import unittest

from simple_timestamp_parser_range import Timestamp, parse_timestamp


class ParseTimestampTests(unittest.TestCase):
    def test_utc_designator(self):
        ts = parse_timestamp("2024-01-02T03:04:05Z")
        self.assertEqual(ts.isoformat(), "2024-01-02T03:04:05Z")

    def test_positive_offset_is_normalised_to_utc(self):
        ts = parse_timestamp("2024-01-02T03:04:05+02:00")
        self.assertEqual(ts.isoformat(), "2024-01-02T01:04:05Z")

    def test_negative_offset_is_normalised_to_utc(self):
        ts = parse_timestamp("2024-01-02T03:04:05-05:30")
        self.assertEqual(ts.isoformat(), "2024-01-02T08:34:05Z")

    def test_fractional_seconds_are_truncated_to_microseconds(self):
        ts = parse_timestamp("2024-01-02T03:04:05.123456789Z")
        self.assertEqual(ts.isoformat(), "2024-01-02T03:04:05.123456Z")

    def test_fractional_seconds_shorter_than_six_digits_are_padded(self):
        ts = parse_timestamp("2024-01-02T03:04:05.5Z")
        self.assertEqual(ts.isoformat(), "2024-01-02T03:04:05.500000Z")

    def test_comma_is_accepted_as_fraction_separator(self):
        ts = parse_timestamp("2024-01-02T03:04:05,25Z")
        self.assertEqual(ts.isoformat(), "2024-01-02T03:04:05.250000Z")

    def test_lowercase_t_separator_is_accepted(self):
        ts = parse_timestamp("2024-01-02t03:04:05Z")
        self.assertEqual(ts.isoformat(), "2024-01-02T03:04:05Z")

    def test_equality_compares_instants_not_offsets(self):
        a = parse_timestamp("2024-01-02T03:04:05Z")
        b = parse_timestamp("2024-01-02T05:04:05+02:00")
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_rejects_missing_offset(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02T03:04:05")

    def test_rejects_bare_date(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02")

    def test_rejects_out_of_range_month(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-13-02T03:04:05Z")

    def test_rejects_out_of_range_offset_minutes(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02T03:04:05+02:60")

    def test_rejects_non_string_input(self):
        with self.assertRaises(ValueError):
            parse_timestamp(20240102)  # type: ignore[arg-type]


class TimestampTests(unittest.TestCase):
    def test_requires_timezone_aware_datetime(self):
        from datetime import datetime

        with self.assertRaises(ValueError):
            Timestamp(datetime(2024, 1, 2, 3, 4, 5))

    def test_utc_property_returns_utc_datetime(self):
        ts = parse_timestamp("2024-01-02T03:04:05+02:00")
        self.assertEqual(ts.utc.isoformat(), "2024-01-02T01:04:05+00:00")


if __name__ == "__main__":
    unittest.main()
