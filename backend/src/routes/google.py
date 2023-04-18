import os

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.controller.google import GoogleClient

router = APIRouter()

# Maybe not the best place for this, but works for now!
google_client = GoogleClient(os.getenv("GOOGLE_AUTH_CLIENT_ID"), os.getenv("GOOGLE_AUTH_SECRET"),
                             os.getenv("GOOGLE_AUTH_PROJECT_ID"), os.getenv("GOOGLE_AUTH_CALLBACK"))

try:
    google_client.setup()
except:
    print("WARNING: Google Client could not be setup, bad credentials?")


@router.get("/auth")
def auth():
    """Starts the google oauth process"""
    return RedirectResponse(google_client.get_redirect_url())


@router.get("/callback")
def callback(code: str):
    """Callback for google to redirect the user back to us with a code"""
    creds = google_client.get_credentials(code)

    if creds is None:
        return {}  # Error?

    # Maybe store token/refresh token in db or a session, creds include client secret so don't expose to end-user pls!
    """
    Sample output:
    {"token": "<the token>", "refresh_token": "<refresh token>", "token_uri": "<token uri>", "client_id": "<client id>", "client_secret": "<client secret>", "scopes": <scopes>, "expiry": "2023-04-18T18:41:10.317778Z"}
    """
    credentials = creds.to_json()
    token = credentials.get("token")
    refresh_token = credentials.get("refresh_token")

    # And then RedirectResponse back to frontend :)
    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar")
