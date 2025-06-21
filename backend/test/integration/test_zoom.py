from unittest import mock
from appointment.database import models
from defines import auth_headers, TEST_USER_ID


class TestZoom:
    def test_zoom_callback_updates_schedule(
        self, monkeypatch, with_db, with_client, make_schedule, make_external_connections
    ):
        # Mock the Zoom API calls
        mock_zoom_client = mock.Mock()
        mock_zoom_client.get_credentials.return_value = '{"access_token": "token", "refresh_token": "refresh"}'
        mock_zoom_client.get_me.return_value = {"id": "zoom_id", "email": "test@test.com"}

        def mock_get_zoom_client(*args, **kwargs):
            return mock_zoom_client

        monkeypatch.setattr('appointment.routes.zoom.get_zoom_client', mock_get_zoom_client)

        schedule = make_schedule(meeting_link_provider=models.MeetingLinkProviderType.none)
        assert schedule.meeting_link_provider == models.MeetingLinkProviderType.none

        # Mock the request.session checks
        with mock.patch('fastapi.Request.session', new_callable=mock.PropertyMock) as mock_session:
            mock_session.return_value = {'zoom_state': 'state', 'zoom_user_id': TEST_USER_ID}
            with_client.get(
                '/zoom/callback', params={'code': 'code', 'state': 'state'}, headers=auth_headers
            )

        # Refresh the schedule now to see the meeting_link_provider change
        with with_db() as db:
            db.add(schedule)
            db.refresh(schedule)

        assert schedule.meeting_link_provider == models.MeetingLinkProviderType.zoom

    def test_zoom_disconnect_without_connection(self, with_client):
        response = with_client.post('/zoom/disconnect', headers=auth_headers)
        assert response.status_code == 200
        assert response.json() is False

    def test_zoom_disconnect_with_connection(self, with_client, make_external_connections):
        make_external_connections(TEST_USER_ID, type=models.ExternalConnectionType.zoom)

        response = with_client.post('/zoom/disconnect', headers=auth_headers)
        assert response.status_code == 200
        assert response.json() is True

    def test_zoom_disconnect_updates_schedule(self, with_db, with_client, make_schedule, make_external_connections):
        make_external_connections(TEST_USER_ID, type=models.ExternalConnectionType.zoom)
        schedule = make_schedule(meeting_link_provider=models.MeetingLinkProviderType.zoom)

        assert schedule.meeting_link_provider == models.MeetingLinkProviderType.zoom

        response = with_client.post('/zoom/disconnect', headers=auth_headers)
        assert response.status_code == 200
        assert response.json() is True

        # Refresh the schedule now that the zoom account is gone,
        # and our meeting link provider should be none
        with with_db() as db:
            db.add(schedule)
            db.refresh(schedule)

        assert schedule.meeting_link_provider == models.MeetingLinkProviderType.none

    def test_zoom_disconnect_does_not_update_schedule_for_other_types(
        self, with_db, with_client, make_schedule, make_external_connections
    ):
        make_external_connections(TEST_USER_ID, type=models.ExternalConnectionType.zoom)
        schedule = make_schedule(meeting_link_provider=models.MeetingLinkProviderType.google_meet)

        assert schedule.meeting_link_provider == models.MeetingLinkProviderType.google_meet

        response = with_client.post('/zoom/disconnect', headers=auth_headers)
        assert response.status_code == 200
        assert response.json() is True

        # Refresh the schedule now that the zoom account is gone,
        # and our meeting link provider should still be google meet
        with with_db() as db:
            db.add(schedule)
            db.refresh(schedule)

        assert schedule.meeting_link_provider == models.MeetingLinkProviderType.google_meet
