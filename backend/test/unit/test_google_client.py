from unittest.mock import patch, MagicMock

from appointment.controller.apis.google_client import GoogleClient


class TestGoogleClient:
    """Tests for GoogleClient OAuth flow and PKCE handling"""

    def _make_client(self):
        return GoogleClient('client_id', 'client_secret', 'project_id', 'https://example.com/callback')

    def test_create_flow_returns_fresh_instances(self):
        """Each call to _create_flow should return a distinct Flow object"""
        client = self._make_client()
        flow_a = client._create_flow()
        flow_b = client._create_flow()
        assert flow_a is not flow_b

    def test_setup_validates_credentials_once(self):
        """setup() should attempt to create a Flow to verify creds, then skip on subsequent calls"""
        client = self._make_client()
        assert client._setup_verified is False

        client.setup()
        assert client._setup_verified is True

        with patch.object(client, '_create_flow', wraps=client._create_flow) as spy:
            client.setup()
            spy.assert_not_called()

    def test_get_redirect_url_returns_code_verifier(self):
        """get_redirect_url should return a 3-tuple including a non-None code_verifier"""
        client = self._make_client()
        result = client.get_redirect_url()

        assert len(result) == 3
        url, state, code_verifier = result
        assert url is not None
        assert state is not None
        assert code_verifier is not None
        assert isinstance(code_verifier, str)
        assert len(code_verifier) > 0

    def test_get_redirect_url_generates_unique_verifiers(self):
        """Each call to get_redirect_url should produce a different code_verifier"""
        client = self._make_client()
        _, _, verifier_a = client.get_redirect_url()
        _, _, verifier_b = client.get_redirect_url()
        assert verifier_a != verifier_b

    def test_get_credentials_passes_code_verifier_to_flow(self):
        """get_credentials should set code_verifier on the Flow before calling fetch_token"""
        client = self._make_client()

        mock_flow = MagicMock()
        mock_flow.credentials = MagicMock()

        with patch.object(client, '_create_flow', return_value=mock_flow):
            client.get_credentials('auth_code', code_verifier='test_verifier_123')

        assert mock_flow.code_verifier == 'test_verifier_123'
        mock_flow.fetch_token.assert_called_once_with(code='auth_code')

    def test_get_credentials_works_without_code_verifier(self):
        """get_credentials should still work when code_verifier is None (backwards compat)"""
        client = self._make_client()

        mock_flow = MagicMock()
        mock_flow.credentials = MagicMock()

        with patch.object(client, '_create_flow', return_value=mock_flow):
            client.get_credentials('auth_code')

        assert mock_flow.code_verifier is None
        mock_flow.fetch_token.assert_called_once_with(code='auth_code')

    def test_concurrent_flows_are_isolated(self):
        """Simulates two users starting OAuth flows (their code_verifiers must not interfere)"""
        client = self._make_client()

        _, _, verifier_user_a = client.get_redirect_url()
        _, _, verifier_user_b = client.get_redirect_url()

        assert verifier_user_a != verifier_user_b

        mock_flow = MagicMock()
        mock_flow.credentials = MagicMock()

        with patch.object(client, '_create_flow', return_value=mock_flow):
            client.get_credentials('code_a', code_verifier=verifier_user_a)
            assert mock_flow.code_verifier == verifier_user_a

        mock_flow_b = MagicMock()
        mock_flow_b.credentials = MagicMock()

        with patch.object(client, '_create_flow', return_value=mock_flow_b):
            client.get_credentials('code_b', code_verifier=verifier_user_b)
            assert mock_flow_b.code_verifier == verifier_user_b
