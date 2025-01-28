import os
from datetime import datetime
from defines import auth_headers, TEST_USER_ID
from appointment.database import repo
from appointment.database.models import InviteStatus

class TestInvite:
    today = today = datetime.today().date()

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

    def test_send_invite_email_subscriber_already_exists(self, with_db, with_client, make_pro_subscriber):
        """Ensures send_invite_email fails if subscriber already exists"""

        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        the_other_guy = make_pro_subscriber()

        response = with_client.post(
            '/invite/send',
            json={'email': the_other_guy.email},
            headers=auth_headers,
        )
        assert response.status_code == 400, response.text
        data = response.json()
        assert data['detail']['id'] == 'CREATE_SUBSCRIBER_ALREADY_EXISTS'

    def test_send_invite_email_subscriber_fails(self, with_db, with_client):
        """Ensures send_invite_email fails if invite email is invalid"""

        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        invite_email = 'hi'

        response = with_client.post(
            '/invite/send',
            json={'email': invite_email},
            headers=auth_headers,
        )
        assert response.status_code == 422, response.text
        data = response.json()
        assert 'not a valid email address' in data['detail'][0]['msg']

    def test_get_all_invites_requires_admin(self, with_db, with_client):
        """Ensures getting all invites requires an admin user"""

        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.get(
            '/invite',
            headers=auth_headers,
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'

    def test_get_all_invites(self, with_db, with_client, make_invite):
        """Ensures we can get all invites"""
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        invites = [make_invite(owner_id=TEST_USER_ID) for _ in range(2)]
        assert invites is not None

        response = with_client.get(
            '/invite',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        invite_list = response.json()
        assert len(invite_list) == 2
        assert invite_list[0]['code'] != invite_list[1]['code']

        for next_invite in invite_list:
            assert next_invite['owner_id'] == TEST_USER_ID
            assert next_invite['code'] is not None
            date_created = datetime.fromisoformat(next_invite['time_created']).date()
            assert date_created == self.today

    def test_generate_invites(self, with_client):
        """Ensures we can generate new invites"""
        response = with_client.post(
            '/invite/generate/5',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        invite_list = response.json()
        assert len(invite_list) == 5

        for next_invite in invite_list:
            assert next_invite['status'] == InviteStatus.active.value
            assert next_invite['code'] is not None
            date_created = datetime.fromisoformat(next_invite['time_created']).date()
            assert date_created == self.today

        response = with_client.get(
            '/invite',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 5

    def test_revoke_invite(self, with_db, with_client, make_invite):
        """Ensures we can revoke an invite code"""
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        test_invite = make_invite(owner_id=TEST_USER_ID)
        assert test_invite.status == InviteStatus.active

        response = with_client.put(
            f'/invite/revoke/{test_invite.code}',
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text

        # verify our invite now has a status of revoked
        response = with_client.get(
            '/invite',
            headers=auth_headers,
        )

        assert response.status_code == 200, response.text
        invite_list = response.json()
        assert len(invite_list) == 1
        assert invite_list[0]['status'] == InviteStatus.revoked.value

        # attempt to revoke the same already-revoked invite code, expect fail
        response = with_client.put(
            f'/invite/revoke/{test_invite.code}',
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVITE_CODE_NOT_AVAILABLE'


    def test_revoke_invite_not_found(self, with_db, with_client, make_invite):
        """Ensures revoking an invite code fails if code is invalid"""
        response = with_client.put(
            '/invite/revoke/99999',
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVITE_CODE_NOT_FOUND'


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
