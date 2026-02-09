import datetime
from datetime import time
from unittest.mock import MagicMock

from freezegun import freeze_time

from appointment.database import schemas
from appointment.database.models import IsoWeekday
from appointment.routes.schedule import is_this_a_valid_booking_time
from appointment.utils import retrieve_user_url_data


class TestRetrieveUserUrlData:
    def test_success(self):
        original_username = 'mycoolusername'
        original_signature = 'hello-world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature == signature
        assert original_clean_url == clean_url

    def test_success_with_extra_slashes(self):
        original_username = 'mycoolusername'
        original_signature = 'hello-world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}////////////////////////'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature == signature
        assert original_clean_url == clean_url

    def test_success_with_uriencoded_signature(self):
        original_username = 'mycoolusername'
        original_signature = 'hello%20world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature != signature
        assert 'hello world' == signature
        assert original_clean_url == clean_url

    def test_failure(self):
        original_username = 'mycoolusername'
        original_signature = 'hello world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}/other-junk/'

        assert not retrieve_user_url_data(url)


class TestIsAValidBookingTime:
    def test_bug_735(self, make_schedule):
        """A test case to cover unsuccessfully capturing bug 735, which is the seemingly random slot not found issue.
        Ref: https://github.com/thunderbird/appointment/issues/735"""
        # Request data submitted from bug and anonymized.
        request_data = {
            's_a': {
                'attendee': {'email': 'email@example.org', 'name': 'Email Example', 'timezone': 'Europe/London'},
                'slot': {'duration': 45, 'start': '2024-11-11T17:00:00.000Z'},
            },
            'url': 'https://appointment.day/user/fake/example/',
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])

        schedule = make_schedule(
            active=True,
            start_date=datetime.date(2024, 11, 1),
            end_date=None,
            earliest_booking=2880,
            farthest_booking=10080,
            weekdays=[1, 2, 3, 4, 5],
            slot_duration=45,
            start_time=16,  # 9AM PDT
            end_time=0,  # 5PM PDT
            timezone='America/Vancouver',
            # This is not accurate, but it was probably saved before Nov 3rd.
            time_updated=datetime.datetime(2024, 11, 1, 12, 0, 0, tzinfo=datetime.UTC),
        )

        # Freeze on the datetime that the error occurred on
        with freeze_time('2024-11-04T09:09:29.530Z'):
            is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)

        assert is_valid is True

    def test_bug_735_case_2(self, make_schedule):
        """A test case to cover successfully capturing bug 735, which is the seemingly random slot not found issue.
        Ref: https://github.com/thunderbird/appointment/issues/735"""
        # Request data submitted from bug and anonymized.
        request_data = {
            's_a': {
                'slot': {'start': '2024-11-17T22:00:00.000Z', 'duration': 30},
                'attendee': {'name': 'melissa', 'email': 'melissa@example.org', 'timezone': 'Australia/Sydney'},
            },
            'url': 'http://localhost:8080/user/username/example/',
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])

        schedule = make_schedule(
            active=True,
            start_date=datetime.date(2024, 11, 7),
            end_date=None,
            earliest_booking=0,
            farthest_booking=10080,
            weekdays=[1, 2, 3, 4, 5],
            slot_duration=30,
            start_time='22:00',  # 9AM AEDT
            end_time='06:00',  # 5PM AEDT
            timezone='Australia/Sydney',
            time_updated=datetime.datetime(2024, 11, 15, 12, 0, 0, tzinfo=datetime.UTC),
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)

        assert is_valid is True

    def test_pst_to_pdt_change(self, make_schedule):
        request_data = {
            's_a': {
                'slot': {'start': '2025-03-11T16:00:00.000Z', 'duration': 30},
                'attendee': {'name': 'melissa', 'email': 'melissa@example.org', 'timezone': 'America/Vancouver'},
            },
            'url': 'http://localhost:8080/user/username/example/',
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])

        schedule = make_schedule(
            active=True,
            start_date=datetime.date(2025, 2, 5),
            end_date=None,
            earliest_booking=0,
            farthest_booking=10080,
            weekdays=[1, 2, 3, 4, 5],
            slot_duration=30,
            start_time='17:00',  # 9AM PST
            end_time='01:00',  # 5PM PST
            timezone='America/Vancouver',
            time_updated=datetime.datetime(2025, 2, 5, 20, 8, 29, tzinfo=datetime.UTC),
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid


class TestIsAValidBookingTimeWithCustomAvailability:
    """Tests for is_this_a_valid_booking_time with custom availabilities enabled.

    These tests use fully mocked schedule objects since we're testing validation logic,
    not database integration. This avoids SQLAlchemy relationship issues.
    """

    @staticmethod
    def _make_mock_availability(day_of_week: int, start_time: time, end_time: time, time_updated: datetime.datetime):
        """Create a mock availability object."""
        avail = MagicMock()
        avail.day_of_week = IsoWeekday(day_of_week)
        avail.start_time = start_time
        avail.end_time = end_time
        avail.time_updated = time_updated
        return avail

    @staticmethod
    def _make_mock_schedule(
        weekdays: list[int],
        slot_duration: int,
        start_time: time,
        end_time: time,
        timezone: str,
        time_updated: datetime.datetime,
        use_custom_availabilities: bool = True,
        availabilities: list = None,
    ):
        """Create a mock schedule object with the necessary properties."""
        import zoneinfo

        schedule = MagicMock()
        schedule.weekdays = weekdays
        schedule.slot_duration = slot_duration
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.timezone = timezone
        schedule.time_updated = time_updated
        schedule.use_custom_availabilities = use_custom_availabilities
        schedule.availabilities = availabilities or []

        # Mock the timezone_offset property
        schedule.timezone_offset = time_updated.replace(
            tzinfo=zoneinfo.ZoneInfo(timezone)
        ).utcoffset()

        return schedule

    def test_custom_availability_booking_within_range(self):
        """Booking within a custom availability time range should be valid."""
        # Tuesday 2025-02-11 at 10:00 AM PST (18:00 UTC)
        request_data = {
            's_a': {
                'slot': {'start': '2025-02-11T18:00:00.000Z', 'duration': 30},
                'attendee': {'name': 'test', 'email': 'test@example.org', 'timezone': 'America/Los_Angeles'},
            },
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])
        time_updated = datetime.datetime(2025, 2, 5, 12, 0, 0, tzinfo=datetime.UTC)

        schedule = self._make_mock_schedule(
            weekdays=[2],  # Tuesday only
            slot_duration=30,
            start_time=time(18, 0),  # 10AM PST in UTC
            end_time=time(1, 0),  # 5PM PST in UTC
            timezone='America/Los_Angeles',
            time_updated=time_updated,
            use_custom_availabilities=True,
            availabilities=[
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(17, 0),  # 9AM PST in UTC
                    end_time=time(20, 0),  # 12PM PST in UTC
                    time_updated=time_updated,
                )
            ],
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid is True

    def test_custom_availability_booking_outside_range(self):
        """Booking outside all custom availability time ranges should be invalid."""
        # Tuesday 2025-02-11 at 2:00 PM PST (22:00 UTC) - outside the 9AM-12PM range
        request_data = {
            's_a': {
                'slot': {'start': '2025-02-11T22:00:00.000Z', 'duration': 30},
                'attendee': {'name': 'test', 'email': 'test@example.org', 'timezone': 'America/Los_Angeles'},
            },
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])
        time_updated = datetime.datetime(2025, 2, 5, 12, 0, 0, tzinfo=datetime.UTC)

        schedule = self._make_mock_schedule(
            weekdays=[2],  # Tuesday only
            slot_duration=30,
            start_time=time(18, 0),
            end_time=time(1, 0),
            timezone='America/Los_Angeles',
            time_updated=time_updated,
            use_custom_availabilities=True,
            availabilities=[
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(17, 0),  # 9AM PST in UTC
                    end_time=time(20, 0),  # 12PM PST in UTC
                    time_updated=time_updated,
                )
            ],
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid is False

    def test_custom_availability_multiple_ranges_same_day(self):
        """Booking within one of multiple custom availability ranges on the same day should be valid."""
        # Tuesday 2025-02-11 at 4:30 PM PST (00:30 UTC next day)
        # This is within the second availability range (4PM-6PM PST)
        request_data = {
            's_a': {
                'slot': {'start': '2025-02-12T00:30:00.000Z', 'duration': 30},
                'attendee': {'name': 'test', 'email': 'test@example.org', 'timezone': 'America/Los_Angeles'},
            },
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])
        time_updated = datetime.datetime(2025, 2, 5, 12, 0, 0, tzinfo=datetime.UTC)

        schedule = self._make_mock_schedule(
            weekdays=[2],  # Tuesday only
            slot_duration=30,
            start_time=time(18, 0),
            end_time=time(2, 0),
            timezone='America/Los_Angeles',
            time_updated=time_updated,
            use_custom_availabilities=True,
            availabilities=[
                # Range 1: 9AM-12PM PST (17:00-20:00 UTC)
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(17, 0),
                    end_time=time(20, 0),
                    time_updated=time_updated,
                ),
                # Range 2: 4PM-6PM PST (00:00-02:00 UTC next day)
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(0, 0),
                    end_time=time(2, 0),
                    time_updated=time_updated,
                ),
            ],
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid is True

    def test_custom_availability_gap_between_ranges(self):
        """Booking in the gap between custom availability ranges should be invalid."""
        # Tuesday 2025-02-11 at 1:00 PM PST (21:00 UTC)
        # This is in the gap between 9AM-12PM and 4PM-6PM ranges
        request_data = {
            's_a': {
                'slot': {'start': '2025-02-11T21:00:00.000Z', 'duration': 30},
                'attendee': {'name': 'test', 'email': 'test@example.org', 'timezone': 'America/Los_Angeles'},
            },
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])
        time_updated = datetime.datetime(2025, 2, 5, 12, 0, 0, tzinfo=datetime.UTC)

        schedule = self._make_mock_schedule(
            weekdays=[2],  # Tuesday only
            slot_duration=30,
            start_time=time(18, 0),
            end_time=time(2, 0),
            timezone='America/Los_Angeles',
            time_updated=time_updated,
            use_custom_availabilities=True,
            availabilities=[
                # Range 1: 9AM-12PM PST (17:00-20:00 UTC)
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(17, 0),
                    end_time=time(20, 0),
                    time_updated=time_updated,
                ),
                # Range 2: 4PM-6PM PST (00:00-02:00 UTC next day)
                # Gap: 12PM-4PM PST (20:00-00:00 UTC)
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(0, 0),
                    end_time=time(2, 0),
                    time_updated=time_updated,
                ),
            ],
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid is False

    def test_custom_availability_no_availability_for_weekday(self):
        """Booking on a weekday with no custom availability defined should be invalid."""
        # Wednesday 2025-02-12 at 10:00 AM PST (18:00 UTC)
        # But only Tuesday has custom availability
        request_data = {
            's_a': {
                'slot': {'start': '2025-02-12T18:00:00.000Z', 'duration': 30},
                'attendee': {'name': 'test', 'email': 'test@example.org', 'timezone': 'America/Los_Angeles'},
            },
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])
        time_updated = datetime.datetime(2025, 2, 5, 12, 0, 0, tzinfo=datetime.UTC)

        schedule = self._make_mock_schedule(
            weekdays=[2, 3],  # Tuesday and Wednesday
            slot_duration=30,
            start_time=time(18, 0),
            end_time=time(1, 0),
            timezone='America/Los_Angeles',
            time_updated=time_updated,
            use_custom_availabilities=True,
            availabilities=[
                # Only Tuesday has custom availability, not Wednesday
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday only
                    start_time=time(17, 0),
                    end_time=time(20, 0),
                    time_updated=time_updated,
                )
            ],
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid is False

    def test_custom_availability_slot_spans_boundary(self):
        """Booking slot that spans past the end of a custom availability range should be invalid."""
        # Tuesday 2025-02-11 at 11:45 AM PST (19:45 UTC)
        # With 30 min duration, this ends at 12:15 PM PST, past the 12PM end time
        request_data = {
            's_a': {
                'slot': {'start': '2025-02-11T19:45:00.000Z', 'duration': 30},
                'attendee': {'name': 'test', 'email': 'test@example.org', 'timezone': 'America/Los_Angeles'},
            },
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])
        time_updated = datetime.datetime(2025, 2, 5, 12, 0, 0, tzinfo=datetime.UTC)

        schedule = self._make_mock_schedule(
            weekdays=[2],  # Tuesday only
            slot_duration=30,
            start_time=time(18, 0),
            end_time=time(20, 0),
            timezone='America/Los_Angeles',
            time_updated=time_updated,
            use_custom_availabilities=True,
            availabilities=[
                # Custom availability: 9AM-12PM PST (17:00-20:00 UTC)
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(17, 0),
                    end_time=time(20, 0),
                    time_updated=time_updated,
                )
            ],
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid is False

    def test_custom_availability_exact_boundary(self):
        """Booking slot that ends exactly at the custom availability end time should be valid."""
        # Tuesday 2025-02-11 at 11:30 AM PST (19:30 UTC)
        # With 30 min duration, this ends exactly at 12PM PST
        request_data = {
            's_a': {
                'slot': {'start': '2025-02-11T19:30:00.000Z', 'duration': 30},
                'attendee': {'name': 'test', 'email': 'test@example.org', 'timezone': 'America/Los_Angeles'},
            },
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])
        time_updated = datetime.datetime(2025, 2, 5, 12, 0, 0, tzinfo=datetime.UTC)

        schedule = self._make_mock_schedule(
            weekdays=[2],  # Tuesday only
            slot_duration=30,
            start_time=time(18, 0),
            end_time=time(20, 0),
            timezone='America/Los_Angeles',
            time_updated=time_updated,
            use_custom_availabilities=True,
            availabilities=[
                # Custom availability: 9AM-12PM PST (17:00-20:00 UTC)
                self._make_mock_availability(
                    day_of_week=2,  # Tuesday
                    start_time=time(17, 0),
                    end_time=time(20, 0),
                    time_updated=time_updated,
                )
            ],
        )

        is_valid = is_this_a_valid_booking_time(schedule, s_a.slot)
        assert is_valid is True
