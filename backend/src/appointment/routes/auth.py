import json
import os
from datetime import timedelta, datetime, UTC
from secrets import token_urlsafe
from typing import Annotated

import argon2.exceptions
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from argon2 import PasswordHasher

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from ..database import repo, schemas
from ..database.models import Subscriber, ExternalConnectionType

from ..dependencies.database import get_db
from ..dependencies.auth import get_subscriber

from ..controller import auth
from ..controller.apis.fxa_client import FxaClient
from ..dependencies.fxa import get_fxa_client
from ..exceptions.fxa_api import NotInAllowListException

router = APIRouter()
ph = PasswordHasher()


def verify_password(password, hashed_password):
    ph.verify(hashed_password, password)


def get_password_hash(password):
    return ph.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({
        "exp": expire,
        "iat": int(datetime.now(UTC).timestamp())
    })
    encoded_jwt = jwt.encode(to_encode, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGO'))
    return encoded_jwt


@router.get("/fxa_login")
def fxa_login(request: Request, email: str, timezone: str|None = None, fxa_client: FxaClient = Depends(get_fxa_client)):
    """Request an authorization url from fxa"""
    if os.getenv('AUTH_SCHEME') != 'fxa':
        raise HTTPException(status_code=405)

    fxa_client.setup()

    try:
        url, state = fxa_client.get_redirect_url(token_urlsafe(32), email)
    except NotInAllowListException:
        raise HTTPException(status_code=403, detail='Your email is not in the allow list')

    request.session['fxa_state'] = state
    request.session['fxa_user_email'] = email
    request.session['fxa_user_timezone'] = timezone

    return {
        'url': url
    }


@router.get("/fxa")
def fxa_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    fxa_client: FxaClient = Depends(get_fxa_client)
):
    """Auth callback from fxa. It's a bit of a journey:
    - We first ensure the state has not changed during the authentication process.
    - We setup a fxa_client, and retrieve credentials and profile information on the user.
    - After which we do a lookup on our fxa external connections for a match on profile's uid field.
        - If not match is made, we create a new subscriber with the given email.
        - Otherwise we just grab the external connection's owner.
    - We update the external connection with any new details
    - We also update (an initial set if the subscriber is new) the profile data for the subscriber.
    - And finally generate a jwt token for the frontend, and redirect them to a special frontend route with that token.
    """
    if os.getenv('AUTH_SCHEME') != 'fxa':
        raise HTTPException(status_code=405)

    if 'fxa_state' not in request.session or request.session['fxa_state'] != state:
        raise HTTPException(400, "Invalid state.")
    if 'fxa_user_email' not in request.session or request.session['fxa_user_email'] == '':
        raise HTTPException(400, "Email could not be retrieved.")

    email = request.session['fxa_user_email']
    # We only use timezone during subscriber creation
    timezone = request.session['fxa_user_timezone']

    # Clear session keys
    request.session.pop('fxa_state')
    request.session.pop('fxa_user_email')
    request.session.pop('fxa_user_timezone')

    fxa_client.setup()

    # Retrieve credentials and user profile
    creds = fxa_client.get_credentials(code)
    profile = fxa_client.get_profile()

    if profile['email'] != email:
        fxa_client.logout()
        raise HTTPException(400, "Email mismatch.")

    # Check if we have an existing fxa connection by profile's uid
    external_connection = repo.get_subscriber_by_fxa_uid(db, profile['uid'])
    # Also look up the subscriber (in case we have an existing account that's not tied to a given fxa account)
    subscriber = repo.get_subscriber_by_email(db, email)

    if not external_connection and not subscriber:
        subscriber = repo.create_subscriber(db, schemas.SubscriberBase(
            email=email,
            username=email,
            timezone=timezone,
        ))
    elif not subscriber:
        subscriber = external_connection.owner

    external_connection_schema = schemas.ExternalConnection(
        name=profile['email'],
        type=ExternalConnectionType.fxa,
        type_id=profile['uid'],
        owner_id=subscriber.id,
        token=json.dumps(creds)
    )

    if not external_connection:
        repo.create_subscriber_external_connection(db, external_connection_schema)
    else:
        repo.update_subscriber_external_connection_token(db, json.dumps(creds), subscriber.id, external_connection_schema.type, external_connection_schema.type_id)

    # Update profile with fxa info
    data = schemas.SubscriberIn(
        avatar_url=profile['avatar'],
        name=profile['displayName'] if 'displayName' in profile else profile['email'].split('@')[0],
        username=profile['email'],
        email=profile['email'],
    )
    repo.update_subscriber(db, data, subscriber.id)

    # Generate our jwt token, we only store the username on the token
    access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))
    access_token = create_access_token(
        data={"sub": f"uid-{subscriber.id}"}, expires_delta=access_token_expires
    )

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/post-login/{access_token}")


@router.post("/token")
def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    if os.getenv('AUTH_SCHEME') == 'fxa':
        raise HTTPException(status_code=405)

    """Retrieve an access token from a given username and password."""
    subscriber = repo.get_subscriber_by_username(db, form_data.username)
    if not subscriber or subscriber.password is None:
        raise HTTPException(status_code=403, detail="User credentials mismatch")

    # Verify the incoming password, and re-hash our password if needed
    try:
        verify_password(form_data.password, subscriber.password)
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(status_code=403, detail="User credentials mismatch")

    if ph.check_needs_rehash(subscriber.password):
        subscriber.password = get_password_hash(form_data.password)
        db.add(subscriber)
        db.commit()

    # Generate our jwt token, we only store the username on the token
    access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))
    access_token = create_access_token(
        data={"sub": f"uid-{subscriber.id}"}, expires_delta=access_token_expires
    )

    """Log a user in with the passed username and password information"""
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/logout')
def logout(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber), fxa_client: FxaClient = Depends(get_fxa_client)):
    """Logout a given subscriber session"""

    if os.getenv('AUTH_SCHEME') == 'fxa':
        fxa_client.setup(subscriber.id, subscriber.get_external_connection(ExternalConnectionType.fxa).token)

    auth.logout(db, subscriber, fxa_client)

    return True


@router.get("/me", response_model=schemas.SubscriberBase)
def me(
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Return the currently authed user model"""
    return schemas.SubscriberBase(
        username=subscriber.username, email=subscriber.email, name=subscriber.name, level=subscriber.level,
        timezone=subscriber.timezone, avatar_url=subscriber.avatar_url
    )


# @router.get('/test-create-account')
# def test_create_account(email: str, password: str, timezone: str, db: Session = Depends(get_db)):
#     """Used to create a test account"""
#     if os.getenv('APP_ENV') != 'dev':
#         raise HTTPException(status_code=405)
#     if os.getenv('AUTH_SCHEME') != 'password':
#         raise HTTPException(status_code=405)
#
#     subscriber = repo.create_subscriber(db, schemas.SubscriberBase(
#         email=email,
#         username=email,
#         name=email.split('@')[0],
#         timezone=timezone
#     ))
#
#     # Update with password
#     subscriber.password = get_password_hash(password)
#
#     db.add(subscriber)
#     db.commit()
#     db.refresh(subscriber)
#
#     return subscriber
