import json
import os
import time

import sentry_sdk
from requests_oauthlib import OAuth2Session
from ...database import models, repo


class ZoomClient:
    OAUTH_AUTHORIZATION_URL = 'https://zoom.us/oauth/authorize'
    OAUTH_DEVICE_AUTHORIZATION_URL = 'https://zoom.us/oauth/devicecode'
    OAUTH_TOKEN_URL = 'https://zoom.us/oauth/token'
    OAUTH_DEVICE_VERIFY_URL = 'https://zoom.us/oauth_device'
    OAUTH_REQUEST_URL = 'https://api.zoom.us/v2'

    SCOPES = ['user:read', 'user_info:read', 'meeting:write']
    NEW_SCOPES = [
        'meeting:read:meeting',
        'meeting:write:meeting',
        'meeting:update:meeting',
        'meeting:delete:meeting',
        'meeting:write:invite_links',
        'user:read:email',
        'user:read:user',
    ]

    client: OAuth2Session | None = None
    subscriber_id: int | None = None

    def __init__(self, client_id, client_secret, callback_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.subscriber_id = None
        self.client = None
        self.use_new_scopes = os.getenv('ZOOM_API_NEW_APP', False) == 'True'

    @property
    def scopes(self):
        """Returns the appropriate scopes"""
        if self.use_new_scopes:
            return self.NEW_SCOPES
        return self.SCOPES

    def check_expiry(self, token: dict | None):
        """Checks expires_at and if expired sets expires_in to a negative number to trigger refresh"""
        if not token:
            return token

        expires_at = token.get('expires_at')
        if expires_at and expires_at <= time.time():
            token['expires_in'] = -100
        elif not expires_at:
            # We shouldn't have to handle this but just in case alert us!
            sentry_sdk.capture_message("Expires at is missing!")
        
        return token

    def setup(self, subscriber_id=None, token=None):
        """Setup our oAuth session"""
        if isinstance(token, str):
            token = json.loads(token)

        token = self.check_expiry(token)

        self.subscriber_id = subscriber_id
        self.client = OAuth2Session(
            self.client_id,
            redirect_uri=self.callback_url,
            scope=self.scopes,
            auto_refresh_url=self.OAUTH_TOKEN_URL,
            auto_refresh_kwargs={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'include_client_id': True,
            },
            token=token,
            token_updater=self.token_saver,
        )

        pass

    def get_redirect_url(self, state):
        url, state = self.client.authorization_url(self.OAUTH_AUTHORIZATION_URL, state=state)

        return url, state

    def get_credentials(self, code: str):
        return self.client.fetch_token(
            self.OAUTH_TOKEN_URL, code, client_secret=self.client_secret, include_client_id=True
        )

    def token_saver(self, token):
        """requests-oauth automagically calls this function when it has a new refresh token for us.
        This makes it a bit awkward but we make it work..."""
        from appointment.dependencies.database import get_db

        self.client.token = token

        # Need a subscriber attached to this request in order to save a token
        if self.subscriber_id is None:
            return

        # get_db is a generator function, retrieve the only yield
        repo.external_connection.update_token(
            next(get_db()), json.dumps(token), self.subscriber_id, models.ExternalConnectionType.zoom
        )

    def get_me(self):
        return self.client.get(f'{self.OAUTH_REQUEST_URL}/users/me').json()

    def create_meeting(self, title, start_time, duration, timezone=None):
        # https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingCreate

        response = self.client.post(
            f'{self.OAUTH_REQUEST_URL}/users/me/meetings',
            json={
                'type': 2,  # Scheduled Meeting
                'default_password': True,
                'duration': duration,
                'start_time': f'{start_time}Z',  # Make it UTC
                'topic': title[:200],  # Max 200 chars
                'settings': {
                    'private_meeting': True,
                    'registrants_confirmation_email': False,
                    'registrants_email_notification': False,
                },
            },
        )

        response.raise_for_status()

        return response.json()

    def get_meeting(self, meeting_id):
        response = self.client.get(f'{self.OAUTH_REQUEST_URL}/meetings/{meeting_id}')
        response.raise_for_status()
        return response.json()
