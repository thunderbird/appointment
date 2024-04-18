import os

from defines import FXA_CLIENT_PATCH
from appointment.database import repo, models


class TestAuth:
    def test_token(self, with_db, with_client, make_pro_subscriber):
        """Test that our username/password authentication works correctly."""
        password = 'test'
        bad_password = 'test2'

        subscriber = make_pro_subscriber(password=password)

        # Test good credentials
        response = with_client.post(
            "/token",
            data={
                'username': subscriber.username,
                'password': password
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["access_token"]
        assert data["token_type"] == 'bearer'

        # Test bad credentials
        response = with_client.post(
            "/token",
            data={
                'username': subscriber.username,
                'password': bad_password
            },
        )
        assert response.status_code == 403, response.text

        # Test credentials with non-existent user
        response = with_client.post(
            "/token",
            data={
                'username': subscriber.username + "1",
                'password': password
            },
        )
        assert response.status_code == 403, response.text

    def test_fxa_login(self, with_client):
        os.environ['AUTH_SCHEME'] = 'fxa'
        response = with_client.get(
            "/fxa_login",
            params={
                'email': FXA_CLIENT_PATCH.get('subscriber_email'),
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert 'url' in data
        assert data.get('url') == FXA_CLIENT_PATCH.get('authorization_url')

    def test_fxa_callback(self, with_db, with_client, monkeypatch):
        """Test that our callback function correctly handles the session states, and creates a new subscriber"""
        os.environ['AUTH_SCHEME'] = 'fxa'

        state = 'a1234'

        monkeypatch.setattr('starlette.requests.HTTPConnection.session', {
            'fxa_state': state,
            'fxa_user_email': FXA_CLIENT_PATCH.get('subscriber_email'),
            'fxa_user_timezone': 'America/Vancouver'
        })

        response = with_client.get(
            "/fxa",
            params={
                'code': FXA_CLIENT_PATCH.get('credentials_code'),
                'state': state
            },
            follow_redirects=False
        )
        # This is a redirect request
        assert response.status_code == 307, response.text

        with with_db() as db:
            subscriber = repo.subscriber.get_by_email(db, FXA_CLIENT_PATCH.get('subscriber_email'))
            assert subscriber
            assert subscriber.avatar_url == FXA_CLIENT_PATCH.get('subscriber_avatar_url')
            assert subscriber.name == FXA_CLIENT_PATCH.get('subscriber_display_name')
            fxa = subscriber.get_external_connection(models.ExternalConnectionType.fxa)
            assert fxa
            assert fxa.type_id == FXA_CLIENT_PATCH.get('external_connection_type_id')
