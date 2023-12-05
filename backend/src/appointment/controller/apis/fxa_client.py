import json
import os

from requests_oauthlib import OAuth2Session
from ...database import models, repo


class FxaClient:
    OAUTH_API_URL = os.getenv('FXA_OAUTH_URL')
    ACCOUNTS_API_URL = os.getenv('FXA_ACCOUNTS_URL')
    PROFILE_API_URL = os.getenv('FXA_PROFILE_URL')

    SCOPES = [
        "profile",
    ]

    client: OAuth2Session | None = None
    subscriber_id: int | None = None

    def __init__(self, api_url, client_id, client_secret, callback_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.subscriber_id = None
        self.client = None

    def setup(self, subscriber_id=None, token=None):
        """Setup our oAuth session"""
        if type(token) is str:
            token = json.loads(token)

        self.subscriber_id = subscriber_id
        self.client = OAuth2Session(self.client_id, redirect_uri=self.callback_url, scope=self.SCOPES,
                                    auto_refresh_url=self.OAUTH_API_URL + '/v1/token',
                                    auto_refresh_kwargs={"client_id": self.client_id, "client_secret": self.client_secret},
                                    token=token,
                                    token_updater=self.token_saver)

        pass

    def get_redirect_url(self, state):
        url, state = self.client.authorization_url(
            self.ACCOUNTS_API_URL + '/authorization',
            state=state,
            access_type='offline',
            entrypoint='tbappointment',
        )
        print(">>> REDIREECT URL ", url, state)

        return url, state

    def get_credentials(self, code: str):
        return self.client.fetch_token(self.OAUTH_API_URL + '/v1/token', code, client_secret=self.client_secret, include_client_id=True)

    def token_saver(self, token):
        """requests-oauth automagically calls this function when it has a new refresh token for us.
        This makes it a bit awkward but we make it work..."""
        from appointment.dependencies.database import get_db

        self.client.token = token

        # Need a subscriber attached to this request in order to save a token
        if self.subscriber_id is None:
            return

        repo.update_subscriber_external_connection_token(get_db(), json.dumps(token), self.subscriber_id, models.ExternalConnectionType.fxa)

    def get_profile(self):
        print("Profile url >> ", self.PROFILE_API_URL + '/v1/profile')
        return self.client.get(url=self.PROFILE_API_URL + '/v1/profile').json()
