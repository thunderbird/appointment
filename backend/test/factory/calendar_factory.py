import pytest
from faker import Faker
from appointment.database import repo, schemas, models
from defines import TEST_USER_ID, FAKER_RANDOM_VALUE, factory_has_value


@pytest.fixture
def make_caldav_calendar(with_db):
    fake = Faker()

    def _make_caldav_calendar(
        subscriber_id=TEST_USER_ID,
        url=FAKER_RANDOM_VALUE,
        title=FAKER_RANDOM_VALUE,
        color=FAKER_RANDOM_VALUE,
        connected=False,
        user=FAKER_RANDOM_VALUE,
        password=FAKER_RANDOM_VALUE,
        external_connection_id=None,
    ):
        with with_db() as db:
            title = title if factory_has_value(title) else fake.name()
            return repo.calendar.create(
                db,
                schemas.CalendarConnection(
                    title=title,
                    color=color if factory_has_value(color) else fake.color(),
                    connected=connected,
                    provider=models.CalendarProvider.caldav,
                    url=url if factory_has_value(url) else fake.url(),
                    user=user if factory_has_value(user) else fake.name(),
                    password=password if factory_has_value(password) else fake.password(),
                ),
                subscriber_id,
                external_connection_id=external_connection_id,
            )

    return _make_caldav_calendar


@pytest.fixture
def make_google_calendar(with_db):
    fake = Faker()

    def _make_google_calendar(
        subscriber_id=TEST_USER_ID,
        title=FAKER_RANDOM_VALUE,
        color=FAKER_RANDOM_VALUE,
        id=FAKER_RANDOM_VALUE,
        connected=False,
        external_connection_id=None,
    ):
        with with_db() as db:
            title = title if factory_has_value(title) else fake.name()
            id = id if factory_has_value(id) else fake.uuid4()
            return repo.calendar.create(
                db,
                schemas.CalendarConnection(
                    title=title,
                    color=color if factory_has_value(color) else fake.color(),
                    connected=connected,
                    provider=models.CalendarProvider.google,
                    url=id,
                    user=id,
                    password='',
                ),
                subscriber_id,
                external_connection_id=external_connection_id,
            )

    return _make_google_calendar
