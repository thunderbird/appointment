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
            ]
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
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(10, 0)
            ),
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
            ]
        )
        assert not all_availability_is_valid(schedule)

        # Test completely overlapping slots
        schedule.availabilities = [
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(12, 0)
            ),
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(10, 0), end_time=time(11, 0)
            ),
        ]
        assert not all_availability_is_valid(schedule)

        # Test slots with invalid start/end time
        schedule.availabilities = [
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(12, 0)
            ),
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(14, 0), end_time=time(13, 0)
            ),
        ]
        assert not all_availability_is_valid(schedule)

        # Test slots that are too small for the defined duration
        schedule.availabilities = [
            schemas.AvailabilityValidationIn(
                schedule_id=1, day_of_week=1, start_time=time(9, 0), end_time=time(9, 15)
            ),
        ]
        assert not all_availability_is_valid(schedule)
