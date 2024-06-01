import os
from typing import Annotated

import sentry_sdk
from fastapi import Depends, Request, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
import jwt

from sqlalchemy.orm import Session

from ..database import repo, schemas, models
from ..dependencies.database import get_db
from ..exceptions import validation
from ..exceptions.validation import InvalidTokenException, InvalidPermissionLevelException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def get_user_from_token(db, token: str):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('JWT_ALGO')])
        sub = payload.get("sub")
        iat = payload.get("iat")
        if sub is None:
            raise InvalidTokenException()
    except jwt.exceptions.InvalidTokenError:
        raise InvalidTokenException()

    id = sub.replace('uid-', '')
    subscriber = repo.subscriber.get(db, int(id))

    # Token has been expired by us - temp measure to avoid spinning a refresh system, or a deny list for this issue
    if any([
        subscriber is None,
        subscriber.is_deleted,
        subscriber and subscriber.minimum_valid_iat_time and not iat,
        subscriber and subscriber.minimum_valid_iat_time and subscriber.minimum_valid_iat_time.timestamp() > int(iat)
    ]):
        raise InvalidTokenException()

    return subscriber


def get_subscriber(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """Automatically retrieve and return the subscriber"""
    if token is None:
        raise InvalidTokenException()

    user = get_user_from_token(db, token)

    if user is None:
        raise InvalidTokenException()

    # Associate user id with users
    if os.getenv('SENTRY_DSN'):
        sentry_sdk.set_user({
            'id': user.id,
        })

    return user


def get_admin_subscriber(
    user: models.Subscriber = Depends(get_subscriber),
):
    """Retrieve the subscriber and check if they're an admin"""
    # check admin allow list
    admin_emails = os.getenv("APP_ADMIN_ALLOW_LIST")

    # Raise an error if we don't have any admin emails specified
    if not admin_emails:
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
