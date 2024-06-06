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

    request.session["google_oauth_state"] = state
    request.session["google_oauth_subscriber_id"] = subscriber.id

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
        return google_callback_error(l10n("google-scope-changed"))
    except GoogleInvalidCredentials:
        return google_callback_error(l10n("google-invalid-creds"))

    if "google_oauth_state" not in request.session or request.session["google_oauth_state"] != state:
        return google_callback_error(l10n("google-auth-fail"))

    subscriber_id = request.session.get("google_oauth_subscriber_id")
    subscriber = repo.subscriber.get(db, subscriber_id)

    # Clear session keys
    request.session.pop("google_oauth_state")
    request.session.pop("google_oauth_subscriber_id")

    if subscriber is None:
        return google_callback_error(l10n("google-auth-fail"))

    profile = google_client.get_profile(token=creds)
    google_email = profile.get("email")
    google_id = profile.get("id")

    # We need sub, it should always be there, but we should bail if it's not.
    if google_id is None:
        return google_callback_error(l10n("google-auth-fail"))

    external_connection = repo.external_connection.get_by_type(
        db, subscriber.id, ExternalConnectionType.google, google_id
    )

    # Create an artificial limit of one google account per account, mainly because we didn't plan for multiple accounts!
    remainder = list(
        filter(
            lambda ec: ec.type_id != google_id,
            repo.external_connection.get_by_type(db, subscriber.id, ExternalConnectionType.google),
        )
    )

    if len(remainder) > 0:
        return google_callback_error(l10n("google-only-one"))

    # Create or update the external connection
    if not external_connection:
        external_connection_schema = schemas.ExternalConnection(
            name=google_email,
            type=ExternalConnectionType.google,
            type_id=google_id,
            owner_id=subscriber.id,
            token=creds.to_json(),
        )

        repo.external_connection.create(db, external_connection_schema)
    else:
        repo.external_connection.update_token(
            db, creds.to_json(), subscriber.id, ExternalConnectionType.google, google_id
        )

    error_occurred = google_client.sync_calendars(db, subscriber_id=subscriber.id, token=creds)

    # And then redirect back to frontend
    if error_occurred:
        return google_callback_error(l10n("google-sync-fail"))

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar")


def google_callback_error(error: str):
    """Call if you encounter an unrecoverable error with the Google callback function"""
    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar?error={error}")


@router.post("/disconnect")
def disconnect_account(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Disconnects a google account. Removes associated data from our services and deletes the connection details."""
    google_connection = subscriber.get_external_connection(ExternalConnectionType.google)

    # Remove all of their google calendars (We only support one connection so this should be good for now)
    repo.calendar.delete_by_subscriber_and_provider(db, subscriber.id, provider=models.CalendarProvider.google)

    # Unassociated any secondary emails if they're attached to their google connection
    if subscriber.secondary_email == google_connection.name:
        subscriber.secondary_email = None
        db.add(subscriber)
        db.commit()

    # Remove their account details
    repo.external_connection.delete_by_type(db, subscriber.id, google_connection.type, google_connection.type_id)

    return True
