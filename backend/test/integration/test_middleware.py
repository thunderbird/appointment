from defines import auth_headers


class TestMiddleware:
    """Test middleware functionality"""

    def test_cache_control_middleware_health_route(self, with_client):
        """Test that health route (no tags) does not have cache-control header"""
        response = with_client.get('/')
        assert response.status_code == 200
        assert 'cache-control' not in response.headers

    def test_cache_control_middleware_random_post_route(self, with_client):
        """Test that a random POST route without no-cache tag doesn't have cache-control header"""
        # Test a route that doesn't have no-cache tag
        response = with_client.post('/support', json={'topic': 'test', 'details': 'test'}, headers=auth_headers)
        assert response.status_code == 200
        assert 'cache-control' not in response.headers

    def test_cache_control_middleware_404_route(self, with_client):
        """Test that 404 routes (no tags) do not have cache-control header"""
        response = with_client.get('/nonexistent-route')
        assert response.status_code == 404
        assert 'cache-control' not in response.headers

    def test_cache_control_middleware_unauthorized_route(self, with_client):
        """Test that unauthorized routes still get cache-control headers if they have no-cache tag"""
        # Test a no-cache route without auth headers
        response = with_client.get('/me/appointments')
        assert response.status_code == 401
        # Even though it's unauthorized, the middleware should still add the header
        assert response.headers.get('cache-control').lower() == 'no-store'


class TestNoCacheTaggedRoutes:
    """Test all routes tagged with 'no-cache' have proper cache-control headers"""

    def test_me_appointments_route(self, with_client):
        """Test /me/appointments route (tagged with no-cache) has cache-control header"""
        response = with_client.get('/me/appointments', headers=auth_headers)
        assert response.status_code == 200
        assert response.headers.get('cache-control').lower() == 'no-store'

    def test_external_connections_route(self, with_client):
        """Test /account/external-connections route (tagged with no-cache) has cache-control header"""
        response = with_client.get('/account/external-connections', headers=auth_headers)
        assert response.status_code == 200
        assert response.headers.get('cache-control').lower() == 'no-store'

    def test_remote_calendar_route(self, with_client):
        """Test /rmt/cal/{id}/{start}/{end} route (tagged with no-cache) has cache-control header"""
        response = with_client.get('/rmt/cal/1/2024-01-01/2024-01-02', headers=auth_headers)
        # This might return 404 or other error depending on test setup, but we care about headers
        assert 'cache-control' in response.headers
        assert response.headers.get('cache-control').lower() == 'no-store'

    def test_public_availability_route(self, with_client):
        """Test /schedule/public/availability route (tagged with no-cache) has cache-control header"""
        response = with_client.post('/schedule/public/availability', headers=auth_headers)
        # This might return 404 or other error depending on test setup, but we care about headers
        assert 'cache-control' in response.headers
        assert response.headers.get('cache-control').lower() == 'no-store'

    def test_public_availability_request_route(self, with_client):
        """Test /schedule/public/availability/request route (tagged with no-cache) has cache-control header"""
        # This route requires a specific payload, but we can test the header
        response = with_client.put('/schedule/public/availability/request', headers=auth_headers)
        # This might return 422 (validation error) or other error, but we care about headers
        assert 'cache-control' in response.headers
        assert response.headers.get('cache-control').lower() == 'no-store'

    def test_public_availability_booking_route(self, with_client):
        """Test /schedule/public/availability/booking route (tagged with no-cache) has cache-control header"""
        # This route requires a specific payload, but we can test the header
        response = with_client.put('/schedule/public/availability/booking', headers=auth_headers)
        # This might return 422 (validation error) or other error, but we care about headers
        assert 'cache-control' in response.headers
        assert response.headers.get('cache-control').lower() == 'no-store'
