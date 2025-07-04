import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from ..controller.apis.google_client import GoogleClient
from ..database import repo, schemas, models
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber, ExternalConnectionType
from ..dependencies.google import get_google_client
from ..exceptions.google_api import GoogleInvalidCredentials
from ..exceptions.google_api import GoogleScopeChanged
from ..exceptions.validation import OAuthFlowNotFinished
from ..l10n import l10n

router = APIRouter()

SESSION_OAUTH_STATE = 'google_oauth_state'
SESSION_OAUTH_SUBSCRIBER_ID = 'google_oauth_subscriber_id'


@router.get('/ftue-status')
def google_auth_status(
    request: Request,
    subscriber: Subscriber = Depends(get_subscriber)
):
    """Checks if oauth flow has started but not finished, if so raises an error."""
    same_subscriber = subscriber.id == request.session.get(SESSION_OAUTH_SUBSCRIBER_ID)
    in_progress = request.session.get(SESSION_OAUTH_STATE, False) and same_subscriber

    if in_progress:
        raise OAuthFlowNotFinished(message_key='google-connect-to-continue')

    return True


@router.get('/auth')
def google_auth(
    request: Request,
    email: str | None = None,
    google_client: GoogleClient = Depends(get_google_client),
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Starts the google oauth process"""
    if email:
        email = email.lower()
    url, state = google_client.get_redirect_url(email)

    request.session[SESSION_OAUTH_STATE] = state
    request.session[SESSION_OAUTH_SUBSCRIBER_ID] = subscriber.id

    return url


@router.get('/callback')
def google_callback(
    request: Request,
    state: str,
    code: str | None = None,
    error: str | None = None,
    google_client: GoogleClient = Depends(get_google_client),
    db: Session = Depends(get_db),
):
    """Callback for google to redirect the user back to us with a code.
    This is called directly, and is not an api function!"""
    subscriber_id = request.session.get(SESSION_OAUTH_SUBSCRIBER_ID)
    subscriber = repo.subscriber.get(db, subscriber_id)
    # Not the end of the world if someone gets redirected to /calendar
    # because that will redirect them to setup if they're not setup!
    is_setup = subscriber.is_setup if subscriber else True

    if error is not None:
        # Specific error for cancelling the flow
        if error == 'access_denied':
            return google_callback_error(is_setup, l10n('google-connect-to-continue'))
        return google_callback_error(is_setup, l10n('google-sync-fail'))

    try:
        creds = google_client.get_credentials(code)
    except GoogleScopeChanged:
        return google_callback_error(is_setup, l10n('google-scope-changed'))
    except GoogleInvalidCredentials:
        return google_callback_error(is_setup, l10n('google-invalid-creds'))

    if SESSION_OAUTH_STATE not in request.session or request.session[SESSION_OAUTH_STATE] != state:
        return google_callback_error(is_setup, l10n('google-auth-fail'))

    # Clear session keys
    request.session.pop(SESSION_OAUTH_STATE)
    request.session.pop(SESSION_OAUTH_SUBSCRIBER_ID)

    if subscriber is None:
        return google_callback_error(is_setup, l10n('google-auth-fail'))

    profile = google_client.get_profile(token=creds)
    google_email = profile.get('email')
    google_id = profile.get('id')

    # We need sub, it should always be there, but we should bail if it's not.
    if google_id is None:
        return google_callback_error(is_setup, l10n('google-auth-fail'))

    external_connection = repo.external_connection.get_by_type(
        db, subscriber.id, ExternalConnectionType.google, google_id
    )

    # Create or update the external connection
    if not external_connection:
        external_connection_schema = schemas.ExternalConnection(
            name=google_email,
            type=ExternalConnectionType.google,
            type_id=google_id,
            owner_id=subscriber.id,
            token=creds.to_json(),
        )

        external_connection = repo.external_connection.create(db, external_connection_schema)
    else:
        # get_by_type returns a list, but when type_id is provided, there should only be one
        external_connection = external_connection[0]

        repo.external_connection.update_token(
            db, creds.to_json(), subscriber.id, ExternalConnectionType.google, google_id
        )

    error_occurred = google_client.sync_calendars(
        db, subscriber_id=subscriber.id, token=creds, external_connection_id=external_connection.id
    )

    # And then redirect back to frontend
    if error_occurred:
        return google_callback_error(is_setup, l10n('google-sync-fail'))

    # Redirect non-setup subscribers back to the setup page
    if not is_setup:
        return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/setup")

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar")


def google_callback_error(is_setup: bool, error: str):
    """Call if you encounter an unrecoverable error with the Google callback function"""
    # Redirect non-setup subscribers back to the setup page
    if not is_setup:
        return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/setup")

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar?error={error}")


@router.post('/disconnect')
def disconnect_account(
    request_body: schemas.DisconnectGoogleAccountRequest,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Disconnects a google account. Removes associated data from our services and deletes the connection details."""
    google_connection = subscriber.get_external_connection(ExternalConnectionType.google, request_body.type_id)

    # Remove all of the google calendars on their given google connection
    repo.calendar.delete_by_subscriber_and_provider(
        db, subscriber.id, provider=models.CalendarProvider.google, external_connection_id=google_connection.id
    )

    # Unassociated any secondary emails if they're attached to their google connection
    if subscriber.secondary_email == google_connection.name.lower():
        subscriber.secondary_email = None
        db.add(subscriber)
        db.commit()

    # Remove their account details
    repo.external_connection.delete_by_type(db, subscriber.id, google_connection.type, google_connection.type_id)

    return True
