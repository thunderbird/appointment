"""Unit tests for handle_schedule_availability_decision Google calendar paths."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, MagicMock, patch

from appointment.database import models, repo, schemas
from appointment.routes.schedule import handle_schedule_availability_decision


class TestHandleScheduleAvailabilityDecisionGoogle:
    """Tests for the Google invite branches in handle_schedule_availability_decision."""

    def _make_google_calendar(self):
        cal = Mock()
        cal.provider = models.CalendarProvider.google
        cal.user = 'cal@google.com'
        return cal

    def _make_schedule(self):
        schedule = Mock()
        schedule.location_url = 'https://meet.example.com'
        schedule.meeting_link_provider = models.MeetingLinkProviderType.none
        schedule.details = 'Test details'
        schedule.name = 'Test Schedule'
        return schedule

    def _make_subscriber(self):
        subscriber = Mock()
        subscriber.name = 'Subscriber'
        subscriber.timezone = 'UTC'
        subscriber.preferred_email = 'sub@example.com'
        subscriber.language = 'en'
        return subscriber

    def _setup(
        self, with_db, make_google_calendar, make_appointment,
        make_attendee, make_appointment_slot, has_external_id=True,
    ):
        calendar = make_google_calendar(connected=True)
        attendee = make_attendee(email='bookee@example.com', name='Bookee')
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

        if has_external_id:
            with with_db() as db:
                repo.appointment.update_external_id_by_id(db, appointment.id, 'google-event-123')

        return calendar, appointment

    @patch('appointment.routes.schedule.get_remote_connection')
    def test_confirm_patches_existing_hold_event(
        self, mock_get_remote_connection,
        with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
    ):
        """When a hold event exists (has external_id), confirm_event should be called."""
        calendar, appointment = self._setup(
            with_db, make_google_calendar, make_appointment,
            make_attendee, make_appointment_slot, has_external_id=True,
        )

        mock_connector = MagicMock()
        mock_get_remote_connection.return_value = (mock_connector, 'sub@example.com')

        google_calendar = self._make_google_calendar()
        schedule = self._make_schedule()
        subscriber = self._make_subscriber()
        background_tasks = MagicMock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment.id)
            slot = db_appointment.slots[0]
            db.add(slot)
            db.add(slot.attendee)

            handle_schedule_availability_decision(
                True, google_calendar, schedule, subscriber, slot,
                db, None, None, background_tasks,
            )

            db.refresh(slot)
            assert slot.booking_status == models.BookingStatus.booked

        mock_connector.confirm_event.assert_called_once_with('google-event-123')

    @patch('appointment.routes.schedule.save_remote_event')
    def test_confirm_creates_event_when_no_hold_exists(
        self, mock_save_remote_event,
        with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
    ):
        """When no hold event exists (no external_id), save_remote_event should be called
        with send_google_notification=True and booking_confirmation=False."""
        calendar, appointment = self._setup(
            with_db, make_google_calendar, make_appointment,
            make_attendee, make_appointment_slot, has_external_id=False,
        )

        mock_event = schemas.Event(
            title='Test',
            start=datetime.now(tz=timezone.utc),
            end=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            description='',
            location=schemas.EventLocation(url=None),
            external_id='new-google-event-456',
        )
        mock_save_remote_event.return_value = mock_event

        google_calendar = self._make_google_calendar()
        schedule = self._make_schedule()
        subscriber = self._make_subscriber()
        background_tasks = MagicMock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment.id)
            slot = db_appointment.slots[0]
            db.add(slot)
            db.add(slot.attendee)

            handle_schedule_availability_decision(
                True, google_calendar, schedule, subscriber, slot,
                db, None, None, background_tasks,
            )

            db.refresh(slot)
            assert slot.booking_status == models.BookingStatus.booked

        mock_save_remote_event.assert_called_once()
        call_kwargs = mock_save_remote_event.call_args
        assert call_kwargs.kwargs.get('send_google_notification') is True
        assert call_kwargs.kwargs.get('booking_confirmation') is False

        with with_db() as db:
            appt = repo.appointment.get(db, appointment.id)
            assert appt.external_id == 'new-google-event-456'

    @patch('appointment.routes.schedule.save_remote_event')
    def test_confirm_creates_event_does_not_send_branded_vevent(
        self, mock_save_remote_event,
        with_db, make_google_calendar, make_appointment, make_attendee, make_appointment_slot,
    ):
        """For Google invites, the branded vevent email should NOT be sent
        (Google handles notifications via sendUpdates)."""
        calendar, appointment = self._setup(
            with_db, make_google_calendar, make_appointment,
            make_attendee, make_appointment_slot, has_external_id=False,
        )

        mock_event = schemas.Event(
            title='Test',
            start=datetime.now(tz=timezone.utc),
            end=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            description='',
            location=schemas.EventLocation(url=None),
        )
        mock_save_remote_event.return_value = mock_event

        google_calendar = self._make_google_calendar()
        schedule = self._make_schedule()
        subscriber = self._make_subscriber()
        background_tasks = MagicMock()

        with with_db() as db:
            db_appointment = repo.appointment.get(db, appointment.id)
            slot = db_appointment.slots[0]
            db.add(slot)
            db.add(slot.attendee)

            handle_schedule_availability_decision(
                True, google_calendar, schedule, subscriber, slot,
                db, None, None, background_tasks,
            )

        for call in background_tasks.add_task.call_args_list:
            func = call[0][0] if call[0] else call.kwargs.get('func')
            assert 'send_invitation' not in getattr(func, '__name__', '')
