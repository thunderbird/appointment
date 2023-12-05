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

from ..controller.apis.fxa_client import FxaClient

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
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGO'))
    return encoded_jwt


@router.get("/fxa_login")
def fxa_login(request: Request, email: str):
    fxa_client = FxaClient(os.getenv('FXA_CLIENT_ID'), os.getenv('FXA_SECRET'), os.getenv('FXA_CALLBACK'))
    fxa_client.setup()
    url, state = fxa_client.get_redirect_url(token_urlsafe(32), email)

    request.session['fxa_state'] = state
    request.session['fxa_user_email'] = email

    return {
        'url': url
    }


@router.get("/fxa-profile")
def fxa_profile(db: Session = Depends(get_db)):
    subscriber : Subscriber = repo.get_subscriber(db, 1)

    fxa_client = FxaClient(os.getenv('FXA_CLIENT_ID'), os.getenv('FXA_SECRET'), os.getenv('FXA_CALLBACK'))
    fxa_client.setup(1, subscriber.get_external_connection(ExternalConnectionType.fxa).token)
    return fxa_client.get_profile()


@router.get("/fxa-token")
def get_da_token(db: Session = Depends(get_db)):
    subscriber: Subscriber = repo.get_subscriber(db, 1)
    return subscriber.get_external_connection(ExternalConnectionType.fxa).token


@router.get('/logout')
def logout(subscriber: Subscriber = Depends(get_subscriber)):
    """Logout a given subscriber session"""

    # We don't actually have to do anything for non-fxa schemes
    if os.getenv('AUTH_SCHEME') != 'fxa':
        return True

    fxa_client = FxaClient(os.getenv('FXA_CLIENT_ID'), os.getenv('FXA_SECRET'), os.getenv('FXA_CALLBACK'))
    fxa_client.setup(subscriber.id, subscriber.get_external_connection(ExternalConnectionType.fxa).token)
    fxa_client.logout()

    return True


@router.get("/fxa")
def fxa_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
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
    if 'fxa_state' not in request.session or request.session['fxa_state'] != state:
        raise HTTPException(400, "Invalid state.")
    if 'fxa_user_email' not in request.session or request.session['fxa_user_email'] == '':
        raise HTTPException(400, "Email could not be retrieved.")

    email = request.session['fxa_user_email']

    # Clear zoom session keys
    request.session.pop('fxa_state')
    request.session.pop('fxa_user_email')

    fxa_client = FxaClient(os.getenv('FXA_CLIENT_ID'), os.getenv('FXA_SECRET'), os.getenv('FXA_CALLBACK'))
    fxa_client.setup()

    # Retrieve credentials and user profile
    creds = fxa_client.get_credentials(code)
    profile = fxa_client.get_profile()

    # Check if we have an existing fxa connection by profile's uid
    external_connection = repo.get_first_external_connection_by_type(db, ExternalConnectionType.fxa, profile['uid'])
    if not external_connection:
        subscriber = repo.create_subscriber(db, schemas.SubscriberBase(
            email=email,
            username=email,
        ))
    else:
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
        name=profile['displayName'] if 'displayName' in profile else subscriber.name,
        username=profile['email'],
        email=profile['email'],
    )
    repo.update_subscriber(db, data, subscriber.id)

    # Generate our jwt token, we only store the username on the token
    access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))
    access_token = create_access_token(
        data={"sub": subscriber.username}, expires_delta=access_token_expires
    )

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/post-login/{access_token}")


@router.post("/token")
def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
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
        data={"sub": subscriber.username}, expires_delta=access_token_expires
    )

    """Log a user in with the passed username and password information"""
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.SubscriberBase)
def me(
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Return the currently authed user model
    """
    return schemas.SubscriberBase(
        username=subscriber.username, email=subscriber.email, name=subscriber.name, level=subscriber.level,
        timezone=subscriber.timezone, avatar_url=subscriber.avatar_url
    )
