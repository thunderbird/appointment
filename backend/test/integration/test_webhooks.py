import datetime
import os

import pytest
from freezegun import freeze_time
from appointment.database import models, repo
from appointment.database.models import ExternalConnectionType

from appointment.dependencies.fxa import get_webhook_auth
from defines import FXA_CLIENT_PATCH


class TestFXAWebhooks:
    def test_fxa_process_change_password(self, with_db, with_client, make_pro_subscriber, make_external_connections):
        """Ensure the change password event is handled correctly"""
        FXA_USER_ID = 'abc-123'

        def override_get_webhook_auth():
            return {
                'iss': 'https://accounts.firefox.com/',
                'sub': FXA_USER_ID,
                'aud': 'REMOTE_SYSTEM',
                'iat': 1565720808,
                'jti': 'e19ed6c5-4816-4171-aa43-56ffe80dbda1',
                'events': {'https://schemas.accounts.firefox.com/event/password-change': {'changeTime': 1565721242227}},
            }

        # Override get_webhook_auth so we don't have to mock up a valid jwt token
        with_client.app.dependency_overrides[get_webhook_auth] = override_get_webhook_auth

        # make a guy
        subscriber = make_pro_subscriber()
        subscriber_id = subscriber.id
        make_external_connections(subscriber_id, type=models.ExternalConnectionType.fxa, type_id=FXA_USER_ID)

        assert subscriber.minimum_valid_iat_time is None

        # Freeze time to before the changeTime timestamp and test the password change works correctly
        with freeze_time('Aug 13th 2019'):
            # Update the external connection time to match our freeze_time
            with with_db() as db:
                fxa_connection = repo.external_connection.get_by_type(
                    db, subscriber_id, models.ExternalConnectionType.fxa, FXA_USER_ID
                )[0]
                fxa_connection.time_updated = datetime.datetime.now()
                db.add(fxa_connection)
                db.commit()

            response = with_client.post(
                '/webhooks/fxa-process',
            )
            assert response.status_code == 200, response.text

            with with_db() as db:
                subscriber = repo.subscriber.get(db, subscriber_id)
                assert subscriber.minimum_valid_iat_time is not None

        # Update the external connection time to match our current time
        # This will make the change password event out of date
        with with_db() as db:
            fxa_connection = repo.external_connection.get_by_type(
                db, subscriber_id, models.ExternalConnectionType.fxa, FXA_USER_ID
            )[0]
            fxa_connection.time_updated = datetime.datetime.now()
            db.add(fxa_connection)
            db.commit()

            # Reset our minimum_valid_iat_time, so we can ensure it stays None
            subscriber = repo.subscriber.get(db, subscriber_id)
            subscriber.minimum_valid_iat_time = None
            db.add(subscriber)
            db.commit()

        # Finally test that minimum_valid_iat_time stays the same due to an outdated password change event
        response = with_client.post(
            '/webhooks/fxa-process',
        )
        assert response.status_code == 200, response.text
        with with_db() as db:
            subscriber = repo.subscriber.get(db, subscriber_id)
            assert subscriber.minimum_valid_iat_time is None

    def test_fxa_process_change_primary_email(
        self, with_db, with_client, make_pro_subscriber, make_external_connections
    ):
        """Ensure the change primary email event is handled correctly"""

        FXA_USER_ID = 'abc-456'
        OLD_EMAIL = 'xBufferFan94x@example.org'
        NEW_EMAIL = 'john.butterfly@example.org'

        def override_get_webhook_auth():
            return {
                'iss': 'https://accounts.firefox.com/',
                'sub': FXA_USER_ID,
                'aud': 'REMOTE_SYSTEM',
                'iat': 1565720808,
                'jti': 'e19ed6c5-4816-4171-aa43-56ffe80dbda1',
                'events': {'https://schemas.accounts.firefox.com/event/profile-change': {'email': NEW_EMAIL}},
            }

        # Override get_webhook_auth so we don't have to mock up a valid jwt token
        with_client.app.dependency_overrides[get_webhook_auth] = override_get_webhook_auth

        # Make a guy with a middleschool-era email they would like to change
        subscriber = make_pro_subscriber(email=OLD_EMAIL)
        subscriber_id = subscriber.id
        subscriber_name = subscriber.name
        make_external_connections(subscriber_id, type=models.ExternalConnectionType.fxa, type_id=FXA_USER_ID)

        assert subscriber.minimum_valid_iat_time is None
        assert subscriber.email != OLD_EMAIL
        assert subscriber.email == OLD_EMAIL.lower()
        assert subscriber.avatar_url != FXA_CLIENT_PATCH.get('subscriber_avatar_url')
        assert subscriber.name != FXA_CLIENT_PATCH.get('subscriber_display_name')

        response = with_client.post(
            '/webhooks/fxa-process',
        )
        assert response.status_code == 200, response.text

        # Refresh the subscriber and test minimum_valid_iat_time (they should be logged out), and email address
        with with_db() as db:
            subscriber = repo.subscriber.get(db, subscriber_id)
            assert subscriber.email == NEW_EMAIL
            assert subscriber.minimum_valid_iat_time is not None

            # Ensure our profile update occured
            assert subscriber.avatar_url == FXA_CLIENT_PATCH.get('subscriber_avatar_url')
            # Ensure name does not change
            assert subscriber.name != FXA_CLIENT_PATCH.get('subscriber_display_name')
            assert subscriber.name == subscriber_name

    def test_fxa_process_delete_user(
        self,
        with_db,
        with_client,
        make_pro_subscriber,
        make_external_connections,
        make_appointment,
        make_caldav_calendar,
    ):
        """Ensure the delete user event is handled correctly"""
        FXA_USER_ID = 'abc-789'

        def override_get_webhook_auth():
            return {
                'iss': 'https://accounts.firefox.com/',
                'sub': FXA_USER_ID,
                'aud': 'REMOTE_SYSTEM',
                'iat': 1565720810,
                'jti': '1b3d623a-300a-4ab8-9241-855c35586809',
                'events': {'https://schemas.accounts.firefox.com/event/delete-user': {}},
            }

        # Override get_webhook_auth so we don't have to mock up a valid jwt token
        with_client.app.dependency_overrides[get_webhook_auth] = override_get_webhook_auth

        subscriber = make_pro_subscriber()
        make_external_connections(subscriber.id, type=models.ExternalConnectionType.fxa, type_id=FXA_USER_ID)
        calendar = make_caldav_calendar(subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)

        response = with_client.post(
            '/webhooks/fxa-process',
        )
        assert response.status_code == 200, response.text

        with with_db() as db:
            # Make sure everything we created is gone. A more exhaustive check is done in the delete account test
            assert repo.subscriber.get(db, subscriber.id) is None
            assert repo.calendar.get(db, calendar.id) is None
            assert repo.appointment.get(db, appointment.id) is None

class TestZoomWebhooks:
    @pytest.fixture
    def setup_deauthorization(self, make_pro_subscriber, make_external_connections):
        zoom_user_id = 'z9jkdsfsdfjhdkfjQ'

        request_body = {
            "event": "app_deauthorized",
            "payload": {
                "account_id": "EabCDEFghiLHMA",
                "user_id": zoom_user_id,
                "signature": "827edc3452044f0bc86bdd5684afb7d1e6becfa1a767f24df1b287853cf73000",
                "deauthorization_time": "2019-06-17T13:52:28.632Z",
                "client_id": "ADZ9k9bTWmGUoUbECUKU_a"
            }
        }

        zoom_signature = 'v0=cc6857f5b05fea4fb0f2057912c14a68996cfcf36a4267c65f15a3e9f1602477'
        zoom_timestamp = "2019-06-17T13:52:28.632Z"
        request_headers = {
            'x-zm-signature': zoom_signature,
            'x-zm-request-timestamp': zoom_timestamp
        }

        fake_secret = 'cake'
        os.environ['ZOOM_API_SECRET'] = fake_secret

        subscriber = make_pro_subscriber()
        external_connection = make_external_connections(
            subscriber_id=subscriber.id,
            type=models.ExternalConnectionType.zoom.value,
            type_id=zoom_user_id
        )

        return request_body, request_headers, subscriber, external_connection

    def test_deauthorization(self, with_client, with_db, setup_deauthorization):
        """Test a successful deauthorization (i.e. deleting the zoom connection)"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization
        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            zoom_user_id = external_connection.type_id

            response = with_client.post(
                '/webhooks/zoom-deauthorization',
                json=request_body,
                headers=request_headers
            )
            assert response.status_code == 200, response.text

            db.refresh(subscriber)
            external_connection = repo.external_connection.get_by_type(
                db,
                subscriber.id,
                type=ExternalConnectionType.zoom,
                type_id=zoom_user_id
            )

            assert subscriber
            assert not external_connection

    def test_deauthorization_silent_fail_due_to_no_connection(self, with_client, with_db, setup_deauthorization):
        """Test that a missing zoom connection doesn't crash the webhook"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization

        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            # Remove our external connection
            db.delete(external_connection)
            db.commit()

            response = with_client.post(
                '/webhooks/zoom-deauthorization',
                json=request_body,
                headers=request_headers
            )
            assert response.status_code == 200, response.text

    def test_deauthorization_silent_fail_due_to_no_user(self, with_client, with_db, setup_deauthorization):
        """Test that a missing subscriber doesn't crash the webhook"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization

        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            # Remove our external connection AND subscriber
            db.delete(external_connection)
            db.delete(subscriber)
            db.commit()

            response = with_client.post(
                '/webhooks/zoom-deauthorization',
                json=request_body,
                headers=request_headers
            )
            assert response.status_code == 200, response.text

    def test_deauthorization_with_invalid_webhook(self, with_client, with_db):
        """Test that an invalid request doesn't crash the webhook"""
        response = with_client.post(
            '/webhooks/zoom-deauthorization',
            json={
                'event': 'im-a-fake-event-woo!'
            },
        )
        assert response.status_code == 200, response.text

    def test_deauthorization_with_invalid_webhook_headers(self, with_client, with_db, setup_deauthorization):
        """Test that a valid response body with invalid headers doesn't remove the connection"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization

        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            response = with_client.post(
                '/webhooks/zoom-deauthorization',
                json=request_body,
                headers={
                    'x-zm-signature': 'bad-signature',
                    'x-zm-signature-timestamp': 'bad-timestamp'
                }
            )
            assert response.status_code == 200, response.text

            # Ensure that our connection still exists
            db.refresh(subscriber)
            db.refresh(external_connection)

            assert subscriber
            assert external_connection
