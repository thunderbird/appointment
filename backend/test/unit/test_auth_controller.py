import os
from urllib.parse import quote_plus

from appointment.controller.auth import signed_url_by_subscriber, sign_url


class TestSignedUrl:
    def test_signing_uses_long_url(self, make_basic_subscriber):
        """Because our signing process is a little complicated with short urls this test ensures we only ever sign
        with the long url (FRONTEND_USER/user) type urls and never the short urls."""
        os.environ['SHORT_BASE_URL'] = 'https://example.org'

        short_url = os.getenv('SHORT_BASE_URL')
        base_url = f'{os.getenv('FRONTEND_URL')}/user'

        subscriber = make_basic_subscriber()

        # Setup our control url
        url_safe_username = quote_plus(subscriber.username)
        url_to_sign = f'{base_url}/{url_safe_username}/'  # We sign with the long url
        url_to_return = f'{short_url}/{url_safe_username}/'  # We send the user the short url
        url = ''.join([url_to_sign, subscriber.short_link_hash])

        signed_url = signed_url_by_subscriber(subscriber)
        control_signed_url = ''.join([url_to_return, sign_url(url)])

        assert signed_url == control_signed_url
