import threading
import time
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

    def test_concurrent_first_calls_create_a_single_client(self, monkeypatch):
        """Routes run in a threadpool, so overlapping first requests must not each create a client."""
        monkeypatch.setenv('POSTHOG_PROJECT_KEY', 'test-key')
        monkeypatch.setenv('POSTHOG_HOST', 'https://posthog.example.org')

        thread_count = 8
        start_together = threading.Barrier(thread_count)
        clients = []

        def slow_constructor(*args, **kwargs):
            # Hold the constructor open long enough for every other thread to reach get_posthog()
            time.sleep(0.1)
            return MagicMock()

        def call_get_posthog():
            start_together.wait(timeout=5)
            clients.append(metrics.get_posthog())

        with patch.object(metrics, 'Posthog', side_effect=slow_constructor) as posthog_class:
            threads = [threading.Thread(target=call_get_posthog) for _ in range(thread_count)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=5)

        assert len(clients) == thread_count
        assert clients[0] is not None
        assert all(client is clients[0] for client in clients)
        posthog_class.assert_called_once()

    def test_client_is_disabled_in_test_env(self, monkeypatch):
        monkeypatch.setenv('POSTHOG_PROJECT_KEY', 'test-key')
        monkeypatch.setenv('POSTHOG_HOST', 'https://posthog.example.org')
        monkeypatch.setenv('APP_ENV', 'test')

        with patch.object(metrics, 'Posthog', side_effect=lambda *args, **kwargs: MagicMock()):
            client = metrics.get_posthog()

        assert client.disabled is True
