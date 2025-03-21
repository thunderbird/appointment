import os
import pytest
from defines import DAY1, DAY5, auth_headers


class TestGeneral:
    def test_config(self):
        assert int(os.getenv('TIER_BASIC_CALENDAR_LIMIT')) == 3
        assert int(os.getenv('TIER_PLUS_CALENDAR_LIMIT')) == 5
        assert int(os.getenv('TIER_PRO_CALENDAR_LIMIT')) == 10
        assert os.getenv('TEST_USER_EMAIL') is not None

    def test_health(self, with_client):
        # existing root route
        response = with_client.get('/')
        assert response.status_code == 200
        assert response.json()
        # undefined route
        response = with_client.get('/abcdefg')
        assert response.status_code == 404

    def test_health_for_locale(self, with_client):
        # Try english first
        response = with_client.get('/', headers={'accept-language': 'en'})
        assert response.status_code == 200
        assert response.json() == 'Health OK'

        # Try german next
        response = with_client.get('/', headers={'accept-language': 'de'})
        assert response.status_code == 200
        assert response.json() == 'Zustand in Ordnung'

    @pytest.mark.parametrize('api_method, api_route', [
        ('get', '/me'),
        ('put', '/me'),
        ('get', '/me/calendars'),
        ('get', '/me/appointments'),
        ('get', '/me/signature'),
        ('post', '/me/signature'),
        ('post', '/cal'),
        ('get', '/cal/1'),
        ('put', '/cal/1'),
        ('post', '/cal/1/connect'),
        ('delete', '/cal/1'),
        ('post', '/caldav/auth'),
        ('post', '/caldav/disconnect'),
        ('post', '/rmt/calendars'),
        ('get', '/rmt/cal/1/' + DAY1 + '/' + DAY5),
        ('post', '/rmt/sync'),
        ('get', '/account/available-emails'),
        ('post', '/account/download'),
        ('get', '/account/external-connections/'),
        ('delete', '/account/delete'),
        ('get', '/google/auth'),
        ('post', '/google/disconnect'),
        ('post', '/schedule'),
        ('get', '/schedule'),
        ('get', '/schedule/0'),
        ('put', '/schedule/0'),
        ('post', '/invite'),
        ('post', '/invite/generate/1'),
        ('put', '/invite/revoke/1'),
        ('post', '/subscriber'),
        ('put', '/subscriber/enable/someemail@email.com'),
        ('put', '/subscriber/disable/someemail@email.com'),
        ('post', '/subscriber/setup'),
        ('post', '/waiting-list/invite'),
    ])
    def test_access_without_authentication_token(self, with_client, api_method, api_route):
        if api_method == 'post':
            response = with_client.post(f'{api_route}')
        elif api_method == 'get':
            response = with_client.get(f'{api_route}')
        elif api_method == 'put':
            response = with_client.put(f'{api_route}')
        else:
            response = with_client.delete(f'{api_route}')
        assert response.status_code == 401

    def test_send_feedback(self, with_client):
        response = with_client.post(
            '/support', json={'topic': 'Hello World', 'details': 'Hello World but longer'}, headers=auth_headers
        )
        assert response.status_code == 200

    def test_send_feedback_no_email_configured(self, with_client):
        """Attempt to send feedback with no support email configured; expect error"""
        saved_email = os.environ['SUPPORT_EMAIL']
        os.environ['SUPPORT_EMAIL'] = ''
        response = with_client.post(
            '/support', json={'topic': 'Hello World', 'details': 'Hello World but longer'}, headers=auth_headers
        )
        os.environ['SUPPORT_EMAIL'] = saved_email
        assert response.status_code == 500
