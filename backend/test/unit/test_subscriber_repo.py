import os
import pytest
from urllib.parse import urlparse
from appointment.database.repo.subscriber import verify_link
from appointment.controller.auth import signed_url_by_subscriber


@pytest.fixture
def clear_url_cache():
    """Clear the get_long_base_sign_url cache and set test FRONTEND_URL"""
    from appointment.defines import get_long_base_sign_url

    get_long_base_sign_url.cache_clear()
    os.environ['FRONTEND_URL'] = 'https://example-long.org'


class TestSubscriber:
    def test_verify_link_uses_long_url(self, with_db, make_basic_subscriber, clear_url_cache):
        """Upon link verification, we should make sure that we are always comparing
        long (FRONTEND_USER/user) type urls since we are always signing with the long url."""

        os.environ['SHORT_BASE_URL'] = 'https://example.org'

        subscriber = make_basic_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)

            assert 'https://example-long.org' not in signed_url
            assert '/user' not in signed_url

            verified_subscriber = verify_link(db, signed_url)

            assert verified_subscriber is not False
            assert verified_subscriber.id == subscriber.id

    def test_verify_link_uses_long_url_when_no_short_url(self, with_db, make_basic_subscriber, clear_url_cache):
        """When SHORT_BASE_URL is not set, the signed URL should contain /user
        because it falls back to the long URL format."""

        # Don't set SHORT_BASE_URL
        os.environ.pop('SHORT_BASE_URL', None)

        subscriber = make_basic_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)

            # When SHORT_BASE_URL is not set, the signed_url should contain the long URL format
            assert urlparse(signed_url).hostname == 'example-long.org'
            assert '/user' in signed_url

            verified_subscriber = verify_link(db, signed_url)

            assert verified_subscriber is not False
            assert verified_subscriber.id == subscriber.id
