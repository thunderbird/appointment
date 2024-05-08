import json
import logging
import os
from typing import Dict

from requests_oauthlib import OAuth2Session
import requests
from ...database import models, repo
from ...exceptions.fxa_api import NotInAllowListException, MissingRefreshTokenException


class FxaConfig:
    issuer: str
    authorization_url: str
    metrics_flow_url: str
    token_url: str
    profile_url: str
    destroy_url: str
    jwks_url: str

    @staticmethod
    def from_url(url):
        response: dict = requests.get(url).json()

        # Check our supported scopes
        scopes = response.get('scopes_supported')
        if 'profile' not in scopes:
            logging.warning("Profile scope not found in supported scopes for fxa!")

        config = FxaConfig()
        config.issuer = response.get('issuer')
        config.authorization_url = response.get('authorization_endpoint')
        # Not available from the config endpoint, but it's on the same domain as authorization
        config.metrics_flow_url = response.get('authorization_endpoint').replace('authorization', 'metrics-flow')
        config.token_url = response.get('token_endpoint')
        config.profile_url = response.get('userinfo_endpoint')
        config.destroy_url = response.get('revocation_endpoint')
        config.jwks_url = response.get('jwks_uri')

        return config


class FxaClient:
    ENTRYPOINT = 'tbappointment'

    SCOPES = [
        "profile",
    ]

    config = FxaConfig()

    client: OAuth2Session | None = None
    subscriber_id: int | None = None

    def __init__(self, client_id, client_secret, callback_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.subscriber_id = None
        self.client = None

    def setup(self, subscriber_id=None, token=None):
        """Retrieve the openid connect urls, and setup our client connection"""
        if type(token) is str:
            token = json.loads(token)

        self.config = FxaConfig.from_url(os.getenv('FXA_OPEN_ID_CONFIG'))

        self.subscriber_id = subscriber_id
        self.client = OAuth2Session(self.client_id, redirect_uri=self.callback_url, scope=self.SCOPES,
                                    auto_refresh_url=self.config.token_url,
                                    auto_refresh_kwargs={"client_id": self.client_id, "client_secret": self.client_secret, 'include_client_id': True},
                                    token=token,
                                    token_updater=self.token_saver)

    def is_in_allow_list(self, db, email: str):
        """Check this email against our allow list"""

        # Allow existing subscribers to login even if they're not on an allow-list
        subscriber = repo.subscriber.get_by_email(db, email)
        if subscriber:
            return True

        allow_list = os.getenv('FXA_ALLOW_LIST')
        # If we have no allow list, then we allow everyone
        if not allow_list or allow_list == '':
            return True

        return email.endswith(tuple(allow_list.split(',')))

    def get_redirect_url(self, db, state, email):
        if not self.is_in_allow_list(db, email):
            raise NotInAllowListException()

        utm_campaign = f"{self.ENTRYPOINT}_{os.getenv('APP_ENV')}"
        utm_source = "login"

        try:
            response = self.client.get(url=self.config.metrics_flow_url, params={
                'entrypoint': self.ENTRYPOINT,
                'form_type': 'email',
                'utm_campaign': utm_campaign,
                'utm_source': utm_source
            })

            response.raise_for_status()

            flow_values = response.json()
        except requests.HTTPError as e:
            # Not great, but we can still continue along..
            logging.error(f"Could not initialize metrics flow, error occurred: {e.response.status_code} - {e.response.text}")
            flow_values = {}

        url, state = self.client.authorization_url(
            self.config.authorization_url,
            state=state,
            access_type='offline',
            entrypoint=self.ENTRYPOINT,
            action='email',
            # Flow metrics stuff
            email=email,
            flow_begin_time=flow_values.get('flowBeginTime'),
            flow_id=flow_values.get('flowId'),
            utm_source=utm_source,
            utm_campaign=utm_campaign
        )

        return url, state

    def get_credentials(self, code: str):
        return self.client.fetch_token(self.config.token_url, code, client_secret=self.client_secret, include_client_id=True)

    def token_saver(self, token):
        """requests-oauth automagically calls this function when it has a new refresh token for us.
        This makes it a bit awkward but we make it work..."""
        from appointment.dependencies.database import get_db

        self.client.token = token

        # Need a subscriber attached to this request in order to save a token
        if self.subscriber_id is None:
            return

        repo.external_connection.update_token(next(get_db()), json.dumps(token), self.subscriber_id, models.ExternalConnectionType.fxa)

    def get_profile(self):
        """Retrieve the user's profile information"""
        return self.client.get(url=self.config.profile_url).json()

    def logout(self):
        """Invalidate the current refresh token"""
        # I assume a refresh token will destroy its access tokens
        refresh_token = self.client.token.get('refresh_token')

        if refresh_token is None:
            raise MissingRefreshTokenException()

        # This route doesn't want auth! (Because we're destroying it)
        resp = requests.post(self.config.destroy_url, json={
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })

        resp.raise_for_status()
        return resp

    def get_jwk(self) -> Dict:
        """Retrieve the keys object on the jwks url"""
        response = requests.get(self.config.jwks_url).json()
        return response.get('keys', [])
