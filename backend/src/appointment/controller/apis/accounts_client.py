import logging
import os

import requests


class AccountsClient:
    subscriber_id: int | None = None

    def __init__(self, client_id, client_secret, callback_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.subscriber_id = None
        self.token = None

        self.accounts_url = os.getenv('TB_ACCOUNTS_HOST')

    def setup(self, subscriber_id=None, token=None):
        self.subscriber_id = subscriber_id
        self.token = token

    def is_in_allow_list(self, db, email: str):
        """FIXME: Not Impl"""
        return True

    def get_redirect_url(self, state):
        try:
            response = requests.post(
                url=f'{self.accounts_url}/api/v1/auth/get-login/',
                json={
                    'secret': self.client_secret,
                    'state': state
                },
                headers={
                    'Accept': 'application/json',
                }
            )

            response.raise_for_status()

            login_url_response = response.json()
            return login_url_response.get('login'), login_url_response.get('state')
        except requests.HTTPError as e:
            logging.error(
                f'Could not retrieve redirect url, error occurred: {e.response.status_code} - {e.response.text}'
            )
            raise e

    def get_credentials(self, token: str):
        """Retrieve the user's profile information"""
        try:
            response = requests.post(
                url=f'{self.accounts_url}/api/v1/token/refresh/',
                json={
                    'refresh': token
                },
                headers={
                    'Accept': 'application/json',
                }
            )

            response.raise_for_status()

            access_token_response = response.json()
            return access_token_response.get('access')
        except requests.HTTPError as e:
            logging.error(
                f'Could not retrieve credentials, error occurred: {e.response.status_code} - {e.response.text}'
            )
            raise e

    def get_profile(self, token):
        """Retrieve the user's profile information"""
        try:
            response = requests.post(
                url=f'{self.accounts_url}/api/v1/auth/get-profile/',
                headers={
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )

            response.raise_for_status()

            profile_response = response.json()
            print(">", profile_response)
            return profile_response
        except requests.HTTPError as e:
            # Not great, but we can still continue along..
            logging.error(
                f'Could not retrieve profile, error occurred: {e.response.status_code} - {e.response.text}'
            )
            raise e

    def logout(self):
        """Invalidate the current refresh token"""
        try:
            response = requests.post(
                url=f'{self.accounts_url}/api/v1/auth/logout/',
                headers={
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
            )

            response.raise_for_status()

            logout_response = response.json()
            return logout_response.get('success')
        except requests.HTTPError as e:
            # Not great, but we can still continue along..
            logging.error(
                f'Could not log out the user, error occurred: {e.response.status_code} - {e.response.text}'
            )
            raise e
