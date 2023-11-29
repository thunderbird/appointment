import pytest
from faker import Faker
from backend.src.appointment.database import repo, schemas, models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_appointment(with_db, make_caldav_calendar, make_appointment_slot):
    fake = Faker()

    def _make_appointment(calendar_id=FAKER_RANDOM_VALUE,
                          title=FAKER_RANDOM_VALUE,
                          details=FAKER_RANDOM_VALUE,
                          duration=FAKER_RANDOM_VALUE,
                          location_url=FAKER_RANDOM_VALUE,
                          location_type=FAKER_RANDOM_VALUE,
                          location_suggestions=FAKER_RANDOM_VALUE,
                          location_selected=FAKER_RANDOM_VALUE,
                          location_name=FAKER_RANDOM_VALUE,
                          location_phone=FAKER_RANDOM_VALUE,
                          keep_open=True,
                          status=models.AppointmentStatus.draft,
                          meeting_link_provider=models.MeetingLinkProviderType.none,
                          slots=FAKER_RANDOM_VALUE
                          ):
        with with_db() as db:
            appointment = repo.create_calendar_appointment(db, schemas.AppointmentFull(
                title=title if factory_has_value(title) else fake.name(),
                details=details if factory_has_value(details) else fake.sentence(),
                duration=duration if factory_has_value(duration) else fake.pyint(15, 60),
                location_url=location_url if factory_has_value(location_url) else fake.url(),
                location_type=location_type if factory_has_value(location_type) else fake.random_element(
                    (models.LocationType.inperson, models.LocationType.online)),
                location_suggestions=location_suggestions if factory_has_value(location_suggestions) else fake.city(),
                location_selected=location_selected if factory_has_value(location_selected) else fake.city(),
                location_name=location_name if factory_has_value(location_name) else fake.city(),
                location_phone=location_phone if factory_has_value(location_phone) else fake.phone_number(),
                keep_open=keep_open,
                status=status,
                meeting_link_provider=meeting_link_provider,
                calendar_id=calendar_id if factory_has_value(calendar_id) else make_caldav_calendar(connected=True).id
            ), [])

            if not factory_has_value(slots):
                make_appointment_slot(appointment_id=appointment.id)
            else:
                repo.add_appointment_slots(db, slots, appointment.id)

            # Refresh our appointment now that is has slot data
            db.refresh(appointment)
            # Load the relationship at least once (otherwise we won't be able to access them)
            appointment.slots
            appointment.calendar
            appointment.calendar.owner

            return appointment

    return _make_appointment
