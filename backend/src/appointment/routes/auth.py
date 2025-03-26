import base64
import json
import os
import secrets
from datetime import timedelta, datetime, UTC
from secrets import token_urlsafe
from typing import Annotated

import argon2.exceptions
import jwt
from fastapi.security import OAuth2PasswordRequestForm
from redis import Redis
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from .. import utils
from ..controller.apis.accounts_client import AccountsClient
from ..controller.auth import schedule_links_by_subscriber
from ..database import repo, schemas
from ..database.models import Subscriber, ExternalConnectionType
from ..defines import INVITES_TO_GIVE_OUT, AuthScheme, REDIS_USER_SESSION_PROFILE_KEY

from ..dependencies.database import get_db, get_shared_redis
from ..dependencies.auth import (
    get_subscriber,
    get_admin_subscriber,
    get_subscriber_from_onetime_token,
    get_accounts_client,
)

from ..controller import auth
from ..controller.apis.fxa_client import FxaClient
from ..dependencies.fxa import get_fxa_client
from ..exceptions import validation
from ..l10n import l10n
from ..utils import get_password_hash

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({'exp': expire, 'iat': int(datetime.now(UTC).timestamp())})
    encoded_jwt = jwt.encode(to_encode, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGO'))
    return encoded_jwt


def create_subscriber(db, email, password, timezone):
    subscriber = repo.subscriber.create(
        db,
        schemas.SubscriberBase(
            email=email.lower(),  # Make sure to store the email address in lower case
            username=email,
            name=email.split('@')[0],
            timezone=timezone,
        ),
    )

    # Update with password
    subscriber.password = get_password_hash(password)

    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    return subscriber


@router.post('/can-login')
def can_login(
    data: schemas.CheckEmail,
    db: Session = Depends(get_db),
    fxa_client: FxaClient = Depends(get_fxa_client),
    accounts_client: AccountsClient = Depends(get_accounts_client),
):
    """Determines if a user can go through the login flow"""
    email = data.email.lower()

    if AuthScheme.is_fxa():
        # This checks if a subscriber exists, or is in allowed list
        return fxa_client.is_in_allow_list(db, email)
    elif AuthScheme.is_accounts():
        return accounts_client.is_in_allow_list(db, email)

    # There's no waiting list setting on password login
    return True


@router.get('/auth/accounts')
def accounts_login(
    request: Request,
    email: str,
    timezone: str | None = None,
    invite_code: str | None = None,
    db: Session = Depends(get_db),
    accounts_client: AccountsClient = Depends(get_accounts_client),
):
    """Request an authorization url from accounts"""
    if not AuthScheme.is_accounts():
        raise HTTPException(status_code=405)

    accounts_client.setup()

    # Normalize email address to lower case
    email = email.lower()

    # Check if they're in the allowed list, but only if they didn't provide an invite code
    # This checks to see if they're already a user (bypasses allow list) or in the allow list.
    is_in_allow_list = accounts_client.is_in_allow_list(db, email)

    if not is_in_allow_list and not invite_code:
        raise HTTPException(status_code=403, detail=l10n('not-in-allow-list'))
    elif not is_in_allow_list and invite_code:
        # For slightly nicer error handling do the invite code check now.
        # Only if they're not in the allow list and have an invite code.
        if not repo.invite.code_exists(db, invite_code):
            raise HTTPException(404, l10n('invite-code-not-valid'))
        if not repo.invite.code_is_available(db, invite_code):
            raise HTTPException(403, l10n('invite-code-not-valid'))

    url, state = accounts_client.get_redirect_url(token_urlsafe(32))

    request.session['tb_accounts_state'] = state
    request.session['tb_accounts_user_email'] = email
    request.session['tb_accounts_user_timezone'] = timezone
    request.session['tb_accounts_user_invite_code'] = invite_code

    return {'url': url}


@router.get('/auth/accounts/callback')
def accounts_callback(
    request: Request,
    user_session_id: str,
    state: str,
    db: Session = Depends(get_db),
    shared_redis_client: Redis = Depends(get_shared_redis),
    accounts_client: AccountsClient = Depends(get_accounts_client),
):
    """Auth callback from accounts. It's a bit of a journey:
    - We first ensure the state has not changed during the authentication process.
    - We setup the accounts client connection.
    - We retrieve the profile from the user session id returned to us in this flow.
        - That pings a shared redis cache, if the user information isn't there the user never logged in to accounts.
    - We attempt to retrieve the user by uuid, and by email.
        - If both fail then we create a new user.
    - We then create or update an external connection for the accounts connection details.
    - We give set the accounts session key in the user's session (cookie) so they can use it for authentication.
    - And finally we send them back to the frontend.
    """
    if not AuthScheme.is_accounts():
        raise HTTPException(status_code=405)

    if 'tb_accounts_state' not in request.session or request.session['tb_accounts_state'] != state:
        raise HTTPException(400, 'Invalid state.')
    if 'tb_accounts_user_email' not in request.session or request.session['tb_accounts_user_email'] == '':
        raise HTTPException(400, 'Email could not be retrieved.')

    # Decode the user session
    user_session_id = base64.b64decode(user_session_id).decode()

    email = request.session['tb_accounts_user_email']
    # We only use timezone during subscriber creation, or if their timezone is None
    timezone = request.session['tb_accounts_user_timezone']
    invite_code = request.session.get('tb_accounts_user_invite_code')

    # Clear session keys
    request.session.pop('tb_accounts_state')
    request.session.pop('tb_accounts_user_email')
    request.session.pop('tb_accounts_user_timezone')
    if invite_code:
        request.session.pop('tb_accounts_user_invite_code')

    accounts_client.setup()

    # Retrieve credentials and user profile
    profile = shared_redis_client.get(f'{REDIS_USER_SESSION_PROFILE_KEY}.{user_session_id}')

    if not profile:
        accounts_client.logout()
        raise HTTPException(400, l10n('email-mismatch'))

    profile = json.loads(profile)

    if profile['email'] != email:
        accounts_client.logout()
        raise HTTPException(400, l10n('email-mismatch'))

    accounts_subscriber = repo.external_connection.get_subscriber_by_accounts_uuid(db, profile.get('uuid'))
    # Also look up the subscriber (in case we have an existing account that's not tied to a given uuid)
    subscriber = repo.subscriber.get_by_email(db, email)

    new_subscriber_flow = not accounts_subscriber and not subscriber

    if new_subscriber_flow:
        # Double check:
        # Ensure the invite code exists and is available
        # Use some inline-errors for now. We don't have a good error flow!
        is_in_allow_list = accounts_client.is_in_allow_list(db, email)

        if not is_in_allow_list:
            if not repo.invite.code_exists(db, invite_code):
                raise HTTPException(404, l10n('invite-code-not-valid'))
            if not repo.invite.code_is_available(db, invite_code):
                raise HTTPException(403, l10n('invite-code-not-valid'))

        subscriber = repo.subscriber.create(
            db,
            schemas.SubscriberBase(
                email=email,
                username=email,
                timezone=timezone,
            ),
        )

        # Give them 10 invites
        repo.invite.generate_codes(db, INVITES_TO_GIVE_OUT, subscriber.id)

        if not is_in_allow_list:
            # Use the invite code after we've created the new subscriber
            used = repo.invite.use_code(db, invite_code, subscriber.id)

            # This shouldn't happen, but just in case!
            if not used:
                repo.subscriber.hard_delete(db, subscriber)
                raise HTTPException(500, l10n('unknown-error'))

    elif not subscriber:
        subscriber = accounts_subscriber

    # Only proceed if user account is enabled (which is the default case for new users)
    if subscriber.is_deleted:
        raise HTTPException(status_code=403, detail=l10n('disabled-account'))

    accounts_connection = repo.external_connection.get_by_type(db, subscriber.id, ExternalConnectionType.accounts)

    # If we have accounts_connection, ensure the incoming one matches our known one.
    # This shouldn't occur, but it's a safety check in-case we missed a webhook push.
    if any([profile['uuid'] != ec.type_id for ec in accounts_connection]):
        # Ensure sentry captures the error too!
        if os.getenv('SENTRY_DSN') != '':
            e = Exception('Invalid Credentials, incoming profile uid does not match existing profile uid')
            capture_exception(e)

        raise HTTPException(403, l10n('invalid-credentials'))

    external_connection_schema = schemas.ExternalConnection(
        name=profile['email'],
        type=ExternalConnectionType.accounts,
        type_id=profile['uuid'],
        owner_id=subscriber.id,
        token=json.dumps({'access': user_session_id}),
    )

    if not accounts_subscriber:
        repo.external_connection.create(db, external_connection_schema)
    else:
        repo.external_connection.update_token(
            db,
            json.dumps({'access': user_session_id}),
            subscriber.id,
            external_connection_schema.type,
            external_connection_schema.type_id,
        )

    # Update profile with fxa info
    data = schemas.SubscriberIn(
        avatar_url=profile['avatar_url'],
        name=subscriber.name,
        username=subscriber.username,
        email=profile['email'],
        timezone=timezone if subscriber.timezone is None else None,
    )

    # If they're a new subscriber we should fill in some defaults!
    if new_subscriber_flow:
        data.name = profile['display_name'] if 'display_name' in profile else profile['email'].split('@')[0]
        data.username = profile['email']

    repo.subscriber.update(db, data, subscriber.id)

    request.session['accounts_session'] = user_session_id

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/post-login/")


@router.get('/fxa_login')
def fxa_login(
    request: Request,
    email: str,
    timezone: str | None = None,
    invite_code: str | None = None,
    db: Session = Depends(get_db),
    fxa_client: FxaClient = Depends(get_fxa_client),
):
    """Request an authorization url from fxa"""
    if not AuthScheme.is_fxa():
        raise HTTPException(status_code=405)

    fxa_client.setup()

    # Normalize email address to lower case
    email = email.lower()

    # Check if they're in the allowed list, but only if they didn't provide an invite code
    # This checks to see if they're already a user (bypasses allow list) or in the allow list.
    is_in_allow_list = fxa_client.is_in_allow_list(db, email)

    if not is_in_allow_list and not invite_code:
        raise HTTPException(status_code=403, detail=l10n('not-in-allow-list'))
    elif not is_in_allow_list and invite_code:
        # For slightly nicer error handling do the invite code check now.
        # Only if they're not in the allow list and have an invite code.
        if not repo.invite.code_exists(db, invite_code):
            raise HTTPException(404, l10n('invite-code-not-valid'))
        if not repo.invite.code_is_available(db, invite_code):
            raise HTTPException(403, l10n('invite-code-not-valid'))

    url, state = fxa_client.get_redirect_url(db, token_urlsafe(32), email)

    request.session['fxa_state'] = state
    request.session['fxa_user_email'] = email
    request.session['fxa_user_timezone'] = timezone
    request.session['fxa_user_invite_code'] = invite_code

    return {'url': url}


@router.get('/fxa')
def fxa_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    fxa_client: FxaClient = Depends(get_fxa_client),
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
    # These are error keys on the frontend
    # login.remoteError.<id>
    errors = {
        'email-mismatch': 'email-mismatch',
        'invite-not-valid': 'invite-not-valid',
        'unknown-error': 'unknown-error',
        'disabled-account': 'disabled-account',
        'invalid-credentials': 'invalid-credentials',
        'invalid-state': 'invalid-state',
        'email-not-in-session': 'email-not-in-session',
    }

    if not AuthScheme.is_fxa():
        raise HTTPException(status_code=405)

    if 'fxa_state' not in request.session or request.session['fxa_state'] != state:
        return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['invalid-state']}")
    if 'fxa_user_email' not in request.session or request.session['fxa_user_email'] == '':
        return RedirectResponse(
            f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['email-not-in-session']}"
        )

    email = request.session['fxa_user_email'].lower()
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

    if email == '' or profile.get('email', '').lower() != email:
        fxa_client.logout()
        return RedirectResponse(
            f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['email-mismatch']}"
        )

    # Check if we have an existing fxa connection by profile's uid
    fxa_subscriber = repo.external_connection.get_subscriber_by_fxa_uid(db, profile['uid'])
    # Also look up the subscriber (in case we have an existing account that's not tied to a given fxa account)
    subscriber = repo.subscriber.get_by_email(db, email)

    new_subscriber_flow = not fxa_subscriber and not subscriber

    if new_subscriber_flow:
        # Double check:
        # Ensure the invite code exists and is available
        # Use some inline-errors for now. We don't have a good error flow!
        is_in_allow_list = fxa_client.is_in_allow_list(db, email)

        if not is_in_allow_list:
            if not repo.invite.code_exists(db, invite_code):
                return RedirectResponse(
                    f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['invite-not-valid']}"
                )
            if not repo.invite.code_is_available(db, invite_code):
                return RedirectResponse(
                    f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['invite-not-valid']}"
                )

        subscriber = repo.subscriber.create(
            db,
            schemas.SubscriberBase(
                email=email,
                username=email,
                timezone=timezone,
            ),
        )

        # Give them 10 invites
        repo.invite.generate_codes(db, INVITES_TO_GIVE_OUT, subscriber.id)

        if not is_in_allow_list:
            # Use the invite code after we've created the new subscriber
            used = repo.invite.use_code(db, invite_code, subscriber.id)

            # This shouldn't happen, but just in case!
            if not used:
                repo.subscriber.hard_delete(db, subscriber)
                return RedirectResponse(
                    f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['unknown-error']}"
                )

    elif not subscriber:
        subscriber = fxa_subscriber

    # Only proceed if user account is enabled (which is the default case for new users)
    if subscriber.is_deleted:
        return RedirectResponse(
            f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['disabled-account']}"
        )

    fxa_connections = repo.external_connection.get_by_type(db, subscriber.id, ExternalConnectionType.fxa)

    # If we have fxa_connections, ensure the incoming one matches our known one.
    # This shouldn't occur, but it's a safety check in-case we missed a webhook push.
    if any([profile['uid'] != ec.type_id for ec in fxa_connections]):
        # Ensure sentry captures the error too!
        if os.getenv('SENTRY_DSN') != '':
            e = Exception('Invalid Credentials, incoming profile uid does not match existing profile uid')
            capture_exception(e)

        return RedirectResponse(
            f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login/?error={errors['invalid-credentials']}"
        )

    external_connection_schema = schemas.ExternalConnection(
        name=profile['email'],
        type=ExternalConnectionType.fxa,
        type_id=profile['uid'],
        owner_id=subscriber.id,
        token=json.dumps(creds),
    )

    if not fxa_subscriber:
        repo.external_connection.create(db, external_connection_schema)
    else:
        repo.external_connection.update_token(
            db, json.dumps(creds), subscriber.id, external_connection_schema.type, external_connection_schema.type_id
        )

    # Update profile with fxa info
    data = schemas.SubscriberIn(
        avatar_url=profile['avatar'],
        name=subscriber.name,
        username=subscriber.username,
        email=profile['email'],
        timezone=timezone if subscriber.timezone is None else None,
    )

    # If they're a new subscriber we should fill in some defaults!
    if new_subscriber_flow:
        data.name = profile['displayName'] if 'displayName' in profile else profile['email'].split('@')[0]
        data.username = profile['email']

    repo.subscriber.update(db, data, subscriber.id)

    # Generate our jwt token, we only store the username on the token
    access_token_expires = timedelta(minutes=float(10))
    one_time_access_token = create_access_token(
        data={'sub': f'uid-{subscriber.id}', 'jti': secrets.token_urlsafe(16)}, expires_delta=access_token_expires
    )

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/post-login/{one_time_access_token}")


@router.post('/fxa-token')
def fxa_token(subscriber=Depends(get_subscriber_from_onetime_token)):
    """Generate a access token from a one time token retrieved after login"""
    if not AuthScheme.is_fxa() and not AuthScheme.is_accounts():
        raise HTTPException(status_code=405)

    # Generate our jwt token, we only store the username on the token
    access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))
    access_token = create_access_token(
        data={
            'sub': f'uid-{subscriber.id}',
        },
        expires_delta=access_token_expires,
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/token')
def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    if not AuthScheme.is_password():
        raise HTTPException(status_code=405)

    has_subscribers = db.query(Subscriber).count()

    if os.getenv('APP_ALLOW_FIRST_TIME_REGISTER') == 'True' and has_subscribers == 0:
        # Create an initial subscriber based with the UTC timezone, the FTUE will give them a change to adjust this
        create_subscriber(db, form_data.username, form_data.password, 'UTC')

    """Retrieve an access token from a given email (=username) and password."""
    subscriber = repo.subscriber.get_by_email(db, form_data.username)
    if not subscriber or subscriber.password is None:
        raise HTTPException(status_code=403, detail=l10n('invalid-credentials'))

    # Only proceed if user account is enabled
    if subscriber.is_deleted:
        raise HTTPException(status_code=403, detail=l10n('disabled-account'))

    # Verify the incoming password, and re-hash our password if needed
    try:
        utils.verify_password(form_data.password, subscriber.password)
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(status_code=403, detail=l10n('invalid-credentials'))

    if utils.ph.check_needs_rehash(subscriber.password):
        subscriber.password = utils.get_password_hash(form_data.password)
        db.add(subscriber)
        db.commit()

    # Generate our jwt token, we only store the user id on the token
    access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))
    access_token = create_access_token(data={'sub': f'uid-{subscriber.id}'}, expires_delta=access_token_expires)

    """Log a user in with the passed user id and password information"""
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/logout')
def logout(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
    fxa_client: FxaClient = Depends(get_fxa_client),
    accounts_client: AccountsClient = Depends(get_accounts_client),
):
    """Logout a given subscriber session"""
    auth_client = None

    if AuthScheme.is_fxa():
        fxa_client.setup(subscriber.id, subscriber.get_external_connection(ExternalConnectionType.fxa).token)
        auth_client = fxa_client
    elif AuthScheme.is_accounts():
        blob = subscriber.get_external_connection(ExternalConnectionType.accounts).token
        token = json.loads(blob)
        if token:
            accounts_client.setup(subscriber.id, token.get('access'))
            auth_client = accounts_client

    # Don't set a minimum_valid_iat_time here.
    auth.logout(db, subscriber, auth_client, deny_previous_tokens=False)

    return True


@router.get('/me', response_model=schemas.SubscriberMeOut)
def me(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Return the currently authed user model"""

    hash = subscriber.unique_hash

    return schemas.SubscriberMeOut(
        username=subscriber.username,
        email=subscriber.email,
        preferred_email=subscriber.preferred_email,
        name=subscriber.name,
        level=subscriber.level,
        timezone=subscriber.timezone,
        avatar_url=subscriber.avatar_url,
        is_setup=subscriber.is_setup,
        schedule_links=schedule_links_by_subscriber(db, subscriber),
        unique_hash=hash,
        language=subscriber.language,
        colour_scheme=subscriber.colour_scheme,
        time_mode=subscriber.time_mode,
    )


@router.post('/permission-check')
def permission_check(subscriber: Subscriber = Depends(get_admin_subscriber)):
    """Checks if they have admin permissions"""
    # This should already be covered, but just in case!
    if subscriber.is_deleted:
        raise validation.InvalidPermissionLevelException()
    return True  # Covered by get_admin_subscriber
