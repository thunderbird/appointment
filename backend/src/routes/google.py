import os
import json
import logging
import uuid

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.responses import RedirectResponse
from fastapi_auth0 import Auth0User

from src.controller.google import GoogleClient
from src.controller.auth import Auth
from src.database import repo
from src.database.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()
auth = Auth()

# Maybe not the best place for this, but works for now!
google_client = GoogleClient(os.getenv("GOOGLE_AUTH_CLIENT_ID"), os.getenv("GOOGLE_AUTH_SECRET"),
                             os.getenv("GOOGLE_AUTH_PROJECT_ID"), os.getenv("GOOGLE_AUTH_CALLBACK"))

def get_db():
  """run database session"""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

try:
    google_client.setup()
except:
    # google client setup was not possible
    logging.warning('[routes.google] Google Client could not be setup, bad credentials?')


@router.get("/auth", dependencies=[Depends(auth.auth0.implicit_scheme)])
def google_auth(user: Auth0User = Security(auth.auth0.get_user)):
    """Starts the google oauth process"""
    return google_client.get_redirect_url()


@router.get("/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """Callback for google to redirect the user back to us with a code"""
    creds = google_client.get_credentials(code)

    if creds is None:
        raise HTTPException(status_code=401, detail="Google authentication credentials are not valid")

    # Store credentials in db. Since creds include client secret don't expose to end-user!
    """
    Sample output:
    {"token": "<the token>", "refresh_token": "<refresh token>", "token_uri": "<token uri>", "client_id": "<client id>", "client_secret": "<client secret>", "scopes": <scopes>, "expiry": "2023-04-18T18:41:10.317778Z"}
    """
    # TODO get currently logged in user
    # subscriber = repo.get_subscriber_by_email(db=db, email=user.email)
    repo.set_subscriber_google_tkn(db, creds.to_json(), subscriber.id)
    # TOKEN_PATH = './src/tmp/test.json' # TODO
    # credentials = json.loads(creds.to_json())
    # token = credentials["token"]
    # refresh_token = credentials["refresh_token"]
    # with open(TOKEN_PATH, 'w') as token:
        # token.write(creds.to_json())

    # And then RedirectResponse back to frontend :)
    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/calendar")
