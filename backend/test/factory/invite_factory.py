import pytest
from faker import Faker
from appointment.database import models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_invite(with_db):
    fake = Faker()

    def _make_invite(
        subscriber_id=None,
        code=FAKER_RANDOM_VALUE,
        status=models.InviteStatus.active,
        owner_id=None
    ) -> models.Invite:
        with with_db() as db:
            invite = models.Invite(
                subscriber_id=subscriber_id,
                status=status,
                code=code if factory_has_value(code) else fake.uuid4(),
                owner_id=owner_id
            )
            db.add(invite)
            db.commit()
            db.refresh(invite)
            return invite

    return _make_invite
