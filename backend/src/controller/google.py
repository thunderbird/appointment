import logging

import requests
from google_auth_oauthlib.flow import Flow
from src.database import repo

class GoogleClient:
    """Authenticates with Google OAuth and allows the retrieval of Google Calendar information"""
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email', 'openid']
    client: Flow | None

    def __init__(self, client_id, client_secret, project_id, callback_url):
        self.config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "project_id": project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        self.callback_url = callback_url
        self.client = None

    def setup(self):
        """Actually create the client, this is separate, so we can catch any errors without breaking everything"""
        self.client = Flow.from_client_config(self.config, self.SCOPES, redirect_uri=self.callback_url)

    def get_redirect_url(self, db, subscriber_id):
        """Returns the redirect url for the google oauth flow"""
        if self.client is None:
            return None

        # (Url, State ID)
        url, state = self.client.authorization_url()
        # Store the state id, so we can refer to it when google redirects the user to our callback
        repo.set_subscriber_google_state(db, state, subscriber_id)

        return url

    def get_credentials(self, code):
        if self.client is None:
            return None

        try:
            self.client.fetch_token(code=code)
            return self.client.credentials
        except ValueError as e:
            logging.error(f"[google.get_credentials] Value error while fetching credentials {str(e)}")
            return None

    def get_email(self, token):
        """Retrieve the user's email associated with the token"""
        if self.client is None:
            return None

        # Reference: https://developers.google.com/identity/openid-connect/openid-connect#obtaininguserprofileinformation
        response = requests.get('https://openidconnect.googleapis.com/v1/userinfo', headers={'Authorization': f"Bearer {token}"})
        userinfo = response.json()
        return userinfo.get('email')
