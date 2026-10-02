import logging
import os
from unittest.mock import patch

import pytest

from appointment.main import _warn_about_local_frontend_url


class TestWarnAboutLocalFrontendUrl:
    @pytest.mark.parametrize(
        'frontend_url',
        ['http://localhost:8090', 'http://127.0.0.1:8090', 'http://[::1]:8090', 'http://0.0.0.0'],
    )
    def test_warns_on_local_url(self, frontend_url, caplog):
        with patch.dict(os.environ, {'APP_ENV': 'dev', 'FRONTEND_URL': frontend_url}):
            with caplog.at_level(logging.WARNING):
                _warn_about_local_frontend_url()

        assert 'only work on this machine' in caplog.text

    def test_warns_when_unset(self, caplog):
        with patch.dict(os.environ, {'APP_ENV': 'dev', 'FRONTEND_URL': ''}):
            with caplog.at_level(logging.WARNING):
                _warn_about_local_frontend_url()

        assert 'FRONTEND_URL is not set' in caplog.text

    def test_silent_on_public_url(self, caplog):
        with patch.dict(os.environ, {'APP_ENV': 'prod', 'FRONTEND_URL': 'https://appointment.example.org'}):
            with caplog.at_level(logging.WARNING):
                _warn_about_local_frontend_url()

        assert caplog.text == ''

    def test_silent_in_test_env(self, caplog):
        with patch.dict(os.environ, {'APP_ENV': 'test', 'FRONTEND_URL': 'http://localhost:8090'}):
            with caplog.at_level(logging.WARNING):
                _warn_about_local_frontend_url()

        assert caplog.text == ''
