import os
import pytest

from appointment.database.repo.subscriber import verify_link
from appointment.controller.auth import signed_url_by_subscriber


class TestSubscriber:
    @pytest.fixture
    def mock_long_base_sign_url(self, monkeypatch):
        """Fixture to mock LONG_BASE_SIGN_URL in both subscriber repo and auth controller modules.
        This is needed because the LONG_BASE_SIGN_URL constant is already evaluated
        before the test is run, so we need to mock it."""

        from appointment.database.repo import subscriber as subscriber_repo
        from appointment.controller import auth

        def _mock_url(url):
            monkeypatch.setattr(subscriber_repo, 'LONG_BASE_SIGN_URL', url)
            monkeypatch.setattr(auth, 'LONG_BASE_SIGN_URL', url)

        return _mock_url

    def test_verify_link_uses_long_url(self, with_db, make_basic_subscriber, mock_long_base_sign_url):
        """Upon link verification, we should make sure that we are always comparing
        long (FRONTEND_USER/user) type urls since we are always signing with the long url."""

        os.environ['SHORT_BASE_URL'] = 'https://example.org'
        os.environ['FRONTEND_URL'] = 'https://example-long.org'

        # Mock the LONG_BASE_SIGN_URL
        mock_long_base_sign_url('https://example-long.org/user')

        subscriber = make_basic_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)

            assert os.environ['FRONTEND_URL'] not in signed_url
            assert '/user' not in signed_url

            verified_subscriber = verify_link(db, signed_url)

            assert verified_subscriber is not False
            assert verified_subscriber.id == subscriber.id

    def test_verify_link_uses_long_url_when_no_short_url(self, with_db, make_basic_subscriber, mock_long_base_sign_url):
        """When SHORT_BASE_URL is not set, the signed URL should contain /user
        because it falls back to the long URL format."""

        # Don't set SHORT_BASE_URL
        os.environ.pop('SHORT_BASE_URL', None)
        os.environ['FRONTEND_URL'] = 'https://example-long.org'

        # Mock the LONG_BASE_SIGN_URL
        mock_long_base_sign_url('https://example-long.org/user')

        subscriber = make_basic_subscriber()

        with with_db() as db:
            signed_url = signed_url_by_subscriber(subscriber)

            # When SHORT_BASE_URL is not set, the signed_url should contain the long URL format
            assert os.environ['FRONTEND_URL'] in signed_url
            assert '/user' in signed_url

            verified_subscriber = verify_link(db, signed_url)

            assert verified_subscriber is not False
            assert verified_subscriber.id == subscriber.id
