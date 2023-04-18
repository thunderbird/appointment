from google_auth_oauthlib.flow import Flow


class GoogleClient:
    """Authenticates with Google OAuth and allows the retrieval of Google Calendar information"""
    SCOPES = ['https://www.googleapis.com/auth/calendar']
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

    def get_redirect_url(self):
        """Returns the redirect url for the google oauth flow"""
        if self.client is None:
            return None

        # (Url, State ID)
        return self.client.authorization_url()[0]

    def get_credentials(self, code):
        if self.client is None:
            return None

        self.client.fetch_token(code=code)
        return self.client.credentials
