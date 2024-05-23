import pytest
from faker import Faker
from appointment.database import repo, schemas, models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_appointment_slot(with_db):
    fake = Faker()

    def _make_appointment_slot(appointment_id=None,
                               start=FAKER_RANDOM_VALUE,
                               duration=FAKER_RANDOM_VALUE,
                               attendee_id=None,
                               booking_tkn=None,
                               booking_expires_at=None,
                               booking_status=models.BookingStatus.none,
                               meeting_link_id=None,
                               meeting_link_url=None):
        with with_db() as db:
            return repo.slot.add_for_appointment(db, [schemas.SlotBase(
                start=start if factory_has_value(start) else fake.date_time(),
                duration=duration if factory_has_value(duration) else fake.pyint(15, 60),
                attendee_id=attendee_id,
                booking_tkn=booking_tkn,
                booking_expires_at=booking_expires_at,
                booking_status=booking_status,
                meeting_link_id=meeting_link_id,
                meeting_link_url=meeting_link_url,
            )], appointment_id)

    return _make_appointment_slot
