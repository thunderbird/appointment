import os
import pytest
from itsdangerous import URLSafeSerializer
from sqlalchemy.exc import InvalidRequestError

from appointment.database import models
from unittest.mock import patch

from appointment.routes.waiting_list import WaitingListAction


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
        assert response.json() is True

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
        assert response.json() is True

        with with_db() as db:
            self.assert_waiting_list_exists(db, waiting_list, success=True)

    def test_bad_token_data_email_not_in_list(self, with_db, with_client, make_waiting_list):
        email = 'hello@example.org'

        serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
        confirm_token = serializer.dumps({'email': email, 'action': WaitingListAction.LEAVE.value})

        response = with_client.post('/waiting-list/action', json={'token': confirm_token})

        # Ensure the response was okay!
        assert response.status_code == 200, response.json()
        assert response.json() is True

        with with_db() as db:
            assert not db.query(models.WaitingList).filter(models.WaitingList.email == email).first()
