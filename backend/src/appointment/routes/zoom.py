import json
import os

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..controller import zoom
from ..controller.apis.zoom_client import ZoomClient
from ..controller.auth import sign_url
from ..database import repo, schemas
from ..database.models import Subscriber, ExternalConnectionType
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db
from ..dependencies.zoom import get_zoom_client
from ..exceptions.validation import OAuthFlowNotFinished
from ..exceptions.zoom_api import ZoomScopeChanged
from ..l10n import l10n

router = APIRouter()

SESSION_OAUTH_STATE = 'zoom_state'
SESSION_OAUTH_SUBSCRIBER_ID = 'zoom_user_id'


def zoom_callback_error(is_setup: bool, error: str):
    """Call if you encounter an unrecoverable error with the Zoom callback function"""
    # Redirect non-setup subscribers back to the setup page
    if not is_setup:
        return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/setup")

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/connectedAccounts?error={error}")


@router.get('/ftue-status')
def zoom_auth_status(request: Request, subscriber: Subscriber = Depends(get_subscriber)):
    """Checks if oauth flow has started but not finished, if so raises an error."""
    same_subscriber = subscriber.id == request.session.get(SESSION_OAUTH_SUBSCRIBER_ID)
    in_progress = request.session.get(SESSION_OAUTH_STATE, False) and same_subscriber

    if in_progress:
        raise OAuthFlowNotFinished(message_key='zoom-connect-to-continue')

    return True


@router.get('/auth')
def zoom_auth(
    request: Request,
    subscriber: Subscriber = Depends(get_subscriber),
    zoom_client: ZoomClient = Depends(get_zoom_client),
):
    """Starts the zoom oauth process"""

    url, state = zoom_client.get_redirect_url(state=sign_url(str(subscriber.id)))

    # We'll need to store this in session
    request.session[SESSION_OAUTH_STATE] = state
    request.session[SESSION_OAUTH_SUBSCRIBER_ID] = subscriber.id

    return {'url': url}


@router.get('/callback')
def zoom_callback(
    request: Request,
    code: str,
    state: str,
    db=Depends(get_db),
):
    if SESSION_OAUTH_STATE not in request.session or request.session[SESSION_OAUTH_STATE] != state:
        raise HTTPException(400, l10n('oauth-error'))
    if SESSION_OAUTH_SUBSCRIBER_ID not in request.session or SESSION_OAUTH_SUBSCRIBER_ID == '':
        raise HTTPException(400, l10n('oauth-error'))

    # Retrieve the user id set at the start of the zoom oauth process
    subscriber = repo.subscriber.get(db, request.session[SESSION_OAUTH_SUBSCRIBER_ID])

    # Clear zoom session keys
    request.session.pop(SESSION_OAUTH_STATE)
    request.session.pop(SESSION_OAUTH_SUBSCRIBER_ID)

    # Generate the zoom client instance based on our subscriber
    # This can't be set as a dep injection since subscriber is based on session.
    zoom_client: ZoomClient = get_zoom_client(subscriber)

    try:
        creds = zoom_client.get_credentials(code)
    except ZoomScopeChanged:
        # Use unknown error as we'll collect the information in sentry
        return zoom_callback_error(subscriber.is_setup, l10n('zoom-unknown-error'))

    # Get the zoom user info, so we can associate their id with their appointment subscriber
    zoom_user_info = zoom_client.get_me()

    external_connection_schema = schemas.ExternalConnection(
        name=zoom_user_info['email'],
        type=ExternalConnectionType.zoom,
        type_id=zoom_user_info['id'],
        owner_id=subscriber.id,
        token=json.dumps(creds),
    )

    if (
        len(
            repo.external_connection.get_by_type(
                db, subscriber.id, external_connection_schema.type, external_connection_schema.type_id
            )
        )
        == 0
    ):
        repo.external_connection.create(db, external_connection_schema)

    # Redirect non-setup subscribers back to the setup page
    if not subscriber.is_setup:
        return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/setup")

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/connectedAccounts")


@router.post('/disconnect')
def disconnect_account(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """We only have one zoom account, so we can just remove it. If it doesn't even exist return false."""
    zoom_connection = subscriber.get_external_connection(ExternalConnectionType.zoom)

    if zoom_connection:
        zoom.disconnect(db, subscriber.id, zoom_connection.type_id)
    else:
        return False

    return True
