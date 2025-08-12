from defines import auth_headers


class TestMiddleware:
    """Test middleware functionality"""

    def test_cache_control_middleware_health_route(self, with_client):
        """Test that health route (no tags) does not have cache-control header"""
        response = with_client.get('/')
        assert response.status_code == 200
        assert 'Cache-Control' not in response.headers

    def test_cache_control_middleware_no_cache_routes(self, with_client):
        """Test that routes tagged with 'no-cache' have cache-control header"""
        # Test /me/appointments route (tagged with no-cache)
        response = with_client.get('/me/appointments', headers=auth_headers)
        assert response.status_code == 200
        assert response.headers.get('Cache-Control') == 'no-store'

    def test_cache_control_middleware_public_availability(self, with_client):
        """Test that public availability route has cache-control header"""
        # This route requires authentication but is tagged with no-cache
        response = with_client.post('/schedule/public/availability', headers=auth_headers)
        assert 'Cache-Control' in response.headers
        assert response.headers.get('Cache-Control') == 'no-store'

    def test_cache_control_middleware_random_post_route(self, with_client):
        """Test that a random POST route without no-cache tag doesn't have cache-control header"""
        # Test a route that doesn't have no-cache tag
        response = with_client.post('/support', json={'topic': 'test', 'details': 'test'}, headers=auth_headers)
        assert response.status_code == 200
        assert 'Cache-Control' not in response.headers

    def test_cache_control_middleware_external_connections(self, with_client):
        """Test that external connections route (tagged with no-cache) has cache-control header"""
        response = with_client.get('/account/external-connections', headers=auth_headers)
        assert response.status_code == 200
        assert response.headers.get('Cache-Control') == 'no-store'

    def test_cache_control_middleware_remote_calendar(self, with_client):
        """Test that remote calendar route (tagged with no-cache) has cache-control header"""
        response = with_client.get('/rmt/cal/1/2024-01-01/2024-01-02', headers=auth_headers)
        assert 'Cache-Control' in response.headers
        assert response.headers.get('Cache-Control') == 'no-store'

    def test_cache_control_middleware_404_route(self, with_client):
        """Test that 404 routes (no tags) do not have cache-control header"""
        response = with_client.get('/nonexistent-route')
        assert response.status_code == 404
        assert 'Cache-Control' not in response.headers

    def test_cache_control_middleware_unauthorized_route(self, with_client):
        """Test that unauthorized routes still get cache-control headers if they have no-cache tag"""
        # Test a no-cache route without auth headers
        response = with_client.get('/me/appointments')
        assert response.status_code == 401
        # Even though it's unauthorized, the middleware should still add the header
        assert response.headers.get('Cache-Control') == 'no-store'
