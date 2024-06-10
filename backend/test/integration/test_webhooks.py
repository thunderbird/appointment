import datetime

from freezegun import freeze_time
from appointment.database import models, repo

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
        assert subscriber.email == OLD_EMAIL
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
