import os

from authlib.integrations.requests_client import OAuth2Session
from requests import Response


class OIDCClient:
    client: OAuth2Session

    def __init__(self):
        self.client = OAuth2Session(
            client_id=os.getenv('OIDC_CLIENT_ID'), client_secret=os.getenv('OIDC_CLIENT_SECRET')
        )

    def introspect_token(self, access_token) -> dict | None:
        response: Response = self.client.introspect_token(
            os.getenv('OIDC_TOKEN_INTROSPECTION_URL'), token=access_token, token_type_hint='access_token'
        )

        data = response.json()

        # Ensure the token is ok
        if data.get('active') is not True:
            return None

        return data
