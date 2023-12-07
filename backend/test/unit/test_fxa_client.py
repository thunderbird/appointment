import os

from backend.src.appointment.controller.apis.fxa_client import FxaClient


class TestFxaClient:
    def test_is_in_allow_list(self):
        os.environ['FXA_ALLOW_LIST'] = ''

        fxa_client = FxaClient(None, None, None)

        test_email = 'test@example.org'

        assert fxa_client.is_in_allow_list(test_email)

        # Domain is in allow list
        os.environ['FXA_ALLOW_LIST'] = '@example.org'
        assert fxa_client.is_in_allow_list(test_email)

        # Email is in allow list
        os.environ['FXA_ALLOW_LIST'] = test_email
        assert fxa_client.is_in_allow_list(test_email)

        # Domain is not in allow list
        os.environ['FXA_ALLOW_LIST'] = '@example.com'
        assert not fxa_client.is_in_allow_list(test_email)

        # Domain is in allow list
        os.environ['FXA_ALLOW_LIST'] = '@example.com,@example.org'
        assert fxa_client.is_in_allow_list(test_email)

        # Email is not allow list
        os.environ['FXA_ALLOW_LIST'] = '@example.com,not-test@example.org'
        assert not fxa_client.is_in_allow_list(test_email)

        # Email is not allow list
        os.environ['FXA_ALLOW_LIST'] = '@example.com,not-test@example.org'
        assert not fxa_client.is_in_allow_list('hello@example.com@bad.org')

