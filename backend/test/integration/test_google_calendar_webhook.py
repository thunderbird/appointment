"""Integration tests for the Google Calendar webhook endpoint and watch channel lifecycle."""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from appointment.controller.apis.google_client import GoogleClient
from appointment.database import models, repo
from appointment.dependencies import google as google_dep

from defines import auth_headers, TEST_USER_ID


class TestGoogleCalendarWebhook:
    def test_sync_notification_returns_200(self, with_client):
        """Google sends a sync notification when a channel is first created."""
        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Channel-Id': 'some-channel-id',
                'X-Goog-Resource-State': 'sync',
            },
        )
        assert response.status_code == 200

    def test_missing_channel_id_returns_200(self, with_client):
        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Resource-State': 'exists',
            },
        )
        assert response.status_code == 200

    def test_unknown_channel_id_returns_200(self, with_client):
        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Channel-Id': 'unknown-channel-id',
                'X-Goog-Resource-State': 'exists',
            },
        )
        assert response.status_code == 200

    def test_disconnected_calendar_triggers_teardown(
        self, with_db, with_client, make_pro_subscriber, make_google_calendar, make_external_connections
    ):
        """If the calendar is no longer connected, the channel should be cleaned up."""
        subscriber = make_pro_subscriber()
        google_creds = json.dumps({
            'token': 'fake-token',
            'refresh_token': 'fake-refresh',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-secret',
        })
        ext_conn = make_external_connections(
            subscriber.id,
            type=models.ExternalConnectionType.google,
            token=google_creds,
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id,
            connected=False,
            external_connection_id=ext_conn.id,
        )

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='disconnected-cal-channel',
                resource_id='res-disconnected',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
                sync_token='some-sync-token',
            )

        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Channel-Id': 'disconnected-cal-channel',
                'X-Goog-Resource-State': 'exists',
            },
        )
        assert response.status_code == 200

        with with_db() as db:
            assert repo.google_calendar_channel.get_by_channel_id(db, 'disconnected-cal-channel') is None

    def test_valid_notification_returns_200(
        self, with_db, with_client, make_pro_subscriber, make_google_calendar, make_external_connections
    ):
        """A valid notification for a connected calendar should return 200 and update the sync token."""
        mock_google_client = MagicMock(spec=GoogleClient)
        mock_google_client.SCOPES = GoogleClient.SCOPES
        mock_google_client.list_events_sync.return_value = ([], 'new-sync-token')
        with_client.app.dependency_overrides[google_dep.get_google_client] = lambda: mock_google_client

        subscriber = make_pro_subscriber()
        google_creds = json.dumps({
            'token': 'fake-token',
            'refresh_token': 'fake-refresh',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-secret',
        })
        ext_conn = make_external_connections(
            subscriber.id,
            type=models.ExternalConnectionType.google,
            token=google_creds,
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id,
            connected=True,
            external_connection_id=ext_conn.id,
        )

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='valid-channel',
                resource_id='res-valid',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
                sync_token='initial-sync-token',
            )

        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Channel-Id': 'valid-channel',
                'X-Goog-Resource-State': 'exists',
            },
        )
        assert response.status_code == 200

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_channel_id(db, 'valid-channel')
            assert channel is not None
            assert channel.sync_token == 'new-sync-token'


class TestCalendarConnectWatchChannel:
    """Watch channels are managed at the schedule level, not on connect/disconnect.
    These tests verify that connecting/disconnecting a calendar does NOT touch watch channels."""

    def test_connect_google_calendar_does_not_create_channel(
        self, with_db, with_client, make_google_calendar, make_external_connections
    ):
        """Connecting a Google calendar alone should not create a watch channel.
        Channels are created when the calendar is set as default in a schedule."""
        google_creds = json.dumps({
            'token': 'fake-token',
            'refresh_token': 'fake-refresh',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-secret',
        })
        ext_conn = make_external_connections(
            TEST_USER_ID, type=models.ExternalConnectionType.google, token=google_creds,
        )
        calendar = make_google_calendar(
            subscriber_id=TEST_USER_ID, connected=False, external_connection_id=ext_conn.id,
        )

        response = with_client.post(f'/cal/{calendar.id}/connect', headers=auth_headers)
        assert response.status_code == 200, response.text
        assert response.json()['connected'] is True

        with with_db() as db:
            assert repo.google_calendar_channel.get_by_calendar_id(db, calendar.id) is None

    def test_disconnect_google_calendar_does_not_remove_channel(
        self, with_db, with_client, make_google_calendar, make_external_connections
    ):
        """Disconnecting a Google calendar should not tear down its watch channel.
        Channels are managed when the schedule's default calendar changes."""
        google_creds = json.dumps({
            'token': 'fake-token',
            'refresh_token': 'fake-refresh',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-secret',
        })
        ext_conn = make_external_connections(
            TEST_USER_ID, type=models.ExternalConnectionType.google, token=google_creds,
        )
        calendar = make_google_calendar(
            subscriber_id=TEST_USER_ID, connected=True, external_connection_id=ext_conn.id,
        )

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='should-remain',
                resource_id='res-remain',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )

        response = with_client.post(f'/cal/{calendar.id}/disconnect', headers=auth_headers)
        assert response.status_code == 200, response.text
        assert response.json()['connected'] is False

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel is not None
            assert channel.channel_id == 'should-remain'

    def test_connect_caldav_calendar_no_channel(self, with_db, with_client, make_caldav_calendar):
        """Connecting a CalDAV calendar should not create a watch channel."""
        calendar = make_caldav_calendar(connected=False)

        response = with_client.post(f'/cal/{calendar.id}/connect', headers=auth_headers)
        assert response.status_code == 200, response.text

        with with_db() as db:
            assert repo.google_calendar_channel.get_by_calendar_id(db, calendar.id) is None
