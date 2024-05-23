import json
import os
import time
from datetime import timedelta, datetime, UTC
from secrets import token_urlsafe
from typing import Annotated

import argon2.exceptions
import jwt
from fastapi.security import OAuth2PasswordRequestForm
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from .. import utils
from ..database import repo, schemas
from ..database.models import Subscriber, ExternalConnectionType

from ..dependencies.database import get_db
from ..dependencies.auth import get_subscriber, get_admin_subscriber

from ..controller import auth
from ..controller.apis.fxa_client import FxaClient
from ..dependencies.fxa import get_fxa_client
from ..exceptions import validation
from ..exceptions.fxa_api import NotInAllowListException
from ..l10n import l10n

router = APIRouter()


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
def fxa_login(request: Request,
              email: str,
              timezone: str | None = None,
              invite_code: str | None = None,
              db: Session = Depends(get_db),
              fxa_client: FxaClient = Depends(get_fxa_client)):
    """Request an authorization url from fxa"""
    if os.getenv('AUTH_SCHEME') != 'fxa':
        raise HTTPException(status_code=405)

    fxa_client.setup()

    try:
        url, state = fxa_client.get_redirect_url(db, token_urlsafe(32), email)
    except NotInAllowListException:
        raise HTTPException(status_code=403, detail='Your email is not in the allow list')

    request.session['fxa_state'] = state
    request.session['fxa_user_email'] = email
    request.session['fxa_user_timezone'] = timezone
    request.session['fxa_user_invite_code'] = invite_code

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
    # We only use timezone during subscriber creation, or if their timezone is None
    timezone = request.session['fxa_user_timezone']
    invite_code = request.session.get('fxa_user_invite_code')

    # Clear session keys
    request.session.pop('fxa_state')
    request.session.pop('fxa_user_email')
    request.session.pop('fxa_user_timezone')
    if invite_code:
        request.session.pop('fxa_user_invite_code')

    fxa_client.setup()

    # Retrieve credentials and user profile
    creds = fxa_client.get_credentials(code)
    profile = fxa_client.get_profile()

    if profile['email'] != email:
        fxa_client.logout()
        raise HTTPException(400, l10n('email-mismatch'))

    # Check if we have an existing fxa connection by profile's uid
    fxa_subscriber = repo.external_connection.get_subscriber_by_fxa_uid(db, profile['uid'])
    # Also look up the subscriber (in case we have an existing account that's not tied to a given fxa account)
    subscriber = repo.subscriber.get_by_email(db, email)

    new_subscriber_flow = not fxa_subscriber and not subscriber

    if new_subscriber_flow:
        # Ensure the invite code exists and is available
        # Use some inline-errors for now. We don't have a good error flow!
        if not repo.invite.code_exists(db, invite_code):
            raise HTTPException(404, l10n('invite-code-not-valid'))
        if not repo.invite.code_is_available(db, invite_code):
            raise HTTPException(403, l10n('invite-code-not-valid'))

        subscriber = repo.subscriber.create(db, schemas.SubscriberBase(
            email=email,
            username=email,
            timezone=timezone,
        ))

        # Use the invite code after we've created the new subscriber
        repo.invite.use_code(db, code, subscriber.id)
    elif not subscriber:
        subscriber = fxa_subscriber

    fxa_connections = repo.external_connection.get_by_type(db, subscriber.id, ExternalConnectionType.fxa)

    # If we have fxa_connections, ensure the incoming one matches our known one.
    # This shouldn't occur, but it's a safety check in-case we missed a webhook push.
    if any([profile['uid'] != ec.type_id for ec in fxa_connections]):
        # Ensure sentry captures the error too!
        if os.getenv('SENTRY_DSN') != '':
            e = Exception("Invalid Credentials, incoming profile uid does not match existing profile uid")
            capture_exception(e)

        raise HTTPException(403, l10n('invalid-credentials'))

    external_connection_schema = schemas.ExternalConnection(
        name=profile['email'],
        type=ExternalConnectionType.fxa,
        type_id=profile['uid'],
        owner_id=subscriber.id,
        token=json.dumps(creds)
    )

    if not fxa_subscriber:
        repo.external_connection.create(db, external_connection_schema)
    else:
        repo.external_connection.update_token(db, json.dumps(creds), subscriber.id,
                                                         external_connection_schema.type,
                                                         external_connection_schema.type_id)

    # Update profile with fxa info
    data = schemas.SubscriberIn(
        avatar_url=profile['avatar'],
        name=subscriber.name,
        username=subscriber.username,
        email=profile['email'],
        timezone=timezone if subscriber.timezone is None else None
    )

    # If they're a new subscriber we should fill in some defaults!
    if new_subscriber_flow:
        data.name = profile['displayName'] if 'displayName' in profile else profile['email'].split('@')[0]
        data.username = profile['email']

    repo.subscriber.update(db, data, subscriber.id)

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
    subscriber = repo.subscriber.get_by_username(db, form_data.username)
    if not subscriber or subscriber.password is None:
        raise HTTPException(status_code=403, detail=l10n('invalid-credentials'))

    # Verify the incoming password, and re-hash our password if needed
    try:
        utils.verify_password(form_data.password, subscriber.password)
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(status_code=403, detail=l10n('invalid-credentials'))

    if utils.ph.check_needs_rehash(subscriber.password):
        subscriber.password = utils.get_password_hash(form_data.password)
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
def logout(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber),
           fxa_client: FxaClient = Depends(get_fxa_client)):
    """Logout a given subscriber session"""

    if os.getenv('AUTH_SCHEME') == 'fxa':
        fxa_client.setup(subscriber.id, subscriber.get_external_connection(ExternalConnectionType.fxa).token)

    # Don't set a minimum_valid_iat_time here.
    auth.logout(db, subscriber, fxa_client, deny_previous_tokens=False)

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


@router.post("/permission-check")
def permission_check(_: Subscriber = Depends(get_admin_subscriber)):
    """Checks if they have admin permissions"""
    return True


# @router.get('/test-create-account')
# def test_create_account(email: str, password: str, timezone: str, db: Session = Depends(get_db)):
#     """Used to create a test account"""
#     if os.getenv('APP_ENV') != 'dev':
#         raise HTTPException(status_code=405)
#     if os.getenv('AUTH_SCHEME') != 'password':
#         raise HTTPException(status_code=405)
#
#     subscriber = repo.subscriber.create(db, schemas.SubscriberBase(
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
