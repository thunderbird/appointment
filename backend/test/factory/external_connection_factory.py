import pytest
from faker import Faker
from backend.src.appointment.database import repo, schemas, models
from defines import FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_external_connections(with_db):
    fake = Faker()

    def _make_external_connections(subscriber_id,
                                   name=FAKER_RANDOM_VALUE,
                                   type=FAKER_RANDOM_VALUE,
                                   type_id=FAKER_RANDOM_VALUE,
                                   token=FAKER_RANDOM_VALUE):
        with with_db() as db:
            return repo.create_subscriber_external_connection(db, schemas.ExternalConnection(
                owner_id=subscriber_id,
                name=name if factory_has_value(name) else fake.name(),
                type=type if factory_has_value(type) else fake.random_element(
                    (models.ExternalConnectionType.zoom.value, models.ExternalConnectionType.google.value, models.ExternalConnectionType.fxa.value)),
                type_id=type_id if factory_has_value(type_id) else fake.uuid4(),
                token=token if factory_has_value(token) else fake.password(),
            ))

    return _make_external_connections
