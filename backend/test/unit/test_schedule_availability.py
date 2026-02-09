from appointment.database.repo.schedule import all_availability_is_valid
from appointment.database import schemas
from datetime import date, time


class TestScheduleAvailability:
    def test_empty_availability_is_valid(self):
        # Test empty availability is valid
        schedule = schemas.ScheduleValidationIn(
            name='test',
            calendar_id=1,
            slot_duration=30,
            start_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        assert all_availability_is_valid(schedule)

    def test_all_availability_is_valid(self):
        # Test already sorted availabilities
        schedule = schemas.ScheduleValidationIn(
            name='test',
            calendar_id=1,
            slot_duration=30,
            start_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            availabilities=[
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(10, 0)
                ),
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(10, 0), end_time=time(11, 0)
                ),
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=2, start_time=time(9, 0), end_time=time(10, 0)
                ),
            ],
        )
        assert all_availability_is_valid(schedule)

        # Test unordered availabilities
        schedule.availabilities = [
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(15, 0), end_time=time(16, 0)
            ),
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(10, 0), end_time=time(11, 0)
            ),
            schemas.AvailabilityValidationIn(schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(10, 0)),
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(17, 0), end_time=time(18, 0)
            ),
        ]
        assert all_availability_is_valid(schedule)

    def test_all_availability_is_invalid(self):
        # Test overlapping end-start times
        schedule = schemas.ScheduleValidationIn(
            name='test',
            calendar_id=1,
            slot_duration=30,
            start_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            availabilities=[
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(11, 0)
                ),
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(10, 0), end_time=time(12, 0)
                ),
            ],
        )
        assert not all_availability_is_valid(schedule)

        # Test completely overlapping slots
        schedule.availabilities = [
            schemas.AvailabilityValidationIn(schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(12, 0)),
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(10, 0), end_time=time(11, 0)
            ),
        ]
        assert not all_availability_is_valid(schedule)

        # Test slots with invalid start/end time
        schedule.availabilities = [
            schemas.AvailabilityValidationIn(schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(12, 0)),
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(14, 0), end_time=time(13, 0)
            ),
        ]
        assert not all_availability_is_valid(schedule)

        # Test slots that are too small for the defined duration
        schedule.availabilities = [
            schemas.AvailabilityValidationIn(schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(9, 15)),
        ]
        assert not all_availability_is_valid(schedule)

    def test_availability_valid_with_negative_utc_offset_crossing_midnight(self):
        """Availability in America/Regina (UTC-6): 5pm-7pm local = 23:00-01:00 UTC.
        The UTC times cross midnight, but should still be valid after timezone conversion."""
        schedule = schemas.ScheduleValidationIn(
            name='test',
            calendar_id=1,
            slot_duration=30,
            start_date=date.today(),
            # Schedule general times: 9am-5pm CST = 15:00-23:00 UTC
            start_time=time(15, 0),
            end_time=time(23, 0),
            timezone='America/Regina',
            availabilities=[
                # 5pm-7pm CST (UTC-6) = 23:00 UTC - 01:00 UTC (next day)
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(23, 0), end_time=time(1, 0)
                ),
            ],
        )
        assert all_availability_is_valid(schedule)

    def test_availability_valid_with_positive_utc_offset_crossing_midnight(self):
        """Availability in Asia/Tokyo (UTC+9): 8am-10am local = 23:00-01:00 UTC.
        The UTC times cross midnight, but should still be valid after timezone conversion."""
        schedule = schemas.ScheduleValidationIn(
            name='test',
            calendar_id=1,
            slot_duration=30,
            start_date=date.today(),
            # Schedule general times: 9am-5pm JST = 00:00-08:00 UTC
            start_time=time(0, 0),
            end_time=time(8, 0),
            timezone='Asia/Tokyo',
            availabilities=[
                # 8am-10am JST (UTC+9) = 23:00 UTC (prev day) - 01:00 UTC (crosses midnight)
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(23, 0), end_time=time(1, 0)
                ),
            ],
        )
        assert all_availability_is_valid(schedule)

    def test_multiple_availability_valid_with_timezone_crossing_midnight(self):
        """Multiple non-overlapping availabilities in America/Regina (UTC-6) where one crosses midnight in UTC."""
        schedule = schemas.ScheduleValidationIn(
            name='test',
            calendar_id=1,
            slot_duration=30,
            start_date=date.today(),
            # Schedule general times: 9am-5pm CST = 15:00-23:00 UTC
            start_time=time(15, 0),
            end_time=time(23, 0),
            timezone='America/Regina',
            availabilities=[
                # 9am-12pm CST (UTC-6) = 15:00-18:00 UTC
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(15, 0), end_time=time(18, 0)
                ),
                # 5pm-7pm CST (UTC-6) = 23:00-01:00 UTC (crosses midnight)
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(23, 0), end_time=time(1, 0)
                ),
            ],
        )
        assert all_availability_is_valid(schedule)

    def test_availability_invalid_with_timezone_overlapping(self):
        """Overlapping availabilities that only overlap in local time after timezone conversion.
        In UTC the slots appear adjacent (end=00:00, start=23:30), but in America/Regina (UTC-6)
        they convert to 6pm-6:30pm and 5:30pm-6pm, which overlap."""
        schedule = schemas.ScheduleValidationIn(
            name='test',
            calendar_id=1,
            slot_duration=30,
            start_date=date.today(),
            # Schedule general times: 9am-5pm CST = 15:00-23:00 UTC
            start_time=time(15, 0),
            end_time=time(23, 0),
            timezone='America/Regina',
            availabilities=[
                # 5pm-6:30pm CST (UTC-6) = 23:00-00:30 UTC (crosses midnight)
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(23, 0), end_time=time(0, 30)
                ),
                # 5:30pm-7pm CST (UTC-6) = 23:30-01:00 UTC (crosses midnight, overlaps above in local time)
                schemas.AvailabilityValidationIn(
                    schedule_id=1, day_of_week=1, start_time=time(23, 30), end_time=time(1, 0)
                ),
            ],
        )
        assert not all_availability_is_valid(schedule)
