from unittest.mock import MagicMock, patch

import pytest

from appointment.dependencies import metrics


@pytest.fixture(autouse=True)
def reset_posthog_client():
    """Each test starts and ends without a cached client."""
    metrics._posthog = None
    yield
    metrics._posthog = None


class TestGetPosthog:
    def test_returns_none_when_not_configured(self, monkeypatch):
        monkeypatch.delenv('POSTHOG_PROJECT_KEY', raising=False)
        monkeypatch.delenv('POSTHOG_HOST', raising=False)

        with patch.object(metrics, 'Posthog') as posthog_class:
            assert metrics.get_posthog() is None

        posthog_class.assert_not_called()

    def test_reuses_a_single_client(self, monkeypatch):
        """Each Posthog client starts a background thread, so we must not create one per call."""
        monkeypatch.setenv('POSTHOG_PROJECT_KEY', 'test-key')
        monkeypatch.setenv('POSTHOG_HOST', 'https://posthog.example.org')

        with patch.object(metrics, 'Posthog', side_effect=lambda *args, **kwargs: MagicMock()) as posthog_class:
            first = metrics.get_posthog()
            second = metrics.get_posthog()
            third = metrics.get_posthog()

        assert first is not None
        assert first is second
        assert second is third
        posthog_class.assert_called_once_with('test-key', host='https://posthog.example.org')

    def test_client_is_disabled_in_test_env(self, monkeypatch):
        monkeypatch.setenv('POSTHOG_PROJECT_KEY', 'test-key')
        monkeypatch.setenv('POSTHOG_HOST', 'https://posthog.example.org')
        monkeypatch.setenv('APP_ENV', 'test')

        with patch.object(metrics, 'Posthog', side_effect=lambda *args, **kwargs: MagicMock()):
            client = metrics.get_posthog()

        assert client.disabled is True
