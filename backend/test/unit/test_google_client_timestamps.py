"""Tests for parse_rfc3339_utc(): the fix for get_free_busy() raising ValueError on any
Google Calendar timestamp carrying fractional seconds (observed against a contract-accurate
Calendar twin returning '...T17:52:58.000Z').
"""

import pytest
from datetime import datetime

from appointment.controller.apis.google_client import parse_rfc3339_utc


class TestFreeBusyTimestampParsing:
    @pytest.mark.parametrize(
        'value, expected',
        [
            ('2026-01-15T10:30:00Z', datetime(2026, 1, 15, 10, 30, 0)),  # whole seconds
            ('2026-01-15T17:52:58.000Z', datetime(2026, 1, 15, 17, 52, 58)),  # zero-padded fractional
            ('2026-01-15T17:52:58.123456Z', datetime(2026, 1, 15, 17, 52, 58, 123456)),  # microsecond precision
            ('2026-01-15T12:30:00+02:00', datetime(2026, 1, 15, 10, 30, 0)),  # positive offset
            ('2026-01-15T12:30:00-05:00', datetime(2026, 1, 15, 17, 30, 0)),  # negative offset
        ],
    )
    def test_well_formed_strings_round_trip_to_naive_utc(self, value, expected):
        result = parse_rfc3339_utc(value)
        assert result.tzinfo is None
        assert result == expected

    @pytest.mark.parametrize(
        'value',
        [
            '',  # empty string
            'not-a-date',  # arbitrary text
            None,  # wrong type entirely
            123,  # wrong type entirely
            '2026-13-45T99:99:99Z',  # well-formed shape, out-of-range components
            '2026/01/15T10:30:00Z',  # wrong separator, matches neither format
        ],
    )
    def test_malformed_input_raises(self, value):
        with pytest.raises((ValueError, TypeError)):
            parse_rfc3339_utc(value)
