"""Tests for parse_rfc3339_utc(): the fix for get_free_busy() raising ValueError on any
Google Calendar timestamp carrying fractional seconds (observed against a contract-accurate
Calendar twin returning '...T17:52:58.000Z').
"""

from datetime import datetime

from hypothesis import given, strategies as st

from appointment.controller.apis.google_client import parse_rfc3339_utc


class TestFreeBusyTimestampParsing:
    def test_whole_seconds(self):
        assert parse_rfc3339_utc('2026-01-15T10:30:00Z') == datetime(2026, 1, 15, 10, 30, 0)

    def test_fractional_seconds(self):
        assert parse_rfc3339_utc('2026-01-15T17:52:58.000Z') == datetime(2026, 1, 15, 17, 52, 58)

    def test_offset_is_normalized_to_naive_utc(self):
        result = parse_rfc3339_utc('2026-01-15T12:30:00+02:00')
        assert result == datetime(2026, 1, 15, 10, 30, 0)
        assert result.tzinfo is None


@st.composite
def rfc3339_utc_strings(draw):
    dt = draw(st.datetimes(min_value=datetime(1990, 1, 1), max_value=datetime(2100, 1, 1)))
    suffix = draw(st.sampled_from(['Z', '.000Z', '.123456Z', '+00:00']))
    return dt, dt.isoformat() + suffix if suffix != '+00:00' else dt.isoformat() + '+00:00'


class TestFreeBusyTimestampParsingProperties:
    @given(rfc3339_utc_strings())
    def test_well_formed_strings_round_trip_to_naive_utc(self, dt_and_string):
        dt, value = dt_and_string
        result = parse_rfc3339_utc(value)
        assert result.tzinfo is None
        assert result.replace(microsecond=0) == dt.replace(microsecond=0)

    @given(st.text())
    def test_arbitrary_text_either_parses_or_raises_a_known_exception(self, value):
        try:
            result = parse_rfc3339_utc(value)
        except (ValueError, TypeError):
            return
        assert isinstance(result, datetime)
        assert result.tzinfo is None
