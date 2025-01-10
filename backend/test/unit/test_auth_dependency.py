import datetime
import os

import pytest
from freezegun import freeze_time

from appointment.controller.auth import signed_url_by_subscriber
from appointment.database import repo
from appointment.dependencies.auth import get_user_from_token, get_subscriber, get_admin_subscriber, \
    get_subscriber_from_schedule_or_signed_url
from appointment.exceptions.validation import InvalidTokenException, InvalidPermissionLevelException
from appointment.routes.auth import create_access_token


class TestAuthDependency:
    def test_get_user_from_token(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        access_token_expires = datetime.timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))

        # Ensure we don't have a minimum_valid_iat_time, that test comes later.
        assert subscriber.minimum_valid_iat_time is None

        # Create the access token and test it
        with freeze_time('Jan 9th 2024'):
            access_token = create_access_token(data={'sub': f'uid-{subscriber.id}'}, expires_delta=access_token_expires)

            assert access_token

            with with_db() as db:
                subscriber_from_token = get_user_from_token(db, access_token)

            assert subscriber_from_token
            assert subscriber_from_token.id == subscriber.id
            assert subscriber_from_token.email == subscriber.email

        # The access token should still be valid the next day
        with freeze_time('Jan 10th 2024'):
            with with_db() as db:
                subscriber_from_token = get_user_from_token(db, access_token)

            assert subscriber_from_token
            assert subscriber_from_token.id == subscriber.id
            assert subscriber_from_token.email == subscriber.email

        # Pick a time outside the token expiry window, and ensure it breaks
        with freeze_time('Feb 1st 2024'):
            with with_db() as db:
                # Internally raises ExpiredSignatureError, but we catch it and send a HTTPException instead.
                with pytest.raises(InvalidTokenException):
                    get_user_from_token(db, access_token)

        # Update the subscriber to have a minimum_valid_iat_time
        with freeze_time('Jan 10th 2024'):
            with with_db() as db:
                # We need to pull down the subscriber in this db session, otherwise we can't save it.
                subscriber = repo.subscriber.get(db, subscriber.id)
                subscriber.minimum_valid_iat_time = datetime.datetime.now(datetime.UTC)
                db.add(subscriber)
                db.commit()

        # Now the access token should be invalid
        with freeze_time('Jan 9th 2024'):
            with with_db() as db:
                # Internally raises ExpiredSignatureError, but we catch it and send a HTTPException instead.
                with pytest.raises(InvalidTokenException):
                    get_user_from_token(db, access_token)

    def test_get_subscriber(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        access_token = create_access_token(data={"sub": f"uid-{subscriber.id}"})

        with with_db() as db:
            retrieved_subscriber = get_subscriber(access_token, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_subscriber_with_invalid_token(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()

        with with_db() as db:
            with pytest.raises(InvalidTokenException):
                # Use a nonsense value, like the subscriber id!
                get_subscriber(subscriber.id, db)

    def test_get_admin_subscriber(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        access_token = create_access_token(data={"sub": f"uid-{subscriber.id}"})

        os.environ['APP_ADMIN_ALLOW_LIST'] = subscriber.email

        with with_db() as db:
            retrieved_subscriber = get_admin_subscriber(get_subscriber(access_token, db))

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_admin_subscriber_fails_with_no_allow_list(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        access_token = create_access_token(data={"sub": f"uid-{subscriber.id}"})

        os.environ['APP_ADMIN_ALLOW_LIST'] = ''

        with with_db() as db:
            with pytest.raises(InvalidPermissionLevelException):
                get_admin_subscriber(get_subscriber(access_token, db))

    def test_get_admin_subscriber_fails_not_in_allow_list(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber(email='cool-beans@example.org')
        access_token = create_access_token(data={"sub": f"uid-{subscriber.id}"})

        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        with with_db() as db:
            with pytest.raises(InvalidPermissionLevelException):
                get_admin_subscriber(get_subscriber(access_token, db))

    def test_get_subscriber_from_schedule_or_signed_url_with_signed_url(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)
            retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(signed_url, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_subscriber_from_schedule_or_signed_url_with_schedule_slug(self, with_db, with_l10n,
                                                                           make_pro_subscriber, make_schedule,
                                                                           make_caldav_calendar):
        subscriber = make_pro_subscriber()
        calendar = make_caldav_calendar(subscriber_id=subscriber.id)
        schedule = make_schedule(calendar_id=calendar.id)

        with with_db() as db:
            url = f"https://apmt.day/{subscriber.username}/{schedule.slug}/"
            retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(url, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email
