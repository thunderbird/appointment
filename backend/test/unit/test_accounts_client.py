from unittest.mock import MagicMock, patch

import pytest
import requests

from appointment.controller.apis.accounts_client import AccountsClient


class TestAccountsClientWaffleFlags:
    def test_get_waffle_flags_success(self):
        accounts_client = AccountsClient('client_id', 'client_secret', 'callback_url')
        accounts_client.accounts_url = 'https://accounts.example.org'

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'flags': {'new-dashboard': True, 'beta-feature': False}}

        with patch(
            'appointment.controller.apis.accounts_client.requests.get', return_value=mock_response
        ) as mock_get:
            flags = accounts_client.get_waffle_flags('a-keycloak-access-token')

        assert flags == {'flags': {'new-dashboard': True, 'beta-feature': False}}
        mock_get.assert_called_once_with(
            url='https://accounts.example.org/api/v1/auth/waffle-flags/',
            headers={'Accept': 'application/json', 'Authorization': 'Bearer a-keycloak-access-token'},
        )

    def test_get_waffle_flags_raises_on_http_error(self):
        accounts_client = AccountsClient('client_id', 'client_secret', 'callback_url')
        accounts_client.accounts_url = 'https://accounts.example.org'

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)

        with patch('appointment.controller.apis.accounts_client.requests.get', return_value=mock_response):
            with pytest.raises(requests.HTTPError):
                accounts_client.get_waffle_flags('bad-token')
