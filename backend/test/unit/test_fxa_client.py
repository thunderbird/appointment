import os

from appointment.controller.apis.fxa_client import FxaClient


class TestFxaClient:
    def test_is_in_allow_list(self, with_db):
        with with_db() as db:
            os.environ['FXA_ALLOW_LIST'] = ''

            fxa_client = FxaClient(None, None, None)

            test_email = 'cooltestguy@example.org'

            assert fxa_client.is_in_allow_list(db, test_email)

            # Domain is in allow list
            os.environ['FXA_ALLOW_LIST'] = '@example.org'
            assert fxa_client.is_in_allow_list(db, test_email)

            # Email is in allow list
            os.environ['FXA_ALLOW_LIST'] = test_email
            assert fxa_client.is_in_allow_list(db, test_email)

            # Domain is not in allow list
            os.environ['FXA_ALLOW_LIST'] = '@example.com'
            assert not fxa_client.is_in_allow_list(db, test_email)

            # Domain is in allow list
            os.environ['FXA_ALLOW_LIST'] = '@example.com,@example.org'
            assert fxa_client.is_in_allow_list(db, test_email)

            # Email is not allow list
            os.environ['FXA_ALLOW_LIST'] = '@example.com,not-test@example.org'
            assert not fxa_client.is_in_allow_list(db, test_email)

            # Email is not allow list
            os.environ['FXA_ALLOW_LIST'] = '@example.com,not-test@example.org'
            assert not fxa_client.is_in_allow_list(db, 'hello@example.com@bad.org')

    def test_allow_list_allows_subscriber(self, with_db, make_basic_subscriber):
        with with_db() as db:
            os.environ['FXA_ALLOW_LIST'] = '@abadexample.org'

            fxa_client = FxaClient(None, None, None)

            test_email = 'new-test@example.org'

            # They're not a user, and they're not in the allow list
            assert not fxa_client.is_in_allow_list(db, test_email)

            make_basic_subscriber(email=test_email)

            # They're not in the allow list, but they are a user!
            assert fxa_client.is_in_allow_list(db, test_email)



