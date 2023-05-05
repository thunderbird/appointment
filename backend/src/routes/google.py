import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.responses import RedirectResponse

from ..controller.google import GoogleClient
from ..database import repo
from ..database.database import SessionLocal
from sqlalchemy.orm import Session

from ..database.schemas import CalendarConnection
from ..dependencies.auth import get_subscriber

from ..database.models import Subscriber, CalendarProvider
from ..dependencies.google import get_google_client

router = APIRouter()


def get_db():
    """run database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/auth")
def google_auth(google_client : GoogleClient = Depends(get_google_client), db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Starts the google oauth process"""
    return google_client.get_redirect_url(db, subscriber.id)


@router.get("/callback")
def google_callback(code: str, state: str, google_client : GoogleClient = Depends(get_google_client), db: Session = Depends(get_db)):
    """Callback for google to redirect the user back to us with a code"""
    creds = google_client.get_credentials(code)

    if creds is None:
        raise HTTPException(status_code=401, detail="Google authentication credentials are not valid")

    subscriber = repo.get_subscriber_by_google_state(db, state)

    if subscriber is None:
        raise HTTPException(status_code=401, detail="Google authentication failed")

    if not subscriber.google_state_expires_at or subscriber.google_state_expires_at < datetime.now():
        # Clear state for our db copy
        repo.set_subscriber_google_state(db, None, subscriber.id)

        raise HTTPException(status_code=401, detail="Google authentication session expired, please try again.")

    # Clear state for our db copy
    repo.set_subscriber_google_state(db, None, subscriber.id)

    # Store credentials in db. Since creds include client secret don't expose to end-user!
    creds_serialized = creds.to_json()
    repo.set_subscriber_google_tkn(db, creds_serialized, subscriber.id)

    # Grab all of the google calendars
    calendars = google_client.list_calendars(creds)
    for calendar in calendars:
        cal = CalendarConnection(title=calendar.get('summary'), color=calendar.get('backgroundColor'), user=calendar.get('id'), password='', url=calendar.get('id'), provider=CalendarProvider.google)
        # add calendar
        new_cal = repo.create_subscriber_calendar(db=db, calendar=cal, subscriber_id=subscriber.id)
        error_occured = new_cal is None

    # And then redirect back to frontend
    # TODO: if we have notifications later, send error_occured with url
    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar")
