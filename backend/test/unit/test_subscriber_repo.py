import os

from appointment.database.repo.subscriber import verify_link
from appointment.controller.auth import signed_url_by_subscriber


class TestSubscriber:
    def test_verify_link_uses_long_url(self, with_db, make_basic_subscriber):
        """Upon link verification, we should make sure that we are always comparing
        long (FRONTEND_USER/user) type urls since we are always signing with the long url."""

        os.environ['SHORT_BASE_URL'] = 'https://example.org'
        os.environ['FRONTEND_URL'] = 'https://example-long.org'

        subscriber = make_basic_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)

            assert os.environ['FRONTEND_URL'] not in signed_url
            assert '/user' not in signed_url

            verified_subscriber = verify_link(db, signed_url)

            assert verified_subscriber is not False
            assert verified_subscriber.id == subscriber.id

    def test_verify_link_uses_long_url_when_no_short_url(self, with_db, make_basic_subscriber):
        """When SHORT_BASE_URL is not set, the signed URL should contain /user
        because it falls back to the long URL format."""

        # Don't set SHORT_BASE_URL
        os.environ.pop('SHORT_BASE_URL', None)
        os.environ['FRONTEND_URL'] = 'https://example-long.org'

        subscriber = make_basic_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)

            # When SHORT_BASE_URL is not set, the signed_url should contain the long URL format
            assert os.environ['FRONTEND_URL'] in signed_url
            assert '/user' in signed_url

            verified_subscriber = verify_link(db, signed_url)

            assert verified_subscriber is not False
            assert verified_subscriber.id == subscriber.id
