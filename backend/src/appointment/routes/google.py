import os
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from ..controller.apis.google_client import GoogleClient
from ..database import repo
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber
from ..dependencies.google import get_google_client
from ..exceptions.google_api import GoogleInvalidCredentials
from ..exceptions.google_api import GoogleScopeChanged

router = APIRouter()


@router.get("/auth")
def google_auth(
    email: str | None = None,
    google_client: GoogleClient = Depends(get_google_client),
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Starts the google oauth process"""
    return google_client.get_redirect_url(email, db, subscriber.id)


@router.get("/callback")
def google_callback(
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
        return google_callback_error("You must enable Calendar and Event access to use Thunderbird Appointment.")
    except GoogleInvalidCredentials:
        return google_callback_error("Google authentication credentials are not valid")

    subscriber = repo.get_subscriber_by_google_state(db, state)

    if subscriber is None:
        return google_callback_error("Google authentication failed")

    if not subscriber.google_state_expires_at or subscriber.google_state_expires_at < datetime.now():
        # Clear state for our db copy
        repo.set_subscriber_google_state(db, None, subscriber.id)

        return google_callback_error("Google authentication session expired, please try again.")

    # Clear state for our db copy
    repo.set_subscriber_google_state(db, None, subscriber.id)

    # Store credentials in db. Since creds include client secret don't expose to end-user!
    creds_serialized = creds.to_json()
    repo.set_subscriber_google_tkn(db, creds_serialized, subscriber.id)

    error_occurred = google_client.sync_calendars(db, subscriber_id=subscriber.id, token=creds)

    # And then redirect back to frontend
    if error_occurred:
        return google_callback_error("An error occurred while syncing calendars. Please try again later.")

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar")


def google_callback_error(error: str):
    """Call if you encounter an unrecoverable error with the Google callback function"""
    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar?error={error}")
