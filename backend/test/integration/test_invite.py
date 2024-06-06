import os
from defines import auth_headers
from appointment.database import repo


class TestInvite:
    def test_send_invite_email_requires_admin(self, with_db, with_client):
        """Ensures send_invite_email requires an admin user"""

        os.environ["APP_ADMIN_ALLOW_LIST"] = "@notexample.org"

        response = with_client.post(
            "/invite/send",
            json={"email": "beatrice@ismycat.meow"},
            headers=auth_headers,
        )
        assert response.status_code == 401, response.text

    def test_send_invite_email_requires_at_least_one_admin_email(self, with_db, with_client):
        """Ensures send_invite_email requires an admin user"""

        os.environ["APP_ADMIN_ALLOW_LIST"] = ""

        response = with_client.post(
            "/invite/send",
            json={"email": "beatrice@ismycat.meow"},
            headers=auth_headers,
        )
        assert response.status_code == 401, response.text

    def test_send_invite_email(self, with_db, with_client):
        """Ensures send_invite_email requires an admin user"""

        os.environ["APP_ADMIN_ALLOW_LIST"] = "@example.org"

        invite_email = "beatrice@ismycat.meow"

        with with_db() as db:
            subscriber = repo.subscriber.get_by_email(db, invite_email)
            assert subscriber is None

        response = with_client.post(
            "/invite/send",
            json={"email": invite_email},
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text

        with with_db() as db:
            subscriber = repo.subscriber.get_by_email(db, invite_email)
            assert subscriber is not None
