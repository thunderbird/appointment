import os

import pytest

from appointment.database.models import CalendarProvider
from appointment.controller.calendar import CalDavConnector, GoogleConnector
from appointment.database import schemas, models

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
        def __init__(self, subscriber_id, calendar_id, redis_instance, url, user, password):
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
    @pytest.mark.parametrize('mock_connector,connector,provider,test_url,test_user', get_mock_connector_class())
    def test_read_remote_calendars(
        self,
        monkeypatch,
        with_client,
        mock_connector,
        connector,
        provider,
        test_url,
        test_user,
        make_external_connections,
    ):
        # Ensure we have an external connection for google
        if provider == schemas.CalendarProvider.google.value:
            make_external_connections(TEST_USER_ID, type=schemas.ExternalConnectionType.google)

        # Patch up the caldav constructor, and list_calendars
        monkeypatch.setattr(connector, '__init__', mock_connector.__init__)
        monkeypatch.setattr(connector, 'list_calendars', mock_connector.list_calendars)

        response = with_client.post(
            '/rmt/calendars',
            json={
                'provider': provider,
                'url': test_url,
                'user': test_user,
                'password': 'caw',
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(c['url'] == test_url for c in data)
        assert any(c['provider'] == provider for c in data)

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
        assert 'url' not in calendar
        assert 'user' not in calendar
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
        assert 'url' not in data
        assert 'user' not in data
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
        assert 'url' not in calendar
        assert 'user' not in calendar
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
        assert 'url' not in data
        assert 'user' not in data
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


class TestCaldav:
    """Tests for caldav specific functionality"""

    def test_create_first_caldav_calendar(self, with_client):
        response = with_client.post(
            '/cal',
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
        assert 'url' not in data
        assert 'user' not in data
        assert 'password' not in data

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
        assert 'url' not in data
        assert 'user' not in data
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
        assert 'url' not in data
        assert 'user' not in data
        assert 'password' not in data

        query = select(models.Calendar).where(models.Calendar.id == generated_calendar.id)

        with with_db() as db:
            cal = db.scalars(query).one()

        assert cal.url == os.getenv('CALDAV_TEST_CALENDAR_URL')
        assert cal.user == os.getenv('CALDAV_TEST_USER')
        assert cal.password == ''
