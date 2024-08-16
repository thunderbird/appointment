import os
import pytest
from itsdangerous import URLSafeSerializer
from sqlalchemy.exc import InvalidRequestError

from appointment.database import models, schemas
from unittest.mock import patch

from appointment.dependencies.auth import get_admin_subscriber, get_subscriber
from appointment.routes.auth import create_access_token
from appointment.routes.waiting_list import WaitingListAction
from appointment.tasks.emails import send_confirm_email, send_invite_account_email
from defines import auth_headers


class TestJoinWaitingList:
    def test_success(self, with_db, with_client):
        email = 'hello@example.org'
        with with_db() as db:
            assert not db.query(models.WaitingList).filter(models.WaitingList.email == email).first()

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            response = with_client.post('/waiting-list/join', json={'email': email})

            # Ensure the response was okay!
            assert response.status_code == 200, response.json()
            assert response.json() is True

            # Ensure our email was inserted
            with with_db() as db:
                assert db.query(models.WaitingList).filter(models.WaitingList.email == email).first() is not None

            # Ensure we sent out an email
            mock.assert_called_once()

    def test_already_in_list(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'
        with with_db() as db:
            assert not db.query(models.WaitingList).filter(models.WaitingList.email == email).first()

        make_waiting_list(email=email)

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            response = with_client.post('/waiting-list/join', json={'email': email})

            # Ensure the response was okay!
            assert response.status_code == 200, response.json()
            assert response.json() is False

            # Ensure we did not send out an email
            mock.assert_not_called()


class TestWaitingListActionConfirm:
    def assert_email_verified(self, db, waiting_list, success=True):
        assert not waiting_list.email_verified

        db.add(waiting_list)
        db.refresh(waiting_list)

        if success:
            assert waiting_list.email_verified
        else:
            assert not waiting_list.email_verified

    def test_success(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'

        waiting_list = make_waiting_list(email=email)

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': WaitingListAction.CONFIRM_EMAIL.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was okay!
        assert response.status_code == 200, response.json()
        assert response.json() == { "action": WaitingListAction.CONFIRM_EMAIL.value, "success": True }

        with with_db() as db:
            self.assert_email_verified(db, waiting_list, success=True)

    def test_bad_secret(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'

        waiting_list = make_waiting_list(email=email)

        serializer = URLSafeSerializer('wow-a-fake-secret', 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': WaitingListAction.CONFIRM_EMAIL.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was not okay!
        assert response.status_code == 400, response.json()

        # They shouldn't be verified before or after the db fetch
        with with_db() as db:
            self.assert_email_verified(db, waiting_list, success=False)

    def test_bad_token_data_invalid_action(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'

        waiting_list = make_waiting_list(email=email)

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': 999})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was not okay!
        assert response.status_code == 400, response.json()

        # They shouldn't be verified before or after the db fetch
        with with_db() as db:
            self.assert_email_verified(db, waiting_list, success=False)

    def test_bad_token_data_missing_email(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'

        waiting_list = make_waiting_list(email=email)

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'action': WaitingListAction.CONFIRM_EMAIL.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was not okay!
        assert response.status_code == 400, response.json()

        # They shouldn't be verified before or after the db fetch
        with with_db() as db:
            self.assert_email_verified(db, waiting_list, success=False)

    def test_bad_token_data_email_not_in_list(self, with_db, with_client):
        email = 'hello@example.org'

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': WaitingListAction.CONFIRM_EMAIL.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was not okay!
        assert response.status_code == 400, response.json()

        # They shouldn't be verified before or after the db fetch
        with with_db() as db:
            assert not db.query(models.WaitingList).filter(models.WaitingList.email == email).first()


class TestWaitingListActionLeave:
    def assert_waiting_list_exists(self, db, waiting_list, success=True):
        assert waiting_list
        email = waiting_list.email

        db.add(waiting_list)
        if success:
            with pytest.raises(InvalidRequestError):
                db.refresh(waiting_list)

            assert not db.query(models.WaitingList).filter(models.WaitingList.email == email).first()
        else:
            db.refresh(waiting_list)
            assert waiting_list is not None

    def test_success(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'

        waiting_list = make_waiting_list(email=email)

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': WaitingListAction.LEAVE.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was okay!
        assert response.status_code == 200, response.json()
        assert response.json() == {"action": WaitingListAction.LEAVE.value, "success": True}

        with with_db() as db:
            self.assert_waiting_list_exists(db, waiting_list, success=True)

    def test_bad_token_data_email_not_in_list(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': WaitingListAction.LEAVE.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was okay!
        assert response.status_code == 200, response.json()
        assert response.json() == { "action": WaitingListAction.LEAVE.value, "success": True }

        with with_db() as db:
            assert not db.query(models.WaitingList).filter(models.WaitingList.email == email).first()

    def test_already_is_a_subscriber(self, with_db, with_client, make_waiting_list, make_basic_subscriber, make_invite):
        """Someone is who already a subscriber should be notified to delete their accounts in the settings page!"""
        email = 'hello@example.org'

        sub = make_basic_subscriber(email=email)
        invite = make_invite(subscriber_id=sub.id)
        _waiting_list = make_waiting_list(email=email, invite_id=invite.id)

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': WaitingListAction.LEAVE.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was okay!
        assert response.status_code == 200, response.json()
        assert response.json() == { "action": WaitingListAction.LEAVE.value, "success": False, "redirectToSettings": True }


class TestWaitingListAdminView:
    def test_view_with_admin(self, with_client, with_db, with_l10n, make_waiting_list):
        os.environ['APP_ADMIN_ALLOW_LIST'] = os.getenv('TEST_USER_EMAIL')

        waiting_list_user = make_waiting_list()

        response = with_client.get('/waiting-list/', headers=auth_headers)

        # Ensure the response was okay!
        data = response.json()

        assert response.status_code == 200, data
        assert len(data) > 0
        assert 'id' in data[0]
        assert data[0]['id'] == waiting_list_user.id

    def test_view_with_admin_non_admin(self, with_client, with_db, with_l10n, make_waiting_list):
        os.environ['APP_ADMIN_ALLOW_LIST'] = f"{os.getenv('TEST_USER_EMAIL')}-naw.com"

        make_waiting_list()

        response = with_client.get('/waiting-list/', headers=auth_headers)

        # Ensure the response was okay!
        data = response.json()

        assert response.status_code == 401, data


class TestWaitingListAdminInvite:
    def test_invite_one_user(self, with_client, with_db, with_l10n, make_waiting_list):
        """Test a successful invitation of one user"""
        os.environ['APP_ADMIN_ALLOW_LIST'] = os.getenv('TEST_USER_EMAIL')

        waiting_list_user = make_waiting_list()

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            response = with_client.post('/waiting-list/invite',
                                        json={
                                            'id_list': [waiting_list_user.id]
                                        },
                                        headers=auth_headers)

            # Ensure the response was okay!
            data = response.json()

            assert response.status_code == 200, data
            assert len(data['accepted']) == 1
            assert len(data['errors']) == 0
            assert data['accepted'][0] == waiting_list_user.id

            # Ensure we sent out an email
            mock.assert_called_once()
            # Triple access D:, one for ArgList, one for Call<Function, Args...>), and then the function is in a tuple?!
            assert mock.call_args_list[0][0][0] == send_invite_account_email
            assert mock.call_args_list[0].kwargs == {'to': waiting_list_user.email}

        with with_db() as db:
            db.add(waiting_list_user)
            db.refresh(waiting_list_user)

            assert waiting_list_user.invite_id
            assert waiting_list_user.invite.subscriber_id
            assert waiting_list_user.invite.subscriber.email == waiting_list_user.email

    def test_invite_many_users(self, with_client, with_db, with_l10n, make_waiting_list):
        """Test a successful invite of many users"""
        os.environ['APP_ADMIN_ALLOW_LIST'] = os.getenv('TEST_USER_EMAIL')

        waiting_list_users = [ make_waiting_list().id for i in range(0, 10) ]

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            response = with_client.post('/waiting-list/invite',
                                        json={
                                            'id_list': waiting_list_users
                                        },
                                        headers=auth_headers)

            # Ensure the response was okay!
            data = response.json()

            assert response.status_code == 200, data
            assert len(data['accepted']) == len(waiting_list_users)
            assert len(data['errors']) == 0

            for i, id in enumerate(waiting_list_users):
                assert data['accepted'][i] == id

            # Ensure we sent out an email
            mock.assert_called()

            with with_db() as db:
                for i, id in enumerate(waiting_list_users):
                    waiting_list_user = db.query(models.WaitingList).filter(models.WaitingList.id == id).first()

                    assert waiting_list_user
                    assert waiting_list_user.invite_id
                    assert waiting_list_user.invite.subscriber_id
                    assert waiting_list_user.invite.subscriber.email == waiting_list_user.email

                    assert mock.call_args_list[i][0][0] == send_invite_account_email
                    assert mock.call_args_list[i].kwargs == {'to': waiting_list_user.email}

    def test_invite_existing_subscriber(self, with_client, with_db, with_l10n, make_waiting_list, make_basic_subscriber):
        os.environ['APP_ADMIN_ALLOW_LIST'] = os.getenv('TEST_USER_EMAIL')

        sub = make_basic_subscriber()
        waiting_list_user = make_waiting_list(email=sub.email)

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            response = with_client.post('/waiting-list/invite',
                                        json={
                                            'id_list': [waiting_list_user.id]
                                        },
                                        headers=auth_headers)

            # Ensure the response was okay!
            data = response.json()

            assert response.status_code == 200, data
            assert len(data['accepted']) == 0
            assert len(data['errors']) == 1

            assert sub.email in data['errors'][0]

            mock.assert_not_called()

    def test_invite_many_users_with_one_existing_subscriber(self, with_client, with_db, with_l10n, make_waiting_list, make_basic_subscriber):
        os.environ['APP_ADMIN_ALLOW_LIST'] = os.getenv('TEST_USER_EMAIL')

        sub = make_basic_subscriber()
        waiting_list_users = [ make_waiting_list().id for i in range(0, 10) ]
        waiting_list_users.append(make_waiting_list(email=sub.email).id)

        with patch('fastapi.BackgroundTasks.add_task') as mock:

            response = with_client.post('/waiting-list/invite',
                                        json={
                                            'id_list': waiting_list_users
                                        },
                                        headers=auth_headers)

            # Ensure the response was okay!
            data = response.json()

            assert response.status_code == 200, data
            assert len(data['accepted']) == len(waiting_list_users) - 1
            assert len(data['errors']) == 1

            for i, id in enumerate(waiting_list_users):
                # Last entry was an error!
                if i == 10:
                    # Should be in the error list, and it shouldn't have called add_task
                    assert sub.email in data['errors'][0]
                    assert i not in mock.call_args_list
                else:
                    assert data['accepted'][i] == id

                    with with_db() as db:
                        waiting_list_user = db.query(models.WaitingList).filter(models.WaitingList.id == id).first()

                        assert waiting_list_user
                        assert mock.call_args_list[i][0][0] == send_invite_account_email
                        assert mock.call_args_list[i].kwargs == {'to': waiting_list_user.email}

