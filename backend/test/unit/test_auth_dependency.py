import datetime
import os

import pytest
from freezegun import freeze_time

from appointment.database import repo
from appointment.dependencies.auth import get_user_from_token
from appointment.exceptions.validation import InvalidTokenException
from appointment.routes.auth import create_access_token


class TestAuthDependency:

    def test_get_user_from_token(self, with_db, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        access_token_expires = datetime.timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))

        # Ensure we don't have a minimum_valid_iat_time, that test comes later.
        assert subscriber.minimum_valid_iat_time is None

        # Create the access token and test it
        with freeze_time("Jan 9th 2024"):
            access_token = create_access_token(data={"sub": f"uid-{subscriber.id}"}, expires_delta=access_token_expires)

            assert access_token

            with with_db() as db:
                subscriber_from_token = get_user_from_token(db, access_token)

            assert subscriber_from_token
            assert subscriber_from_token == subscriber_from_token

        # The access token should still be valid the next day
        with freeze_time("Jan 10th 2024"):
            with with_db() as db:
                subscriber_from_token = get_user_from_token(db, access_token)

            assert subscriber_from_token
            assert subscriber_from_token == subscriber_from_token

        # Pick a time outside the token expiry window, and ensure it breaks
        with freeze_time("Feb 1st 2024"):
            with with_db() as db:
                # Internally raises ExpiredSignatureError, but we catch it and send a HTTPException instead.
                with pytest.raises(InvalidTokenException):
                    get_user_from_token(db, access_token)

        # Update the subscriber to have a minimum_valid_iat_time
        with freeze_time("Jan 10th 2024"):
            with with_db() as db:
                # We need to pull down the subscriber in this db session, otherwise we can't save it.
                subscriber = repo.subscriber.get(db, subscriber.id)
                subscriber.minimum_valid_iat_time = datetime.datetime.now(datetime.UTC)
                db.add(subscriber)
                db.commit()

        # Now the access token should be invalid
        with freeze_time("Jan 9th 2024"):
            with with_db() as db:
                # Internally raises ExpiredSignatureError, but we catch it and send a HTTPException instead.
                with pytest.raises(InvalidTokenException):
                    get_user_from_token(db, access_token)
