import datetime
import json
import os
from typing import Annotated

import sentry_sdk
from fastapi import Depends, Body, Request, HTTPException
from fastapi.params import Depends as DependsClass
from fastapi.security import OAuth2PasswordBearer
import jwt

from sqlalchemy.orm import Session

from ..controller.apis.accounts_client import AccountsClient
from ..controller.apis.oidc_client import OIDCClient
from ..database import repo, models
from ..defines import AuthScheme, REDIS_OIDC_TOKEN_KEY
from ..dependencies.database import get_db, get_redis
from ..exceptions import validation
from ..exceptions.validation import InvalidTokenException, InvalidPermissionLevelException
from ..utils import encrypt, decrypt, get_expiry_time_with_grace_period

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token', auto_error=False)


def get_user_from_oidc_token_introspection(db, token: str, redis_instance):
    # Do we have the data cached?
    encrypted_token = encrypt(token)
    token_data = None
    cache_hit = False

    if redis_instance:
        # Retrieve the cached token data
        encrypted_token_data = redis_instance.get(f'{REDIS_OIDC_TOKEN_KEY}:{encrypted_token}')
        if encrypted_token_data:
            token_data = json.loads(decrypt(encrypted_token_data))

    # If redis isn't setup, or we don't have any cached token data then do the introspection
    if not token_data:
        oidc_client = OIDCClient()
        token_data = oidc_client.introspect_token(token)
    else:
        cache_hit = True

    # Still nothing? Error out.
    if not token_data:
        raise InvalidTokenException()

    subscriber = repo.external_connection.get_subscriber_by_oidc_id(db, token_data.get('sub'))
    if not subscriber:
        raise InvalidTokenException()

    if redis_instance and not cache_hit:
        # If the token expires in less time than the default expiry time, use that.
        expiry = (
            get_expiry_time_with_grace_period(token_data.get('exp', 0))
            - datetime.datetime.now(datetime.UTC).timestamp()
        )

        expiry = max(expiry, 1)
        expiry = min(int(os.getenv('REDIS_OIDC_TOKEN_INTROSPECT_EXPIRE_SECONDS', 300)), expiry)

        # Cache the token data for 300 seconds or the defined env var
        redis_instance.set(
            f'{REDIS_OIDC_TOKEN_KEY}:{encrypted_token}',
            value=encrypt(json.dumps(token_data)),
            ex=int(expiry),
        )

    return subscriber


def get_user_from_token(db, token: str, require_jti=False):
    sub = None
    iat = None
    jti = None
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('JWT_ALGO')])
        sub = payload.get('sub')
        iat = payload.get('iat')
        jti = payload.get('jti')
        if sub is None:
            raise InvalidTokenException()
    except jwt.exceptions.InvalidTokenError:
        raise InvalidTokenException()

    sub_id = sub.replace('uid-', '')
    subscriber = repo.subscriber.get(db, int(sub_id))

    # Check this first as any doesn't short-circuit
    if subscriber is None:
        raise InvalidTokenException()

    # Token has been expired by us - temp measure to avoid spinning a refresh system, or a deny list for this issue
    if any(
        [
            subscriber.is_deleted,
            subscriber.minimum_valid_iat_time and not iat,
            # We only need second resolution
            subscriber.minimum_valid_iat_time and int(subscriber.minimum_valid_iat_time.timestamp()) > int(iat),
            # If we require this token to be a one time token, then require the claim
            require_jti and not jti,
            # If don't require this token to be a one time token, and it is...well we don't want it, go away.
            not require_jti and jti,
        ]
    ):
        raise InvalidTokenException()

    # If we're a one-time token, set the minimum valid iat time to now!
    # Beats having to store them multiple times, and it's only used in post-login.
    if jti:
        now = datetime.datetime.now(datetime.UTC)
        subscriber.minimum_valid_iat_time = now
        db.add(subscriber)
        db.commit()

    return subscriber


def get_subscriber(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
    redis_instance=Depends(get_redis),
    require_jti=False,
):
    """Automatically retrieve and return the subscriber"""
    if token is None:
        raise InvalidTokenException()

    # When this method is called directly (not through FastAPI DI), redis_instance will be
    # the Depends object itself rather than the resolved value, so assigning it to None will
    # make it call the OIDC introspect endpoint in that case (no caching)
    if isinstance(redis_instance, DependsClass):
        redis_instance = None

    if AuthScheme.is_oidc():
        user = get_user_from_oidc_token_introspection(db, token, redis_instance)
    else:
        user = get_user_from_token(db, token, require_jti)

    if user is None:
        raise InvalidTokenException()

    # Associate user id with users
    if os.getenv('SENTRY_DSN'):
        sentry_sdk.set_user(
            {
                'id': user.id,
            }
        )

    return user


async def get_subscriber_from_onetime_token(
    request: Request,
    db: Session = Depends(get_db),
    redis_instance=Depends(get_redis),
):
    """Retrieve the subscriber via a one-time token only!"""
    token: str = await oauth2_scheme(request)
    return get_subscriber(request, token, db, redis_instance, require_jti=True)


async def get_subscriber_or_none(
    request: Request,
    db: Session = Depends(get_db),
    redis_instance=Depends(get_redis),
):
    """Retrieve the subscriber or return None. This does not automatically error out like the other deps"""
    try:
        token: str = await oauth2_scheme(request)
        subscriber = get_subscriber(request, token, db, redis_instance)
    except InvalidTokenException:
        return None
    except HTTPException:
        return None
    except Exception as ex:
        # Catch any un-expected exceptions
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(ex)
        return None

    return subscriber


def get_admin_subscriber(
    user: models.Subscriber = Depends(get_subscriber),
):
    """Retrieve the subscriber and check if they're an admin"""
    # check admin allow list
    admin_emails = os.getenv('APP_ADMIN_ALLOW_LIST')

    # Raise an error if we don't have any admin emails specified
    if not admin_emails or not user:
        raise InvalidPermissionLevelException()

    admin_emails = admin_emails.split(',')
    if not any([user.email.endswith(allowed_email) for allowed_email in admin_emails]):
        raise InvalidPermissionLevelException()

    return user


def get_subscriber_from_signed_url(
    url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """Retrieve a subscriber based off a signed url from the body. Requires `url` param to be used in the request."""
    subscriber = repo.subscriber.verify_link(db, url)
    if not subscriber:
        raise validation.InvalidLinkException

    return subscriber


def get_subscriber_from_schedule_or_signed_url(
    url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """Retrieve a subscriber based off a signed url or schedule slug namespaced by their username."""
    subscriber = repo.subscriber.verify_link(db, url)
    if not subscriber:
        subscriber = repo.schedule.verify_link(db, url)

    if not subscriber:
        raise validation.InvalidLinkException

    return subscriber


def get_accounts_client():
    """Returns an instance of Accounts."""
    return AccountsClient(
        os.getenv('TB_ACCOUNTS_CLIENT_ID'), os.getenv('TB_ACCOUNTS_SECRET'), os.getenv('TB_ACCOUNTS_CALLBACK')
    )
