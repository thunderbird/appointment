import os
from defines import auth_headers
from backend.src.appointment.database import repo


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
