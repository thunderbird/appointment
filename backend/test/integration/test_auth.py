import os

from appointment.l10n import l10n
from defines import FXA_CLIENT_PATCH, auth_headers
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

    def test_fxa_callback(self, with_db, with_client, monkeypatch, make_invite):
        """Test that our callback function correctly handles the session states, and creates a new subscriber"""
        os.environ['AUTH_SCHEME'] = 'fxa'

        state = 'a1234'

        invite = make_invite()

        monkeypatch.setattr('starlette.requests.HTTPConnection.session', {
            'fxa_state': state,
            'fxa_user_email': FXA_CLIENT_PATCH.get('subscriber_email'),
            'fxa_user_timezone': 'America/Vancouver',
            'fxa_user_invite_code': invite.code,
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

    def test_fxa_callback_with_mismatch_uid(self, with_db, with_client, monkeypatch, make_external_connections,
                                            make_basic_subscriber, with_l10n):
        """Test that our fxa callback will throw an invalid-credentials error if the incoming fxa uid doesn't match any existing ones."""
        os.environ['AUTH_SCHEME'] = 'fxa'

        state = 'a1234'

        subscriber = make_basic_subscriber(email=FXA_CLIENT_PATCH.get('subscriber_email'))

        mismatch_uid = f"{FXA_CLIENT_PATCH.get('external_connection_type_id')}-not-actually"
        make_external_connections(subscriber.id, type=models.ExternalConnectionType.fxa, type_id=mismatch_uid)

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

        # This should error out as a 403
        assert response.status_code == 403, response.text
        # This will just key match due to the lack of context.
        assert response.json().get('detail') == l10n('invalid-credentials')

    def test_permission_check_with_no_admin_email(self, with_client):
        os.environ['APP_ADMIN_ALLOW_LIST'] = ''

        response = with_client.post('/permission-check',
                                    headers=auth_headers)
        assert response.status_code == 401, response.text

    def test_permission_check_with_wrong_admin_email(self, with_client):
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.post('/permission-check',
                                    headers=auth_headers)
        assert response.status_code == 401, response.text

    def test_permission_check_with_correct_admin_email(self, with_client):
        os.environ['APP_ADMIN_ALLOW_LIST'] = f"@{os.getenv('TEST_USER_EMAIL').split('@')[1]}"

        response = with_client.post('/permission-check',
                                    headers=auth_headers)
        assert response.status_code == 200, response.text

    def test_permission_check_with_correct_full_admin_email(self, with_client):
        os.environ['APP_ADMIN_ALLOW_LIST'] = os.getenv('TEST_USER_EMAIL')

        response = with_client.post('/permission-check',
                                    headers=auth_headers)
        assert response.status_code == 200, response.text
