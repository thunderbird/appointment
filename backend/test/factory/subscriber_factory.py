import secrets

import pytest
from argon2 import PasswordHasher
from faker import Faker
from appointment.database import repo, schemas, models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_subscriber(with_db):
    fake = Faker()

    def _make_subscriber(
        level, name=FAKER_RANDOM_VALUE, username=FAKER_RANDOM_VALUE, email=FAKER_RANDOM_VALUE, password=None
    ):
        with with_db() as db:
            subscriber = repo.subscriber.create(
                db,
                schemas.SubscriberAuth(
                    name=name if factory_has_value(name) else fake.name(),
                    username=username if factory_has_value(username) else fake.name().replace(' ', '_'),
                    email=email if factory_has_value(email) else fake.email(),
                    level=level,
                    timezone='America/Vancouver',
                    short_link_hash=secrets.token_hex(32)
                ),
            )
            # If we've passed in a password then hash it and save it to the subscriber
            if password:
                ph = PasswordHasher()
                subscriber.password = ph.hash(password)
                db.add(subscriber)
                db.commit()
                db.refresh(subscriber)

            return subscriber

    return _make_subscriber


@pytest.fixture
def make_pro_subscriber(make_subscriber):
    """Alias for make_subscriber with pro subscriber level"""

    def _make_pro_subscriber(
        name=FAKER_RANDOM_VALUE, username=FAKER_RANDOM_VALUE, email=FAKER_RANDOM_VALUE, password=None
    ):
        return make_subscriber(models.SubscriberLevel.pro, name, username, email, password)

    return _make_pro_subscriber


@pytest.fixture
def make_basic_subscriber(make_subscriber):
    """Alias for make_subscriber with basic subscriber level"""

    def _make_basic_subscriber(
        name=FAKER_RANDOM_VALUE, username=FAKER_RANDOM_VALUE, email=FAKER_RANDOM_VALUE, password=None
    ):
        return make_subscriber(models.SubscriberLevel.basic, name, username, email, password)

    return _make_basic_subscriber
