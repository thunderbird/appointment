import os

import pytest

from appointment.database.models import CalendarProvider
from appointment.controller.calendar import CalDavConnector, GoogleConnector
from appointment.database import schemas, models, repo
from appointment.defines import GOOGLE_CALDAV_DOMAINS

from sqlalchemy import select

from defines import auth_headers, TEST_USER_ID


def get_calendar_factory():
    """Provides multiple inputs to the test. The test runs per each time we yield.
    We pass fixture string names, and we'll need to create them by using request.getfixturevalue(string_name).
    It's ugly, but `parametrize` doesn't support fixtures..."""
    providers = {
        schemas.CalendarProvider.caldav: 'make_caldav_calendar',
        schemas.CalendarProvider.google: 'make_google_calendar',
    }
    for provider, factory_name in providers.items():
        yield provider, factory_name


def get_mock_connector_class():
    """Provide two fake connectors, the original connector (for monkeypatching), and the test data"""
    test_url = 'https://caldav.thunderbird.net/'
    test_user = 'thunderbird'

    class MockCaldavConnector:
        @staticmethod
        def __init__(self, db, subscriber_id, calendar_id, redis_instance, url, user, password):
            """We don't want to initialize a client"""
            pass

        @staticmethod
        def list_calendars(self):
            return [
                schemas.CalendarConnectionOut(provider=schemas.CalendarProvider.caldav, url=test_url, user=test_user)
            ]

    class MockGoogleConnector:
        @staticmethod
        def __init__(
            self,
            subscriber_id,
            calendar_id,
            redis_instance,
            db,
            remote_calendar_id,
            google_client,
            google_tkn: str = None,
        ):
            pass

        @staticmethod
        def list_calendars(self):
            return [
                schemas.CalendarConnectionOut(provider=schemas.CalendarProvider.google, url=test_url, user=test_user)
            ]

    connectors = [
        (MockCaldavConnector, CalDavConnector, schemas.CalendarProvider.caldav.value, test_url, test_user),
        (MockGoogleConnector, GoogleConnector, schemas.CalendarProvider.google.value, test_url, test_user),
    ]

    for connector in connectors:
        # This is pretty ugly
        yield connector[0], connector[1], connector[2], connector[3], connector[4]


class TestCalendar:
    def test_read_connected_calendars_before_creation(self, with_client):
        response = with_client.get('/me/calendars', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_read_unconnected_calendars_before_creation(self, with_client):
        response = with_client.get('/me/calendars', params={'only_connected': False}, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_read_connected_calendars_after_creation(self, with_client, provider, factory_name, request):
        """Get /me/calendars and ensure the list is 0 (as it only returns connected calendars by default)"""
        # Get the fixture by name
        calendar_factory = request.getfixturevalue(factory_name)
        calendar_factory()

        response = with_client.get('/me/calendars', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_read_unconnected_calendars_after_creation(self, with_client, provider, factory_name, request):
        """Get /me/calendars and ensure the list is 1 (as we're explicitly asking for unconnected calendars too)"""
        generated_calendar = request.getfixturevalue(factory_name)()

        response = with_client.get('/me/calendars', params={'only_connected': False}, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        calendar = data[0]
        assert calendar['title'] == generated_calendar.title
        assert calendar['color'] == generated_calendar.color
        assert not calendar['connected']
        assert 'password' not in calendar

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_read_existing_caldav_calendar(self, with_client, provider, factory_name, request):
        generated_calendar = request.getfixturevalue(factory_name)()

        response = with_client.get('/cal/1', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['title'] == generated_calendar.title
        assert data['color'] == generated_calendar.color
        assert data['provider'] == provider.value
        assert data['url'] == generated_calendar.url
        assert data['user'] == generated_calendar.user
        assert not data['connected']
        assert 'password' not in data

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_read_missing_calendar(self, with_client, provider, factory_name, request):
        generated_calendar = request.getfixturevalue(factory_name)()

        # Intentionally read the wrong calendar id
        response = with_client.get(f'/cal/{generated_calendar.id + 1}', headers=auth_headers)
        assert response.status_code == 404, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_read_foreign_calendar(self, with_client, make_pro_subscriber, provider, factory_name, request):
        """Ensure we can't read other peoples calendars"""
        the_other_guy = make_pro_subscriber()
        generated_calendar = request.getfixturevalue(factory_name)(the_other_guy.id)

        response = with_client.get(f'/cal/{generated_calendar.id}', headers=auth_headers)
        assert response.status_code == 403, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_update_foreign_calendar(self, with_client, make_pro_subscriber, provider, factory_name, request):
        the_other_guy = make_pro_subscriber()
        generated_calendar = request.getfixturevalue(factory_name)(the_other_guy.id)

        response = with_client.put(
            f'/cal/{generated_calendar.id}',
            json={'title': 'b', 'url': 'b', 'user': 'b', 'password': 'b'},
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_update_invalid_calendar_id(self, with_client, request):
        response = with_client.put(
            f'/cal/{9999}',
            json={'title': 'b', 'url': 'b', 'user': 'b', 'password': 'b'},
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_connect_calendar(self, with_client, provider, factory_name, request):
        generated_calendar = request.getfixturevalue(factory_name)()

        assert generated_calendar.connected is False

        response = with_client.post(f'/cal/{generated_calendar.id}/connect', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['title'] == generated_calendar.title
        assert data['color'] == generated_calendar.color
        assert data['connected']
        assert 'password' not in data

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_connect_missing_calendar(self, with_client, provider, factory_name, request):
        generated_calendar = request.getfixturevalue(factory_name)()

        # Intentionally use the wrong calendar id
        response = with_client.post(f'/cal/{generated_calendar.id + 1}/connect', headers=auth_headers)
        assert response.status_code == 404, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_connect_foreign_calendar(self, with_client, make_pro_subscriber, provider, factory_name, request):
        the_other_guy = make_pro_subscriber()
        generated_calendar = request.getfixturevalue(factory_name)(the_other_guy.id)

        response = with_client.post(f'/cal/{generated_calendar.id}/connect', headers=auth_headers)
        assert response.status_code == 403, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_read_connected_calendars_after_connection(self, with_client, provider, factory_name, request):
        generated_calendar = request.getfixturevalue(factory_name)(connected=True)

        with_client.post(
            '/cal',
            json={
                'title': 'Second CalDAV calendar',
                'color': '#123456',
                'provider': CalendarProvider.caldav.value,
                'url': 'test',
                'user': 'test',
                'password': 'test',
            },
            headers=auth_headers,
        )
        response = with_client.get('/me/calendars', headers=auth_headers)
        assert response.status_code == 200, response.text

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        calendar = data[0]
        assert calendar['title'] == generated_calendar.title
        assert calendar['color'] == generated_calendar.color
        assert calendar['connected']
        assert 'password' not in calendar

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_read_unconnected_calendars_after_connection(self, with_client, provider, factory_name, request):
        request.getfixturevalue(factory_name)(connected=True)
        request.getfixturevalue(factory_name)(connected=False)

        response = with_client.get('/me/calendars', params={'only_connected': False}, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_delete_existing_calendar(self, with_client, provider, factory_name, request):
        generated_calendar = request.getfixturevalue(factory_name)(connected=True)

        response = with_client.delete(f'/cal/{generated_calendar.id}', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['title'] == generated_calendar.title
        assert data['color'] == generated_calendar.color
        assert data['connected']
        assert 'password' not in data

        response = with_client.get(f'/cal/{generated_calendar.id}', headers=auth_headers)
        assert response.status_code == 404, response.text

        response = with_client.get('/me/calendars', headers=auth_headers)
        data = response.json()
        assert len(data) == 0

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_delete_missing_calendar(self, with_client, provider, factory_name, request):
        generated_calendar = request.getfixturevalue(factory_name)()

        # Intentionally call the wrong id
        response = with_client.delete(f'/cal/{generated_calendar.id + 1}', headers=auth_headers)
        assert response.status_code == 404, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_delete_foreign_calendar(self, with_client, make_pro_subscriber, provider, factory_name, request):
        the_other_guy = make_pro_subscriber()
        generated_calendar = request.getfixturevalue(factory_name)(the_other_guy.id)

        response = with_client.delete(f'/cal/{generated_calendar.id}', headers=auth_headers)
        assert response.status_code == 403, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_connect_more_calendars_than_tier_allows(
        self, with_client, with_db, make_basic_subscriber, provider, factory_name, request
    ):
        basic_user = make_basic_subscriber()

        cal = {}
        for i in range(1, int(os.getenv('TIER_BASIC_CALENDAR_LIMIT'))):
            cal[i] = request.getfixturevalue(factory_name)(basic_user.id, connected=True)

        response = with_client.post(f'/cal/{cal[2].id}/connect', headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_create_connection_failure(self, with_client, monkeypatch):
        """Attempt to create caldav calendar connection with invalid credentials, expect failure"""

        # Mock the CalDavConnector to simulate connection failure
        from appointment.controller.calendar import CalDavConnector

        def mock_test_connection(self):
            return False

        monkeypatch.setattr(CalDavConnector, 'test_connection', mock_test_connection)

        response = with_client.post(
            '/caldav',
            json={
                'title': 'A caldav calendar',
                'color': '#123456',
                'provider': CalendarProvider.caldav.value,
                'url': 'https://invalid-caldav-server.com',
                'user': 'invalid_user',
                'password': 'invalid_password',
            },
            headers=auth_headers,
        )
        assert response.status_code == 400, response.text

    @pytest.mark.parametrize('provider,factory_name', get_calendar_factory())
    def test_disconnect_calendar(self, with_client, provider, factory_name, request):
        new_calendar = request.getfixturevalue(factory_name)(connected=True)

        response = with_client.post(f'/cal/{new_calendar.id}/disconnect', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['title'] == new_calendar.title
        assert data['color'] == new_calendar.color
        assert data['id'] == new_calendar.id
        assert not data['connected']


class TestCaldav:
    """Tests for caldav specific functionality"""

    def test_create_first_caldav_calendar(self, with_client):
        response = with_client.post(
            '/caldav',
            json={
                'title': 'First CalDAV calendar',
                'color': '#123456',
                'provider': CalendarProvider.caldav.value,
                'url': os.getenv('CALDAV_TEST_CALENDAR_URL'),
                'user': os.getenv('CALDAV_TEST_USER'),
                'password': os.getenv('CALDAV_TEST_PASS'),
                'connected': False,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['title'] == 'First CalDAV calendar'
        assert data['color'] == '#123456'
        assert not data['connected']
        assert 'password' not in data

    def test_create_google_caldav_calendar(self, with_client):
        response = with_client.post(
            '/caldav/auth',
            json={
                'url': 'https://' + GOOGLE_CALDAV_DOMAINS[0],
                'user': os.getenv('CALDAV_TEST_USER'),
                'password': os.getenv('CALDAV_TEST_PASS'),
            },
            headers=auth_headers,
        )
        assert response.status_code == 400, response.text
        data = response.json()
        assert data['detail']['id'] == 'GOOGLE_CALDAV_NOT_SUPPORTED'

    def test_update_existing_caldav_calendar_with_password(self, with_client, with_db, make_caldav_calendar):
        generated_calendar = make_caldav_calendar()

        response = with_client.put(
            f'/cal/{generated_calendar.id}',
            json={
                'title': 'First modified CalDAV calendar',
                'color': '#234567',
                'url': os.getenv('CALDAV_TEST_CALENDAR_URL') + 'x',
                'user': os.getenv('CALDAV_TEST_USER') + 'x',
                'password': os.getenv('CALDAV_TEST_PASS') + 'x',
                'connected': True,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()

        assert data['title'] == 'First modified CalDAV calendar'
        assert data['color'] == '#234567'
        assert not data['connected']
        assert 'password' not in data

        query = select(models.Calendar).where(models.Calendar.id == generated_calendar.id)

        with with_db() as db:
            cal = db.scalars(query).one()

        assert cal.url == os.getenv('CALDAV_TEST_CALENDAR_URL') + 'x'
        assert cal.user == os.getenv('CALDAV_TEST_USER') + 'x'
        assert cal.password == os.getenv('CALDAV_TEST_PASS') + 'x'

    def test_update_existing_caldav_calendar_without_password(self, with_client, with_db, make_caldav_calendar):
        """Ensure if we put a blank password into the request that the calendar will update with an empty password."""
        generated_calendar = make_caldav_calendar(password='')

        response = with_client.put(
            f'/cal/{generated_calendar.id}',
            json={
                'title': 'First modified CalDAV calendar',
                'color': '#234567',
                'url': os.getenv('CALDAV_TEST_CALENDAR_URL'),
                'user': os.getenv('CALDAV_TEST_USER'),
                'password': '',
                'connected': True,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['title'] == 'First modified CalDAV calendar'
        assert data['color'] == '#234567'
        assert 'password' not in data

        query = select(models.Calendar).where(models.Calendar.id == generated_calendar.id)

        with with_db() as db:
            cal = db.scalars(query).one()

        assert cal.url == os.getenv('CALDAV_TEST_CALENDAR_URL')
        assert cal.user == os.getenv('CALDAV_TEST_USER')
        assert cal.password == ''

    def test_caldav_auth_links_external_connection_id(self, with_client, with_db, monkeypatch):
        """Test that creating calendars through /caldav/auth correctly links external_connection_id"""

        # Mock the CalDAV client and its methods
        class MockCalendar:
            def __init__(self, name, url):
                self.name = name
                self.url = url

        class MockPrincipal:
            def calendars(self):
                return [
                    MockCalendar('Test Calendar 1', 'https://test-server.com/calendar1/'),
                    MockCalendar('Test Calendar 2', 'https://test-server.com/calendar2/'),
                ]

        class MockClient:
            def principal(self):
                return MockPrincipal()

        from appointment.controller.calendar import CalDavConnector

        def mock_init(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
            # Store the parameters we need
            self.db = db
            self.subscriber_id = subscriber_id
            self.user = user
            self.password = password
            self.client = MockClient()

        def mock_test_connection(self):
            return True

        def mock_is_supported(self, cal):
            return True

        def mock_bust_cached_events(self, all_calendars=False):
            # Mock implementation - no-op for testing
            pass

        # Apply all the mocks
        monkeypatch.setattr(CalDavConnector, '__init__', mock_init)
        monkeypatch.setattr(CalDavConnector, 'test_connection', mock_test_connection)
        monkeypatch.setattr(CalDavConnector, '_is_supported', mock_is_supported)
        monkeypatch.setattr(CalDavConnector, 'bust_cached_events', mock_bust_cached_events)

        # Call the /caldav/auth endpoint
        response = with_client.post(
            '/caldav/auth',
            json={
                'url': 'https://test-caldav-server.com',
                'user': 'test_user',
                'password': 'test_password',
            },
            headers=auth_headers,
        )

        assert response.status_code == 200, response.text

        with with_db() as db:
            # Check that an external connection was created
            external_connections_query = select(models.ExternalConnections).where(
                models.ExternalConnections.owner_id == TEST_USER_ID
            )
            external_connections = db.scalars(external_connections_query).all()
            assert len(external_connections) == 1

            external_connection = external_connections[0]
            assert external_connection.type == models.ExternalConnectionType.caldav
            assert external_connection.name == 'test_user'

            # Check that calendars were created with the correct external_connection_id
            calendars_query = select(models.Calendar).where(models.Calendar.owner_id == TEST_USER_ID)
            calendars = db.scalars(calendars_query).all()
            assert len(calendars) == 2  # We mocked 2 calendars

            # Verify both calendars have the correct external_connection_id
            for calendar in calendars:
                assert calendar.external_connection_id == external_connection.id
                assert calendar.provider == models.CalendarProvider.caldav
                assert calendar.user == 'test_user'
                assert calendar.password == 'test_password'

            # Verify calendar titles match our mock data
            calendar_titles = [cal.title for cal in calendars]
            assert 'Test Calendar 1' in calendar_titles
            assert 'Test Calendar 2' in calendar_titles


class TestCalendarUpdateOrCreate:
    """Tests for the update_or_create function in the calendar repository.

    These tests ensure that multiple subscribers can connect the same external calendar
    (e.g., the same Google calendar) and each gets their own calendar record.
    """

    def test_update_or_create_creates_new_calendar_when_none_exists(
        self, with_db, make_pro_subscriber, make_external_connections
    ):
        """Test that update_or_create creates a new calendar when no calendar exists with that URL."""
        subscriber = make_pro_subscriber()
        ec = make_external_connections(subscriber.id, type=models.ExternalConnectionType.google)

        calendar_url = 'test-calendar@google.com'
        calendar_data = schemas.CalendarConnection(
            title='Test Calendar',
            color='#4285f4',
            provider=models.CalendarProvider.google,
            url=calendar_url,
            user=calendar_url,
            password='',
        )

        with with_db() as db:
            result = repo.calendar.update_or_create(
                db=db,
                calendar=calendar_data,
                calendar_url=calendar_url,
                subscriber_id=subscriber.id,
                external_connection_id=ec.id,
            )

            assert result is not None
            assert result.owner_id == subscriber.id
            assert result.url == calendar_url
            assert result.title == 'Test Calendar'
            assert result.external_connection_id == ec.id

    def test_update_or_create_updates_existing_calendar_for_same_subscriber(
        self, with_db, make_pro_subscriber, make_external_connections
    ):
        """Test that update_or_create updates an existing calendar when the same subscriber calls it."""
        subscriber = make_pro_subscriber()
        ec = make_external_connections(subscriber.id, type=models.ExternalConnectionType.google)

        calendar_url = 'test-calendar@google.com'
        original_calendar = schemas.CalendarConnection(
            title='Original Title',
            color='#4285f4',
            provider=models.CalendarProvider.google,
            url=calendar_url,
            user=calendar_url,
            password='',
        )

        with with_db() as db:
            # Create the initial calendar
            first_result = repo.calendar.update_or_create(
                db=db,
                calendar=original_calendar,
                calendar_url=calendar_url,
                subscriber_id=subscriber.id,
                external_connection_id=ec.id,
            )
            first_calendar_id = first_result.id

            # Now call update_or_create again with updated data
            updated_calendar = schemas.CalendarConnection(
                title='Updated Title',
                color='#ff0000',
                provider=models.CalendarProvider.google,
                url=calendar_url,
                user=calendar_url,
                password='',
            )

            second_result = repo.calendar.update_or_create(
                db=db,
                calendar=updated_calendar,
                calendar_url=calendar_url,
                subscriber_id=subscriber.id,
                external_connection_id=ec.id,
            )

            # Should update the existing calendar, not create a new one
            assert second_result.id == first_calendar_id
            assert second_result.title == 'Updated Title'
            assert second_result.color == '#ff0000'

            # Verify only one calendar exists for this subscriber
            subscriber_calendars = repo.calendar.get_by_subscriber(db, subscriber.id)
            assert len(subscriber_calendars) == 1

    def test_update_or_create_creates_separate_calendar_for_different_subscriber(
        self, with_db, make_pro_subscriber, make_external_connections
    ):
        """Test that update_or_create creates a new calendar when a different subscriber
        connects the same external calendar (e.g., same Google calendar URL) successfully.
        """
        subscriber_a = make_pro_subscriber()
        subscriber_b = make_pro_subscriber()

        ec_a = make_external_connections(subscriber_a.id, type=models.ExternalConnectionType.google)
        ec_b = make_external_connections(subscriber_b.id, type=models.ExternalConnectionType.google)

        # Both subscribers are connecting the same Google calendar
        shared_calendar_url = 'shared-calendar@google.com'

        calendar_data_a = schemas.CalendarConnection(
            title='Calendar for Subscriber A',
            color='#4285f4',
            provider=models.CalendarProvider.google,
            url=shared_calendar_url,
            user=shared_calendar_url,
            password='',
        )

        calendar_data_b = schemas.CalendarConnection(
            title='Calendar for Subscriber B',
            color='#ff0000',
            provider=models.CalendarProvider.google,
            url=shared_calendar_url,
            user=shared_calendar_url,
            password='',
        )

        with with_db() as db:
            # Subscriber A connects the calendar first
            calendar_a = repo.calendar.update_or_create(
                db=db,
                calendar=calendar_data_a,
                calendar_url=shared_calendar_url,
                subscriber_id=subscriber_a.id,
                external_connection_id=ec_a.id,
            )

            assert calendar_a is not None
            assert calendar_a.owner_id == subscriber_a.id

            # Subscriber B connects the same calendar
            calendar_b = repo.calendar.update_or_create(
                db=db,
                calendar=calendar_data_b,
                calendar_url=shared_calendar_url,
                subscriber_id=subscriber_b.id,
                external_connection_id=ec_b.id,
            )

            # Subscriber B should get their own calendar record
            assert calendar_b is not None
            assert calendar_b.owner_id == subscriber_b.id
            assert calendar_b.id != calendar_a.id  # Different calendar records

            # Verify each subscriber has exactly one calendar
            calendars_a = repo.calendar.get_by_subscriber(db, subscriber_a.id)
            calendars_b = repo.calendar.get_by_subscriber(db, subscriber_b.id)

            assert len(calendars_a) == 1
            assert len(calendars_b) == 1

            # Verify the calendars belong to the correct subscribers
            assert calendars_a[0].owner_id == subscriber_a.id
            assert calendars_b[0].owner_id == subscriber_b.id

            # Verify the external connections are correct
            assert calendars_a[0].external_connection_id == ec_a.id
            assert calendars_b[0].external_connection_id == ec_b.id

    def test_update_or_create_does_not_modify_other_subscribers_calendar(
        self, with_db, make_pro_subscriber, make_external_connections
    ):
        """Test that when Subscriber B connects a calendar that Subscriber A already has,
        Subscriber A's calendar is not modified."""
        subscriber_a = make_pro_subscriber()
        subscriber_b = make_pro_subscriber()

        ec_a = make_external_connections(subscriber_a.id, type=models.ExternalConnectionType.google)
        ec_b = make_external_connections(subscriber_b.id, type=models.ExternalConnectionType.google)

        shared_calendar_url = 'shared-calendar@google.com'

        calendar_data_a = schemas.CalendarConnection(
            title='Original Title A',
            color='#4285f4',
            provider=models.CalendarProvider.google,
            url=shared_calendar_url,
            user=shared_calendar_url,
            password='',
        )

        calendar_data_b = schemas.CalendarConnection(
            title='Title B',
            color='#ff0000',
            provider=models.CalendarProvider.google,
            url=shared_calendar_url,
            user=shared_calendar_url,
            password='',
        )

        with with_db() as db:
            # Subscriber A connects first
            repo.calendar.update_or_create(
                db=db,
                calendar=calendar_data_a,
                calendar_url=shared_calendar_url,
                subscriber_id=subscriber_a.id,
                external_connection_id=ec_a.id,
            )

            # Subscriber B connects the same calendar
            repo.calendar.update_or_create(
                db=db,
                calendar=calendar_data_b,
                calendar_url=shared_calendar_url,
                subscriber_id=subscriber_b.id,
                external_connection_id=ec_b.id,
            )

            # Verify Subscriber A's calendar was not modified
            calendars_a = repo.calendar.get_by_subscriber(db, subscriber_a.id)
            assert len(calendars_a) == 1
            assert calendars_a[0].title == 'Original Title A'
            assert calendars_a[0].color == '#4285f4'
            assert calendars_a[0].external_connection_id == ec_a.id
