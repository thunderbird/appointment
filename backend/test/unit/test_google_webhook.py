"""Unit tests for the Google Calendar webhook processing logic."""

import json
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from appointment.controller.google_watch import setup_watch_channel, teardown_watch_channel
from appointment.database import models, repo
from appointment.routes.webhooks import (
    _find_appointment_by_external_id,
    _handle_bookee_rsvp,
    _handle_subscriber_rsvp,
)


class TestFindAppointmentByExternalId:
    def test_finds_matching_appointment(self, with_db, make_google_calendar, make_appointment):
        calendar = make_google_calendar(connected=True)
        appointment = make_appointment(calendar_id=calendar.id, slots=None)

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment.id)
            db_appointment.external_id = 'google-event-123'
            db.commit()

            result = _find_appointment_by_external_id(db, calendar.id, 'google-event-123')
            assert result is not None
            assert result.id == appointment.id

    def test_returns_none_for_no_match(self, with_db, make_google_calendar, make_appointment):
        calendar = make_google_calendar(connected=True)
        make_appointment(calendar_id=calendar.id, slots=None)

        with with_db() as db:
            result = _find_appointment_by_external_id(db, calendar.id, 'nonexistent-event')
            assert result is None

    def test_scoped_to_calendar(self, with_db, make_google_calendar, make_appointment, make_pro_subscriber):
        """Appointments on other calendars should not be found."""
        sub = make_pro_subscriber()
        cal1 = make_google_calendar(subscriber_id=sub.id, connected=True)
        cal2 = make_google_calendar(subscriber_id=sub.id, connected=True)
        appt = make_appointment(calendar_id=cal1.id, slots=None)

        with with_db() as db:
            db_appt = repo.appointment.get(db, appt.id)
            db_appt.external_id = 'event-on-cal1'
            db.commit()

            assert _find_appointment_by_external_id(db, cal1.id, 'event-on-cal1') is not None
            assert _find_appointment_by_external_id(db, cal2.id, 'event-on-cal1') is None


class TestHandleBookeeRsvp:
    def _make_test_objects(self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot):
        calendar = make_google_calendar(connected=True)
        attendee = make_attendee(email='bookee@example.com', name='Bookee')
        appointment = make_appointment(
            calendar_id=calendar.id,
            status=models.AppointmentStatus.opened,
            slots=None,
        )
        make_appointment_slot(
            appointment_id=appointment.id,
            booking_status=models.BookingStatus.requested,
            attendee_id=attendee.id,
        )

        with with_db() as db:
            db_appt = repo.appointment.get(db, appointment.id)
            db_appt.external_id = 'google-event-456'
            db.commit()

            # Retrieve slot ID from DB to avoid detached instance issues
            slot_id = db_appt.slots[0].id if db_appt.slots else None

        return calendar, appointment.id, slot_id, attendee

    def test_decline_marks_slot_declined(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
    ):
        calendar, appointment_id, slot_id, attendee = self._make_test_objects(
            with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
        )

        mock_client = Mock()
        mock_client.delete_event = Mock()
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment_id)
            db_slot = repo.slot.get(db, slot_id)

            _handle_bookee_rsvp(
                db, db_appointment, db_slot, 'declined', mock_client, mock_token, calendar.user
            )

            db.refresh(db_slot)
            assert db_slot.booking_status == models.BookingStatus.declined
            mock_client.delete_event.assert_called_once()

    def test_accept_does_not_auto_book(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
    ):
        """Bookee accepting the tentative invite should not auto-book;
        the subscriber must still confirm via the branded email or app UI."""
        calendar, appointment_id, slot_id, attendee = self._make_test_objects(
            with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
        )

        mock_client = Mock()
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment_id)
            db_slot = repo.slot.get(db, slot_id)

            _handle_bookee_rsvp(
                db, db_appointment, db_slot, 'accepted', mock_client, mock_token, calendar.user
            )

            db.refresh(db_slot)
            assert db_slot.booking_status == models.BookingStatus.requested

            db.refresh(db_appointment)
            assert db_appointment.status == models.AppointmentStatus.opened

    def test_accept_noop_for_already_booked(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
    ):
        calendar = make_google_calendar(connected=True)
        attendee = make_attendee(email='bookee@example.com')
        appointment = make_appointment(
            calendar_id=calendar.id,
            status=models.AppointmentStatus.closed,
            slots=None,
        )
        make_appointment_slot(
            appointment_id=appointment.id,
            booking_status=models.BookingStatus.booked,
            attendee_id=attendee.id,
        )

        mock_client = Mock()
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment.id)
            db_slot = db_appointment.slots[0]

            _handle_bookee_rsvp(
                db, db_appointment, db_slot, 'accepted', mock_client, mock_token, calendar.user
            )

            db.refresh(db_slot)
            assert db_slot.booking_status == models.BookingStatus.booked
            mock_client.insert_event.assert_not_called()

    def test_needsaction_is_ignored(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
    ):
        calendar, appointment_id, slot_id, attendee = self._make_test_objects(
            with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
        )

        mock_client = Mock()
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment_id)
            db_slot = repo.slot.get(db, slot_id)

            _handle_bookee_rsvp(
                db, db_appointment, db_slot, 'needsAction', mock_client, mock_token, calendar.user
            )

            db.refresh(db_slot)
            assert db_slot.booking_status == models.BookingStatus.requested


class TestHandleSubscriberRsvp:
    """Tests for _handle_subscriber_rsvp, focused on meeting-link and event-update behaviour."""

    def _make_test_objects(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
        meeting_link_provider=models.MeetingLinkProviderType.none,
        location_url='https://meet.example.com',
    ):
        calendar = make_google_calendar(connected=True)
        attendee = make_attendee(email='bookee@example.com', name='Bookee')
        appointment = make_appointment(
            calendar_id=calendar.id,
            status=models.AppointmentStatus.opened,
            location_url=location_url,
            meeting_link_provider=meeting_link_provider,
            slots=None,
        )
        make_appointment_slot(
            appointment_id=appointment.id,
            booking_status=models.BookingStatus.requested,
            attendee_id=attendee.id,
        )

        with with_db() as db:
            db_appt = repo.appointment.get(db, appointment.id)
            db_appt.external_id = 'google-event-789'
            db.commit()
            slot_id = db_appt.slots[0].id

        return calendar, appointment.id, slot_id

    def test_accept_patches_event_with_location_and_title(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
    ):
        """Accepting via Google should patch the event with summary, location, and description."""
        calendar, appointment_id, slot_id = self._make_test_objects(
            with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
        )

        mock_client = Mock()
        mock_client.get_event.return_value = {
            'attendees': [
                {'email': 'owner@example.com', 'self': True, 'responseStatus': 'needsAction'},
                {'email': 'bookee@example.com', 'responseStatus': 'needsAction'},
            ]
        }
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment_id)
            db_slot = repo.slot.get(db, slot_id)

            _handle_subscriber_rsvp(
                db, db_appointment, db_slot, 'accepted',
                mock_client, mock_token, calendar.user,
            )

        mock_client.patch_event.assert_called_once()
        patch_body = mock_client.patch_event.call_args.args[2]
        assert patch_body['status'] == 'confirmed'
        assert 'summary' in patch_body
        assert patch_body.get('location') == 'https://meet.example.com'

        desc_lines = patch_body.get('description', '').split('\n')
        assert any(line.endswith('https://meet.example.com') for line in desc_lines)

    @patch('appointment.controller.zoom.create_meeting_link')
    def test_accept_creates_zoom_link_when_configured(
        self, mock_create_zoom,
        with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
    ):
        """When meeting_link_provider is zoom, a Zoom link should be created and used as location."""
        mock_create_zoom.return_value = 'https://zoom.us/j/123456'

        calendar, appointment_id, slot_id = self._make_test_objects(
            with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
            meeting_link_provider=models.MeetingLinkProviderType.zoom,
        )

        mock_client = Mock()
        mock_client.get_event.return_value = {'attendees': []}
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment_id)
            db_slot = repo.slot.get(db, slot_id)

            _handle_subscriber_rsvp(
                db, db_appointment, db_slot, 'accepted',
                mock_client, mock_token, calendar.user,
            )

        mock_create_zoom.assert_called_once()
        patch_body = mock_client.patch_event.call_args.args[2]
        assert patch_body.get('location') == 'https://zoom.us/j/123456'

    def test_accept_sets_organizer_response_to_accepted(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
    ):
        """The organizer (self) attendee responseStatus should be set to accepted."""
        calendar, appointment_id, slot_id = self._make_test_objects(
            with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
        )

        mock_client = Mock()
        mock_client.get_event.return_value = {
            'attendees': [
                {'email': 'owner@example.com', 'self': True, 'responseStatus': 'needsAction'},
                {'email': 'bookee@example.com', 'responseStatus': 'needsAction'},
            ]
        }
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment_id)
            db_slot = repo.slot.get(db, slot_id)

            _handle_subscriber_rsvp(
                db, db_appointment, db_slot, 'accepted',
                mock_client, mock_token, calendar.user,
            )

        patch_body = mock_client.patch_event.call_args.args[2]
        owner_att = next(a for a in patch_body['attendees'] if a.get('self'))
        assert owner_att['responseStatus'] == 'accepted'

    def test_accept_noop_when_already_closed(
        self, with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot
    ):
        """If the appointment is already closed, accepting again should be a no-op."""
        calendar = make_google_calendar(connected=True)
        attendee = make_attendee(email='bookee@example.com', name='Bookee')
        appointment = make_appointment(
            calendar_id=calendar.id,
            status=models.AppointmentStatus.closed,
            slots=None,
        )
        make_appointment_slot(
            appointment_id=appointment.id,
            booking_status=models.BookingStatus.booked,
            attendee_id=attendee.id,
        )

        with with_db() as db:
            db_appt = repo.appointment.get(db, appointment.id)
            db_appt.external_id = 'already-confirmed-event'
            db.commit()

        mock_client = Mock()
        mock_token = Mock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment.id)
            db_slot = db_appointment.slots[0]

            _handle_subscriber_rsvp(
                db, db_appointment, db_slot, 'accepted',
                mock_client, mock_token, calendar.user,
            )

        mock_client.patch_event.assert_not_called()


class TestGoogleCalendarChannelRepo:
    def test_create_and_get_by_channel_id(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='test-channel-abc',
                resource_id='test-resource-xyz',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )
            assert channel.id is not None

            found = repo.google_calendar_channel.get_by_channel_id(db, 'test-channel-abc')
            assert found is not None
            assert found.id == channel.id

    def test_get_by_calendar_id(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='channel-for-cal',
                resource_id='resource-for-cal',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )

            found = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert found is not None
            assert found.channel_id == 'channel-for-cal'

    def test_update_sync_token(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='ch-sync-test',
                resource_id='res-sync-test',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )
            assert channel.sync_token is None

            updated = repo.google_calendar_channel.update_sync_token(db, channel, 'new-sync-token-123')
            assert updated.sync_token == 'new-sync-token-123'

    def test_get_expiring(self, with_db, make_google_calendar, make_pro_subscriber):
        sub = make_pro_subscriber()
        cal1 = make_google_calendar(subscriber_id=sub.id, connected=True)
        cal2 = make_google_calendar(subscriber_id=sub.id, connected=True)

        now = datetime.now(tz=timezone.utc)
        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=cal1.id,
                channel_id='expiring-soon',
                resource_id='res-1',
                expiration=now + timedelta(hours=12),
            )
            repo.google_calendar_channel.create(
                db,
                calendar_id=cal2.id,
                channel_id='not-expiring',
                resource_id='res-2',
                expiration=now + timedelta(days=5),
            )

            threshold = now + timedelta(hours=24)
            expiring = repo.google_calendar_channel.get_expiring(db, before=threshold)
            assert len(expiring) == 1
            assert expiring[0].channel_id == 'expiring-soon'

    def test_delete(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='to-delete',
                resource_id='res-del',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )

            repo.google_calendar_channel.delete(db, channel)

            assert repo.google_calendar_channel.get_by_channel_id(db, 'to-delete') is None

    def test_cascade_delete_with_calendar(self, with_db, make_google_calendar):
        """Channel should be deleted when its calendar is deleted."""
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='cascade-test',
                resource_id='res-cascade',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )

            repo.calendar.delete(db, calendar.id)

            assert repo.google_calendar_channel.get_by_channel_id(db, 'cascade-test') is None


class TestSetupWatchChannel:
    def test_creates_channel_for_google_calendar(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        google_creds = json.dumps({
            'token': 'fake-token',
            'refresh_token': 'fake-refresh',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-secret',
        })
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=google_creds,
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id,
        )

        mock_client = Mock()
        mock_client.SCOPES = ['https://www.googleapis.com/auth/calendar.events']
        mock_client.watch_events.return_value = {
            'id': 'new-channel-id',
            'resourceId': 'new-resource-id',
            'expiration': str(int((datetime.now(tz=timezone.utc) + timedelta(days=7)).timestamp() * 1000)),
        }
        mock_client.get_initial_sync_token.return_value = 'initial-sync-token'

        os.environ['BACKEND_URL'] = 'http://localhost:5000'

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            setup_watch_channel(db, mock_client, db_cal)

            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel is not None
            assert channel.channel_id == 'new-channel-id'
            assert channel.sync_token == 'initial-sync-token'

    def test_noop_if_channel_already_exists(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        google_creds = json.dumps({
            'token': 'fake-token',
            'refresh_token': 'fake-refresh',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-secret',
        })
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=google_creds,
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id,
        )

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='existing-channel',
                resource_id='existing-resource',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )

        mock_client = Mock()

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            setup_watch_channel(db, mock_client, db_cal)

            mock_client.watch_events.assert_not_called()

    def test_noop_for_caldav_calendar(self, with_db, make_caldav_calendar):
        calendar = make_caldav_calendar(connected=True)
        mock_client = Mock()

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            setup_watch_channel(db, mock_client, db_cal)

            mock_client.watch_events.assert_not_called()

    def test_noop_if_no_google_client(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            setup_watch_channel(db, None, db_cal)

            assert repo.google_calendar_channel.get_by_calendar_id(db, calendar.id) is None


class TestTeardownWatchChannel:
    def test_removes_existing_channel(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        google_creds = json.dumps({
            'token': 'fake-token',
            'refresh_token': 'fake-refresh',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-secret',
        })
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=google_creds,
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id,
        )

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='teardown-channel',
                resource_id='teardown-resource',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )

        mock_client = Mock()
        mock_client.SCOPES = ['https://www.googleapis.com/auth/calendar.events']

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            teardown_watch_channel(db, mock_client, db_cal)

            mock_client.stop_channel.assert_called_once()
            assert repo.google_calendar_channel.get_by_calendar_id(db, calendar.id) is None

    def test_noop_if_no_channel(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        mock_client = Mock()

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            teardown_watch_channel(db, mock_client, db_cal)

            mock_client.stop_channel.assert_not_called()

    def test_deletes_record_even_without_google_client(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='orphan-channel',
                resource_id='orphan-resource',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=7),
            )

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            teardown_watch_channel(db, None, db_cal)

            assert repo.google_calendar_channel.get_by_calendar_id(db, calendar.id) is None
