import pytest
from faker import Faker
from appointment.database import models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_waiting_list(with_db):
    fake = Faker()

    def _make_waiting_list(invite_id=None, email=FAKER_RANDOM_VALUE, email_verified=False) -> models.WaitingList:
        with with_db() as db:
            invite = models.WaitingList(
                email=email if factory_has_value(email) else fake.email(),
                email_verified=email_verified,
                invite_id=invite_id,
            )
            db.add(invite)
            db.commit()
            db.refresh(invite)
            return invite

    return _make_waiting_list
