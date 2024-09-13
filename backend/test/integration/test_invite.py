import os
from defines import auth_headers, TEST_USER_ID
from appointment.database import repo


class TestInvite:
    def test_send_invite_email_requires_admin(self, with_db, with_client):
        """Ensures send_invite_email requires an admin user"""

        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.post(
            '/invite/send',
            json={'email': 'beatrice@ismycat.meow'},
            headers=auth_headers,
        )
        assert response.status_code == 401, response.text

    def test_send_invite_email_requires_at_least_one_admin_email(self, with_db, with_client):
        """Ensures send_invite_email requires an admin user"""

        os.environ['APP_ADMIN_ALLOW_LIST'] = ''

        response = with_client.post(
            '/invite/send',
            json={'email': 'beatrice@ismycat.meow'},
            headers=auth_headers,
        )
        assert response.status_code == 401, response.text

    def test_send_invite_email(self, with_db, with_client):
        """Ensures send_invite_email requires an admin user"""

        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        invite_email = 'beatrice@ismycat.meow'

        with with_db() as db:
            subscriber = repo.subscriber.get_by_email(db, invite_email)
            assert subscriber is None

        response = with_client.post(
            '/invite/send',
            json={'email': invite_email},
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text

        with with_db() as db:
            subscriber = repo.subscriber.get_by_email(db, invite_email)
            assert subscriber is not None


class TestPublicInvites:
    def test_empty(self, with_client):
        response = with_client.get(
            '/me/invites',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == []

    def test_invites_show(self, with_client, make_invite):
        invites = [make_invite(owner_id=TEST_USER_ID) for _ in range(2)]

        response = with_client.get(
            '/me/invites',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(invites)
        assert data[0]['code'] == invites[0].code
        assert data[1]['code'] == invites[1].code

    def test_used_invites_dont_show(self, with_client, make_invite, make_basic_subscriber):
        invite = make_invite(owner_id=TEST_USER_ID)

        other_guy = make_basic_subscriber()
        other_invite = make_invite(owner_id=TEST_USER_ID, subscriber_id=other_guy.id)

        response = with_client.get(
            '/me/invites',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data[0]['code'] != other_invite.code
        assert data[0]['code'] == invite.code

    def test_only_code_and_status_are_shown(self, with_client, make_invite):
        invite = make_invite(owner_id=TEST_USER_ID)

        response = with_client.get(
            '/me/invites',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data[0]['code'] == invite.code
        assert list(data[0].keys()) == ['code', 'status']
