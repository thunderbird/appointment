import pytest
from faker import Faker
from appointment.database import repo, schemas, models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_schedule(with_db, make_caldav_calendar):
    fake = Faker()

    def _make_schedule(
        calendar_id=FAKER_RANDOM_VALUE,
        active=False,
        name=FAKER_RANDOM_VALUE,
        location_type=FAKER_RANDOM_VALUE,
        location_url=FAKER_RANDOM_VALUE,
        details=FAKER_RANDOM_VALUE,
        start_date=FAKER_RANDOM_VALUE,
        end_date=FAKER_RANDOM_VALUE,
        start_time=FAKER_RANDOM_VALUE,
        end_time=FAKER_RANDOM_VALUE,
        earliest_booking=FAKER_RANDOM_VALUE,
        farthest_booking=FAKER_RANDOM_VALUE,
        weekdays=[1, 2, 3, 4, 5],
        slot_duration=FAKER_RANDOM_VALUE,
        meeting_link_provider=models.MeetingLinkProviderType.none,
        slug=FAKER_RANDOM_VALUE,
        booking_confirmation=True,
    ):
        with with_db() as db:
            return repo.schedule.create(
                db,
                schemas.ScheduleBase(
                    active=active,
                    name=name if factory_has_value(name) else fake.name(),
                    location_url=location_url if factory_has_value(location_url) else fake.url(),
                    location_type=location_type
                    if factory_has_value(location_type)
                    else fake.random_element((models.LocationType.inperson, models.LocationType.online)),
                    details=details if factory_has_value(details) else fake.sentence(),
                    start_date=start_date if factory_has_value(start_date) else fake.date_object(),
                    end_date=end_date if factory_has_value(end_date) else fake.date_object(),
                    start_time=start_time if factory_has_value(start_time) else fake.time_object(),
                    end_time=end_time if factory_has_value(end_time) else fake.time_object(),
                    earliest_booking=earliest_booking if factory_has_value(earliest_booking) else fake.pyint(5, 15),
                    farthest_booking=farthest_booking if factory_has_value(farthest_booking) else fake.pyint(15, 60),
                    weekdays=weekdays,
                    slot_duration=slot_duration if factory_has_value(slot_duration) else fake.pyint(15, 60),
                    meeting_link_provider=meeting_link_provider,
                    slug=slug if factory_has_value(slug) else fake.uuid4(),
                    booking_confirmation=booking_confirmation,
                    calendar_id=calendar_id
                    if factory_has_value(calendar_id)
                    else make_caldav_calendar(connected=True).id,
                ),
            )

    return _make_schedule
