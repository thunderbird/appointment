import json
import os
from unittest.mock import patch, MagicMock

from appointment.controller.calendar import CalDavConnector, Tools
from appointment.database import models
from appointment.exceptions.calendar import TestConnectionFailed

from sqlalchemy import select

from defines import auth_headers, TEST_USER_ID


class TestOidcAutodiscoverAuth:
    """Tests for POST /caldav/oidc/auth"""

    def _mock_tb_accounts_success(self, app_password='test-app-password'):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'app_password': app_password}
        mock_response.raise_for_status = MagicMock()
        return mock_response

    def _mock_tb_accounts_failure(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': False}
        mock_response.raise_for_status = MagicMock()
        return mock_response

    def test_successful_oidc_auth_creates_external_connection(self, with_client, with_db, monkeypatch):
        """Full OIDC auth flow: DNS lookup, TB Accounts call, connection test, external connection creation."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        class MockCalDavConnector:
            @staticmethod
            def __init__(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
                pass

            @staticmethod
            def test_connection(self):
                return True

            @staticmethod
            def sync_calendars(self, external_connection_id=None):
                pass

        monkeypatch.setattr(CalDavConnector, '__init__', MockCalDavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, 'test_connection', MockCalDavConnector.test_connection)
        monkeypatch.setattr(CalDavConnector, 'sync_calendars', MockCalDavConnector.sync_calendars)

        with patch('appointment.routes.caldav.requests.post', return_value=self._mock_tb_accounts_success()):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 200, response.text
        assert response.json() is True

        with with_db() as db:
            ecs = db.scalars(
                select(models.ExternalConnections).where(
                    models.ExternalConnections.owner_id == TEST_USER_ID,
                    models.ExternalConnections.type == models.ExternalConnectionType.caldav,
                )
            ).all()
            assert len(ecs) == 1
            assert ecs[0].name == os.getenv('TEST_USER_EMAIL')

    def test_oidc_auth_updates_existing_external_connection(
        self, with_client, with_db, monkeypatch, make_external_connections
    ):
        """When an external connection already exists, its token should be updated."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        subscriber_email = os.getenv('TEST_USER_EMAIL')
        caldav_id = json.dumps(['https://caldav.test.example', subscriber_email])
        make_external_connections(
            subscriber_id=TEST_USER_ID,
            name=subscriber_email,
            type=models.ExternalConnectionType.caldav,
            type_id=caldav_id,
            token='old-password',
        )

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        class MockCalDavConnector:
            @staticmethod
            def __init__(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
                pass

            @staticmethod
            def test_connection(self):
                return True

            @staticmethod
            def sync_calendars(self, external_connection_id=None):
                pass

        monkeypatch.setattr(CalDavConnector, '__init__', MockCalDavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, 'test_connection', MockCalDavConnector.test_connection)
        monkeypatch.setattr(CalDavConnector, 'sync_calendars', MockCalDavConnector.sync_calendars)

        new_password = 'new-app-password'
        with patch(
            'appointment.routes.caldav.requests.post',
            return_value=self._mock_tb_accounts_success(app_password=new_password),
        ):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 200, response.text

        with with_db() as db:
            ecs = db.scalars(
                select(models.ExternalConnections).where(
                    models.ExternalConnections.owner_id == TEST_USER_ID,
                    models.ExternalConnections.type == models.ExternalConnectionType.caldav,
                )
            ).all()
            assert len(ecs) == 1
            assert ecs[0].token == new_password

    def test_oidc_auth_missing_tb_accounts_host(self, with_client, monkeypatch):
        """Should raise RemoteCalendarConnectionError when TB_ACCOUNTS_HOST is missing."""
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')
        monkeypatch.delenv('TB_ACCOUNTS_HOST', raising=False)
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        response = with_client.post('/caldav/oidc/auth', headers=auth_headers)
        assert response.status_code == 400, response.text
        assert response.json()['detail']['id'] == 'REMOTE_CALENDAR_CONNECTION_ERROR'

    def test_oidc_auth_missing_caldav_secret(self, with_client, monkeypatch):
        """Should raise RemoteCalendarConnectionError when APPOINTMENT_CALDAV_SECRET is missing."""
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.delenv('APPOINTMENT_CALDAV_SECRET', raising=False)

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        response = with_client.post('/caldav/oidc/auth', headers=auth_headers)
        assert response.status_code == 400, response.text
        assert response.json()['detail']['id'] == 'REMOTE_CALENDAR_CONNECTION_ERROR'

    def test_oidc_auth_tb_accounts_returns_unsuccessful(self, with_client, monkeypatch):
        """Should raise RemoteCalendarConnectionError when TB Accounts returns success=False."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        with patch('appointment.routes.caldav.requests.post', return_value=self._mock_tb_accounts_failure()):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 400, response.text
        assert response.json()['detail']['id'] == 'REMOTE_CALENDAR_CONNECTION_ERROR'

    def test_oidc_auth_tb_accounts_request_exception(self, with_client, monkeypatch):
        """Should raise RemoteCalendarConnectionError when the request to TB Accounts fails."""
        import requests as req

        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        with patch('appointment.routes.caldav.requests.post', side_effect=req.ConnectionError('connection failed')):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 400, response.text
        assert response.json()['detail']['id'] == 'REMOTE_CALENDAR_CONNECTION_ERROR'

    def test_oidc_auth_connection_test_fails(self, with_client, monkeypatch):
        """Should raise RemoteCalendarConnectionError when CalDAV connection test fails."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        def mock_test_connection(self):
            return False

        monkeypatch.setattr(CalDavConnector, 'test_connection', mock_test_connection)

        with patch('appointment.routes.caldav.requests.post', return_value=self._mock_tb_accounts_success()):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 400, response.text
        assert response.json()['detail']['id'] == 'REMOTE_CALENDAR_CONNECTION_ERROR'

    def test_oidc_auth_connection_test_raises_exception(self, with_client, monkeypatch):
        """Should raise RemoteCalendarConnectionError with reason when TestConnectionFailed is raised."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        def mock_test_connection(self):
            raise TestConnectionFailed(reason='server unreachable')

        monkeypatch.setattr(CalDavConnector, 'test_connection', mock_test_connection)

        with patch('appointment.routes.caldav.requests.post', return_value=self._mock_tb_accounts_success()):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 400, response.text
        assert response.json()['detail']['id'] == 'REMOTE_CALENDAR_CONNECTION_ERROR'

    def test_oidc_auth_uses_dns_lookup_url(self, with_client, monkeypatch):
        """When DNS lookup returns a result, it should be applied to the connection URL."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        captured_urls = []

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: ('https://resolved.test.example/dav', 300))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)

        def capturing_init(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
            captured_urls.append(url)

        monkeypatch.setattr(CalDavConnector, '__init__', capturing_init)
        monkeypatch.setattr(CalDavConnector, 'test_connection', lambda self: True)
        monkeypatch.setattr(CalDavConnector, 'sync_calendars', lambda self, **kw: None)

        with patch('appointment.routes.caldav.requests.post', return_value=self._mock_tb_accounts_success()):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 200, response.text
        assert len(captured_urls) == 1
        assert captured_urls[0] == 'https://resolved.test.example/dav'

    def test_oidc_auth_uses_well_known_fallback(self, with_client, monkeypatch):
        """When DNS lookup returns None, well-known lookup should be tried."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'test-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        captured_urls = []

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(
            Tools, 'well_known_caldav_lookup', lambda *a, **kw: 'https://wellknown.test.example/caldav'
        )

        def capturing_init(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
            captured_urls.append(url)

        monkeypatch.setattr(CalDavConnector, '__init__', capturing_init)
        monkeypatch.setattr(CalDavConnector, 'test_connection', lambda self: True)
        monkeypatch.setattr(CalDavConnector, 'sync_calendars', lambda self, **kw: None)

        with patch('appointment.routes.caldav.requests.post', return_value=self._mock_tb_accounts_success()):
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 200, response.text
        assert len(captured_urls) == 1
        assert captured_urls[0] == 'https://wellknown.test.example/caldav'

    def test_oidc_auth_sends_correct_payload_to_tb_accounts(self, with_client, monkeypatch):
        """Verify the request to TB Accounts contains the correct payload."""
        monkeypatch.setenv('TB_ACCOUNTS_HOST', 'https://accounts.test.example')
        monkeypatch.setenv('APPOINTMENT_CALDAV_SECRET', 'my-secret')
        monkeypatch.setenv('TB_ACCOUNTS_CALDAV_URL', 'https://caldav.test.example')

        monkeypatch.setattr(Tools, 'dns_caldav_lookup', lambda *a, **kw: (None, None))
        monkeypatch.setattr(Tools, 'well_known_caldav_lookup', lambda *a, **kw: None)
        monkeypatch.setattr(CalDavConnector, '__init__', lambda self, **kw: None)
        monkeypatch.setattr(CalDavConnector, 'test_connection', lambda self: True)
        monkeypatch.setattr(CalDavConnector, 'sync_calendars', lambda self, **kw: None)

        with patch('appointment.routes.caldav.requests.post', return_value=self._mock_tb_accounts_success()) as mock_post:
            response = with_client.post('/caldav/oidc/auth', headers=auth_headers)

        assert response.status_code == 200, response.text
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://accounts.test.example/appointment/caldav/setup/'
        assert call_args[1]['json']['appointment-secret'] == 'my-secret'
        assert call_args[1]['json']['oidc-access-token'] == 'testtokenplsignore'

    def test_oidc_auth_requires_authentication(self, with_client, monkeypatch):
        """Request without auth headers should be rejected."""
        response = with_client.post('/caldav/oidc/auth')
        assert response.status_code == 401, response.text

