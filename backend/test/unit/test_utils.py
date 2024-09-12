import pytest
from appointment.utils import retrieve_user_url_data


class TestRetrieveUserUrlData:
    def test_success(self):
        original_username = 'mycoolusername'
        original_signature = 'hello-world'
        original_clean_url = f'https://appointment.local/user/{original_username}'
        url = f'{original_clean_url}/{original_signature}/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature == signature
        assert original_clean_url == clean_url

    def test_success_with_extra_slashes(self):
        original_username = 'mycoolusername'
        original_signature = 'hello-world'
        original_clean_url = f'https://appointment.local/user/{original_username}'
        url = f'{original_clean_url}/{original_signature}////////////////////////'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature == signature
        assert original_clean_url == clean_url

    def test_success_with_uriencoded_signature(self):
        original_username = 'mycoolusername'
        original_signature = 'hello%20world'
        original_clean_url = f'https://appointment.local/user/{original_username}'
        url = f'{original_clean_url}/{original_signature}/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature != signature
        assert 'hello world' == signature
        assert original_clean_url == clean_url

    def test_failure(self):
        original_username = 'mycoolusername'
        original_signature = 'hello world'
        original_clean_url = f'https://appointment.local/user/{original_username}'
        url = f'{original_clean_url}/{original_signature}/other-junk/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username != username
        assert original_signature != signature
        assert original_clean_url != clean_url
