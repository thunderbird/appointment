import datetime
import os

from authlib.integrations.requests_client import OAuth2Session
from requests import Response

from appointment.utils import get_expiry_time_with_grace_period


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

        expiry = data.get('exp')
        if expiry:
            # Grace period maxes out at 2 minutes (120 seconds)
            expiry = get_expiry_time_with_grace_period(expiry)
            if expiry < datetime.datetime.now(datetime.UTC).timestamp():
                return None

        # Ensure the token is ok
        if data.get('active') is not True:
            return None

        return data
