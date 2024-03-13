import os
from typing import Annotated

from fastapi import Depends, Request, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from sqlalchemy.orm import Session

from ..database import repo, schemas
from ..dependencies.database import get_db
from ..exceptions import validation
from ..exceptions.validation import InvalidTokenException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def get_user_from_token(db, token: str):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('JWT_ALGO')])
        sub = payload.get("sub")
        iat = payload.get("iat")
        if sub is None:
            raise InvalidTokenException()
    except JWTError:
        raise InvalidTokenException()

    id = sub.replace('uid-', '')
    subscriber = repo.get_subscriber(db, int(id))

    # Token has been expired by us - temp measure to avoid spinning a refresh system, or a deny list for this issue
    if subscriber is None:
        raise InvalidTokenException()
    elif subscriber.minimum_valid_iat_time and not iat:
        raise InvalidTokenException()
    elif subscriber.minimum_valid_iat_time and subscriber.minimum_valid_iat_time.timestamp() > int(iat):
        raise InvalidTokenException()

    return subscriber


def get_subscriber(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    if token is None:
        raise InvalidTokenException()

    """Automatically retrieve and return the subscriber"""
    user = get_user_from_token(db, token)

    if user is None:
        raise InvalidTokenException()

    return user


def get_subscriber_from_signed_url(
    url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """Retrieve a subscriber based off a signed url from the body. Requires `url` param to be used in the request."""
    subscriber = repo.verify_subscriber_link(db, url)
    if not subscriber:
        raise validation.InvalidLinkException

    return subscriber
