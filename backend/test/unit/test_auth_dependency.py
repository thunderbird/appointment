import datetime
import os
import uuid
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from unittest import mock


from appointment.controller.auth import signed_url_by_subscriber
from appointment.database import repo
from appointment.database.models import ExternalConnectionType
from appointment.dependencies.auth import (
    get_user_from_token,
    get_subscriber,
    get_admin_subscriber,
    get_subscriber_from_schedule_or_signed_url,
    get_user_from_oidc_token_introspection,
)
from appointment.exceptions.validation import (
    InvalidTokenException,
    InvalidPermissionLevelException,
    InvalidLinkException,
)
from appointment.routes.auth import create_access_token


class TestAuthDependency:
    def test_get_user_from_oidc_token_introspection(
        self, with_db, make_pro_subscriber, make_external_connections, monkeypatch
    ):
        # uuid works well for a random string
        oidc_id = uuid.uuid4().hex
        access_token = uuid.uuid4().hex
        subscriber = make_pro_subscriber()
        make_external_connections(subscriber_id=subscriber.id, type_id=oidc_id, type=ExternalConnectionType.oidc)

        with patch('appointment.controller.apis.oidc_client.OIDCClient.introspect_token') as introspect_token_mock:
            # Test that invalid token raises if introspect_token returns None
            introspect_token_mock.return_value = None

            with with_db() as db:
                with pytest.raises(InvalidTokenException):
                    get_user_from_oidc_token_introspection(db, access_token, None)

            # Reset call amount
            introspect_token_mock.reset_mock()

            # Return some fake token data
            introspect_token_mock.return_value = {
                'sub': oidc_id,
                'username': subscriber.username,
                'email': subscriber.email,
                'exp': (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)).timestamp(),
            }

            # Mock this redis request
            def redis_mock_get(key, default=None):
                return None

            def redis_mock_set(key, ex, **kwargs):
                assert str(ex) == os.getenv('REDIS_OIDC_TOKEN_INTROSPECT_EXPIRE_SECONDS')

            redis_mock = mock.MagicMock()
            monkeypatch.setattr(redis_mock, 'get', redis_mock_get)
            monkeypatch.setattr(redis_mock, 'set', redis_mock_set)

            # Test a successful return
            with with_db() as db:
                token_subscriber = get_user_from_oidc_token_introspection(db, access_token, redis_mock)
                introspect_token_mock.assert_called_once_with(access_token)
                assert token_subscriber is not None
                assert subscriber.id == token_subscriber.id

            # Reset call amount
            introspect_token_mock.reset_mock()

            # Adjust the max ttl to 1 day
            os.environ['REDIS_OIDC_TOKEN_INTROSPECT_EXPIRE_SECONDS'] = '86400'

            def redis_mock_set_new(key, ex, **kwargs):
                # Since the token expires in less time than the max cache it should be about an hour instead of the day
                # Exact value may differ due to execution time...
                assert str(ex) < os.getenv('REDIS_OIDC_TOKEN_INTROSPECT_EXPIRE_SECONDS')

            monkeypatch.setattr(redis_mock, 'set', redis_mock_set_new)

            # Test a successful return
            with with_db() as db:
                token_subscriber = get_user_from_oidc_token_introspection(db, access_token, redis_mock)
                introspect_token_mock.assert_called_once_with(access_token)
                assert token_subscriber is not None
                assert subscriber.id == token_subscriber.id

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
        access_token = create_access_token(data={'sub': f'uid-{subscriber.id}'})
        # Create a dummy request, not needed for this test
        request = mock.MagicMock()

        with with_db() as db:
            retrieved_subscriber = get_subscriber(request, access_token, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_subscriber_with_invalid_token(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        # Create a dummy request, not needed for this test
        request = mock.MagicMock()

        with with_db() as db:
            with pytest.raises(InvalidTokenException):
                # Use a nonsense value, like the subscriber id!
                get_subscriber(request, subscriber.id, db)

    def test_get_admin_subscriber(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        access_token = create_access_token(data={'sub': f'uid-{subscriber.id}'})
        # Create a dummy request, not needed for this test
        request = mock.MagicMock()

        os.environ['APP_ADMIN_ALLOW_LIST'] = subscriber.email

        with with_db() as db:
            retrieved_subscriber = get_admin_subscriber(get_subscriber(request, access_token, db))

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_admin_subscriber_fails_with_no_allow_list(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        access_token = create_access_token(data={'sub': f'uid-{subscriber.id}'})
        # Create a dummy request, not needed for this test
        request = mock.MagicMock()

        os.environ['APP_ADMIN_ALLOW_LIST'] = ''

        with with_db() as db:
            with pytest.raises(InvalidPermissionLevelException):
                get_admin_subscriber(get_subscriber(request, access_token, db))

    def test_get_admin_subscriber_fails_not_in_allow_list(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber(email='cool-beans@example.org')
        access_token = create_access_token(data={'sub': f'uid-{subscriber.id}'})
        # Create a dummy request, not needed for this test
        request = mock.MagicMock()

        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        with with_db() as db:
            with pytest.raises(InvalidPermissionLevelException):
                get_admin_subscriber(get_subscriber(request, access_token, db))

    def test_get_subscriber_from_schedule_or_signed_url_with_signed_url(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)
            retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(signed_url, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_subscriber_from_schedule_or_signed_url_with_schedule_slug_using_short_url(
        self, with_db, with_l10n, make_pro_subscriber, make_schedule, make_caldav_calendar
    ):
        subscriber = make_pro_subscriber()
        calendar = make_caldav_calendar(subscriber_id=subscriber.id)
        schedule = make_schedule(calendar_id=calendar.id)

        with with_db() as db:
            url = f'https://apmt.day/{subscriber.username}/{schedule.slug}/'
            retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(url, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_subscriber_from_schedule_or_signed_url_without_schedule_slug_using_short_url(
        self, with_db, with_l10n, make_pro_subscriber, make_schedule, make_caldav_calendar
    ):
        subscriber = make_pro_subscriber()
        calendar = make_caldav_calendar(subscriber_id=subscriber.id)
        schedule = make_schedule(calendar_id=calendar.id, slug='the-schedule')

        with with_db() as db:
            url = f'https://apmt.day/{subscriber.username}/'

            # Since we have a schedule slug this will error out
            with pytest.raises(InvalidLinkException):
                retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(url, db)

            schedule.slug = None
            db.add(schedule)
            db.commit()

            # Now that we don't have a schedule slug, this will succeed.
            retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(url, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_subscriber_from_schedule_or_signed_url_with_schedule_slug(
        self, with_db, with_l10n, make_pro_subscriber, make_schedule, make_caldav_calendar
    ):
        subscriber = make_pro_subscriber()
        calendar = make_caldav_calendar(subscriber_id=subscriber.id)
        schedule = make_schedule(calendar_id=calendar.id)

        with with_db() as db:
            url = f'https://apmt.day/user/{subscriber.username}/{schedule.slug}/'
            retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(url, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email

    def test_get_subscriber_from_schedule_or_signed_url_without_schedule_slug(
        self, with_db, with_l10n, make_pro_subscriber, make_schedule, make_caldav_calendar
    ):
        subscriber = make_pro_subscriber()
        calendar = make_caldav_calendar(subscriber_id=subscriber.id)
        schedule = make_schedule(calendar_id=calendar.id, slug='the-schedule-2')

        with with_db() as db:
            url = f'https://apmt.day/user/{subscriber.username}/'

            # Since we have a schedule slug this will error out
            with pytest.raises(InvalidLinkException):
                retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(url, db)

            schedule.slug = None
            db.add(schedule)
            db.commit()

            # Now that we don't have a schedule slug, this will succeed.
            retrieved_subscriber = get_subscriber_from_schedule_or_signed_url(url, db)

        assert retrieved_subscriber.id == subscriber.id
        assert retrieved_subscriber.email == subscriber.email
