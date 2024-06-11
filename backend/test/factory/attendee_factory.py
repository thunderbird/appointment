import pytest
from faker import Faker
from appointment.database import models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_attendee(with_db):
    fake = Faker()

    def _make_attendee(email=FAKER_RANDOM_VALUE, name=FAKER_RANDOM_VALUE):
        with with_db() as db:
            db_attendee = models.Attendee(
                email=email if factory_has_value(email) else fake.email(),
                name=name if factory_has_value(name) else fake.name(),
            )
            db.add(db_attendee)
            db.commit()
            db.refresh(db_attendee)

        return db_attendee

    return _make_attendee
