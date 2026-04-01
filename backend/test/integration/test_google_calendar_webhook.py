"""Integration tests for the Google Calendar webhook endpoint and watch channel lifecycle."""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from appointment.controller.apis.google_client import GoogleClient
from appointment.database import models, repo, schemas
from appointment.dependencies import google as google_dep
from appointment.routes.webhooks import _handle_subscriber_rsvp, _handle_bookee_rsvp, _handle_event_cancelled

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

    def test_state_mismatch_is_rejected(
        self, with_db, with_client, make_pro_subscriber, make_google_calendar, make_external_connections
    ):
        """A notification with a mismatched state token should be silently ignored."""
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
                channel_id='state-channel',
                resource_id='res-state',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
                state='correct-state-token',
                sync_token='some-sync-token',
            )

        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Channel-Id': 'state-channel',
                'X-Goog-Resource-State': 'exists',
                'X-Goog-Channel-Token': 'wrong-state-token',
            },
        )
        assert response.status_code == 200

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_channel_id(db, 'state-channel')
            assert channel is not None
            assert channel.sync_token == 'some-sync-token'

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

        channel_state = 'disconnected-state'
        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='disconnected-cal-channel',
                resource_id='res-disconnected',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
                state=channel_state,
                sync_token='some-sync-token',
            )

        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Channel-Id': 'disconnected-cal-channel',
                'X-Goog-Resource-State': 'exists',
                'X-Goog-Channel-Token': channel_state,
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

        channel_state = 'test-state-token'
        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='valid-channel',
                resource_id='res-valid',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
                state=channel_state,
                sync_token='initial-sync-token',
            )

        response = with_client.post(
            '/webhooks/google-calendar',
            headers={
                'X-Goog-Channel-Id': 'valid-channel',
                'X-Goog-Resource-State': 'exists',
                'X-Goog-Channel-Token': channel_state,
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
                state='remain-state',
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


class TestGoogleCalendarEventRsvp:
    """Tests for subscriber and bookee RSVP handling via the Google Calendar webhook."""

    BOOKEE_EMAIL = 'bookee@example.com'
    GOOGLE_EVENT_ID = 'google-event-123'
    REMOTE_CALENDAR_ID = 'cal@google.com'

    @pytest.fixture
    def rsvp_setup(
        self, with_db,
        make_pro_subscriber, make_google_calendar, make_external_connections,
        make_appointment, make_attendee, make_appointment_slot,
    ):
        """Create an opened appointment with a requested slot, linked to a Google calendar."""
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id, connected=True)
        attendee = make_attendee(email=self.BOOKEE_EMAIL, name='Bookee')
        appointment = make_appointment(
            calendar_id=calendar.id,
            status=models.AppointmentStatus.opened,
            slots=None,
        )
        make_appointment_slot(
            appointment_id=appointment.id,
            attendee_id=attendee.id,
            booking_status=models.BookingStatus.requested,
            booking_tkn='test-token',
        )

        with with_db() as db:
            repo.appointment.update_external_id_by_id(db, appointment.id, self.GOOGLE_EVENT_ID)

        mock_google_client = MagicMock(spec=GoogleClient)
        mock_google_token = MagicMock()

        return mock_google_client, mock_google_token, appointment

    def _reload(self, with_db, appointment_id):
        """Reload appointment and its first slot from a fresh session."""
        with with_db() as db:
            appt = repo.appointment.get(db, appointment_id)
            slot = appt.slots[0]
            return appt, slot

    def test_subscriber_accepts_confirms_booking(self, with_db, rsvp_setup):
        """When the subscriber accepts a tentative event via Google Calendar,
        the appointment should be closed, the slot booked, and the event
        patched with status, summary, location, and description."""
        mock_google_client, mock_token, appointment = rsvp_setup
        mock_google_client.get_event.return_value = {
            'attendees': [
                {'email': 'owner@example.com', 'self': True, 'responseStatus': 'needsAction'},
                {'email': self.BOOKEE_EMAIL, 'responseStatus': 'needsAction'},
            ]
        }

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            _handle_subscriber_rsvp(
                db, appt, slot, 'accepted',
                mock_google_client, mock_token, self.REMOTE_CALENDAR_ID,
            )

        appt, slot = self._reload(with_db, appointment.id)
        assert appt.status == models.AppointmentStatus.closed
        assert slot.booking_status == models.BookingStatus.booked

        mock_google_client.patch_event.assert_called_once()
        call_args = mock_google_client.patch_event.call_args
        assert call_args.args[0] == self.REMOTE_CALENDAR_ID
        assert call_args.args[1] == self.GOOGLE_EVENT_ID
        body = call_args.args[2]
        assert body['status'] == 'confirmed'
        assert 'summary' in body
        assert 'description' in body
        owner_att = next(a for a in body['attendees'] if a.get('self'))
        assert owner_att['responseStatus'] == 'accepted'

    def test_subscriber_accepts_already_closed_is_noop(self, with_db, rsvp_setup):
        """If the appointment is already closed, a subscriber accept should not change anything."""
        mock_google_client, mock_token, appointment = rsvp_setup

        with with_db() as db:
            repo.appointment.update_status(db, appointment.id, models.AppointmentStatus.closed)

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            _handle_subscriber_rsvp(
                db, appt, slot, 'accepted',
                mock_google_client, mock_token, self.REMOTE_CALENDAR_ID,
            )

        _, slot = self._reload(with_db, appointment.id)
        assert slot.booking_status == models.BookingStatus.requested
        mock_google_client.patch_event.assert_not_called()

    def test_bookee_accepts_does_not_confirm(self, with_db, rsvp_setup):
        """When the bookee accepts, the appointment should remain opened and the slot requested."""
        mock_google_client, mock_token, appointment = rsvp_setup

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            _handle_bookee_rsvp(
                db, appt, slot, 'accepted',
                mock_google_client, mock_token, self.REMOTE_CALENDAR_ID,
            )

        appt, slot = self._reload(with_db, appointment.id)
        assert appt.status == models.AppointmentStatus.opened
        assert slot.booking_status == models.BookingStatus.requested
        mock_google_client.patch_event.assert_not_called()

    def test_subscriber_declines_marks_slot_declined(self, with_db, rsvp_setup):
        """When the subscriber declines via Google Calendar, the slot should be
        marked as declined and the event deleted with notifications."""
        mock_google_client, mock_token, appointment = rsvp_setup

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            _handle_subscriber_rsvp(
                db, appt, slot, 'declined',
                mock_google_client, mock_token, self.REMOTE_CALENDAR_ID,
            )

        _, slot = self._reload(with_db, appointment.id)
        assert slot.booking_status == models.BookingStatus.declined

        mock_google_client.delete_event.assert_called_once_with(
            self.REMOTE_CALENDAR_ID, self.GOOGLE_EVENT_ID, mock_token,
            send_updates='all',
        )

    def test_subscriber_declines_already_declined_is_noop(self, with_db, rsvp_setup):
        """If the slot is already declined, a subscriber decline should not call delete again."""
        mock_google_client, mock_token, appointment = rsvp_setup

        with with_db() as db:
            slot_update = models.BookingStatus.declined
            repo.slot.update(db, repo.appointment.get(db, appointment.id).slots[0].id,
                             schemas.SlotUpdate(booking_status=slot_update))

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            _handle_subscriber_rsvp(
                db, appt, slot, 'declined',
                mock_google_client, mock_token, self.REMOTE_CALENDAR_ID,
            )

        mock_google_client.delete_event.assert_not_called()

    def test_bookee_declines_marks_slot_declined(self, with_db, rsvp_setup):
        """When the bookee declines, the slot should be marked as declined and the event deleted."""
        mock_google_client, mock_token, appointment = rsvp_setup

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            _handle_bookee_rsvp(
                db, appt, slot, 'declined',
                mock_google_client, mock_token, self.REMOTE_CALENDAR_ID,
            )

        _, slot = self._reload(with_db, appointment.id)
        assert slot.booking_status == models.BookingStatus.declined
        mock_google_client.delete_event.assert_called_once()

    def test_event_cancelled_marks_slot_declined(self, with_db, rsvp_setup):
        """When the subscriber deletes the event from Google Calendar,
        the slot should be marked as cancelled."""
        _, _, appointment = rsvp_setup

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            _handle_event_cancelled(db, appt, slot)

        _, slot = self._reload(with_db, appointment.id)
        assert slot.booking_status == models.BookingStatus.cancelled

    def test_event_cancelled_already_cancelled_is_noop(self, with_db, rsvp_setup):
        """If the slot is already cancelled, a cancelled event should not change anything."""
        _, _, appointment = rsvp_setup

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            repo.slot.update(
                db, appt.slots[0].id,
                schemas.SlotUpdate(booking_status=models.BookingStatus.cancelled),
            )

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            slot = appt.slots[0]
            assert slot.booking_status == models.BookingStatus.cancelled
            _handle_event_cancelled(db, appt, slot)

        _, slot = self._reload(with_db, appointment.id)
        assert slot.booking_status == models.BookingStatus.cancelled
