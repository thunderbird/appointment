import os

from authlib.integrations.requests_client import OAuth2Session
from requests import Response


class OIDCClient:
    client: OAuth2Session

    def __init__(self):
        # Ensure these values exist
        assert os.getenv('OIDC_CLIENT_ID')
        assert os.getenv('OIDC_CLIENT_SECRET')

        self.client = OAuth2Session(
            client_id=os.getenv('OIDC_CLIENT_ID'), client_secret=os.getenv('OIDC_CLIENT_SECRET')
        )
        # self.client.register(
        #    'oidc',
        #    client_id=os.getenv('OIDC_CLIENT_ID'),
        #    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
        #    server_metadata_url=os.getenv('OIDC_WELL_KNOWN'),
        # )

    def introspect_token(self, access_token) -> dict | None:
        response: Response = self.client.introspect_token(
            os.getenv('OIDC_TOKEN_INTROSPECTION_URL'), token=access_token, token_type_hint='access_token'
        )

        data = response.json()
        print(response.json())

        # Ensure the token is ok
        if data.get('active') is not True:
            return None

        return data
