import pytest
from faker import Faker
from backend.src.appointment.database import repo, schemas, models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_subscriber(with_db):
    fake = Faker()

    def _make_subscriber(level, name=FAKER_RANDOM_VALUE, username=FAKER_RANDOM_VALUE, email=FAKER_RANDOM_VALUE):
        with with_db() as db:
            return repo.create_subscriber(db, schemas.SubscriberBase(
                name=name if factory_has_value(name) else fake.name(),
                username=username if factory_has_value(username) else fake.name(),
                email=email if factory_has_value(FAKER_RANDOM_VALUE) else fake.email(),
                level=level,
                timezone='America/Vancouver'
            ))

    return _make_subscriber


@pytest.fixture
def make_pro_subscriber(make_subscriber):
    """Alias for make_subscriber with pro subscriber level"""
    def _make_pro_subscriber(name=FAKER_RANDOM_VALUE, username=FAKER_RANDOM_VALUE, email=FAKER_RANDOM_VALUE):
        return make_subscriber(models.SubscriberLevel.pro, name, username, email)

    return _make_pro_subscriber


@pytest.fixture
def make_basic_subscriber(make_subscriber):
    """Alias for make_subscriber with basic subscriber level"""
    def _make_basic_subscriber(name=FAKER_RANDOM_VALUE, username=FAKER_RANDOM_VALUE, email=FAKER_RANDOM_VALUE):
        return make_subscriber(models.SubscriberLevel.basic, name, username, email)

    return _make_basic_subscriber
