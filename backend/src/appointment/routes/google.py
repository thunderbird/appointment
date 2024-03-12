import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from ..controller.apis.google_client import GoogleClient
from ..database import repo, schemas
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber, ExternalConnectionType
from ..dependencies.google import get_google_client
from ..exceptions.google_api import GoogleInvalidCredentials
from ..exceptions.google_api import GoogleScopeChanged
from ..l10n import l10n

router = APIRouter()


@router.get("/auth")
def google_auth(
    request: Request,
    email: str | None = None,
    google_client: GoogleClient = Depends(get_google_client),
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Starts the google oauth process"""
    url, state = google_client.get_redirect_url(email)

    request.session['google_oauth_state'] = state
    request.session['google_oauth_subscriber_id'] = subscriber.id

    return url


@router.get("/callback")
def google_callback(
    request: Request,
    code: str,
    state: str,
    google_client: GoogleClient = Depends(get_google_client),
    db: Session = Depends(get_db),
):
    """Callback for google to redirect the user back to us with a code.
    This is called directly, and is not an api function!"""
    try:
        creds = google_client.get_credentials(code)
    except GoogleScopeChanged:
        return google_callback_error(l10n('google-scope-changed'))
    except GoogleInvalidCredentials:
        return google_callback_error(l10n('google-invalid-creds'))

    if 'google_oauth_state' not in request.session or request.session['google_oauth_state'] != state:
        return google_callback_error(l10n('google-auth-fail'))

    subscriber_id = request.session.get('google_oauth_subscriber_id')
    subscriber = repo.get_subscriber(db, subscriber_id)

    # Clear session keys
    request.session.pop('google_oauth_state')
    request.session.pop('google_oauth_subscriber_id')

    if subscriber is None:
        return google_callback_error(l10n('google-auth-fail'))

    profile = google_client.get_profile(token=creds)
    google_email = profile.get('email')
    google_id = profile.get('id')

    # We need sub, it should always be there, but we should bail if it's not.
    if google_id is None:
        return google_callback_error(l10n('google-auth-fail'))

    external_connection = repo.get_external_connections_by_type(db, subscriber.id, ExternalConnectionType.google, google_id)

    # Create or update the external connection
    if not external_connection:
        external_connection_schema = schemas.ExternalConnection(
            name=google_email,
            type=ExternalConnectionType.google,
            type_id=google_id,
            owner_id=subscriber.id,
            token=creds.to_json()
        )

        repo.create_subscriber_external_connection(db, external_connection_schema)
    else:
        repo.update_subscriber_external_connection_token(db, creds.to_json(), subscriber.id,
                                                         ExternalConnectionType.google, google_id)

    error_occurred = google_client.sync_calendars(db, subscriber_id=subscriber.id, token=creds)

    # And then redirect back to frontend
    if error_occurred:
        return google_callback_error(l10n('google-sync-fail'))

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar")


def google_callback_error(error: str):
    """Call if you encounter an unrecoverable error with the Google callback function"""
    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar?error={error}")
