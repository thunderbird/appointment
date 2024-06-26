import pytest
from faker import Faker
from appointment.database import models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_invite_bucket(with_db):
    fake = Faker()

    def _make_invite_bucket(invite_id=None, email=FAKER_RANDOM_VALUE) -> models.InviteBucket:
        with with_db() as db:
            invite = models.InviteBucket(
                email=email if factory_has_value(email) else fake.email(),
                invite_id=invite_id,
            )
            db.add(invite)
            db.commit()
            db.refresh(invite)
            return invite

    return _make_invite_bucket
