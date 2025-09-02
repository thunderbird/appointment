import pytest
import dateutil.parser
from unittest.mock import patch, MagicMock
from datetime import datetime

from defines import DAY1, DAY3, auth_headers, TEST_USER_ID
from appointment.database.repo import appointment as appointment_repo
from appointment.database.models import (
    MeetingLinkProviderType,
    ExternalConnectionType,
    AppointmentStatus,
    Slot,
    BookingStatus,
)


class TestAppointment:
    @staticmethod
    def date_time_to_str(date_time):
        return str(date_time).replace(' ', 'T')

    def test_get_remote_caldav_events(self, with_client, make_appointment, monkeypatch):
        """Test against a fake remote caldav, we're testing the route controller
        not the actual caldav connector here!
        """
        from appointment.controller.calendar import CalDavConnector

        generated_appointment = make_appointment()

        def list_events(self, start, end):
            end = dateutil.parser.parse(end)
            from appointment.database import schemas

            return [
                schemas.Event(
                    title=generated_appointment.title,
                    start=generated_appointment.slots[0].start,
                    end=end,
                    all_day=False,
                    description=generated_appointment.details,
                    calendar_title=generated_appointment.calendar.title,
                    calendar_color=generated_appointment.calendar.color,
                )
            ]

        monkeypatch.setattr(CalDavConnector, 'list_events', list_events)

        path = f'/rmt/cal/{generated_appointment.calendar_id}/' + DAY1 + '/' + DAY3
        response = with_client.get(path, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == generated_appointment.title
        assert data[0]['start'] == generated_appointment.slots[0].start.isoformat()
        assert data[0]['end'] == dateutil.parser.parse(DAY3).isoformat()

    def test_caldav_list_events_with_missing_properties(self, make_appointment, monkeypatch):
        """Test that CalDavConnector.list_events handles events with missing properties gracefully"""
        from appointment.controller.calendar import CalDavConnector

        # Create mock events with various missing properties
        class MockVEvent:
            def __init__(self, has_summary=True, has_dtend=True, has_duration=False):
                self.dtstart = MagicMock()
                self.dtstart.value = datetime(2023, 12, 1, 10, 0, 0)

                if has_summary:
                    self.summary = MagicMock()
                    self.summary.value = "Test Event"

                if has_dtend:
                    self.dtend = MagicMock()
                    self.dtend.value = datetime(2023, 12, 1, 11, 0, 0)
                elif has_duration:
                    self.duration = MagicMock()
                    self.duration.value = "PT1H"  # 1 hour

        class MockVObjectInstance:
            def __init__(self, has_summary=True, has_dtend=True, has_duration=False):
                self.vevent = MockVEvent(has_summary, has_dtend, has_duration)

        class MockEvent:
            def __init__(self, has_summary=True, has_dtend=True, has_duration=False):
                self.icalendar_component = {'status': 'confirmed'}
                self.vobject_instance = MockVObjectInstance(has_summary, has_dtend, has_duration)

            def get_duration(self):
                from datetime import timedelta
                return timedelta(hours=1)

        # Create various test events
        mock_events = [
            MockEvent(has_summary=True, has_dtend=True),     # Normal event
            MockEvent(has_summary=False, has_dtend=True),    # Missing summary
            MockEvent(has_summary=True, has_dtend=False, has_duration=True),  # Has duration instead of dtend
            MockEvent(has_summary=False, has_dtend=False, has_duration=True), # Missing summary and dtend
        ]

        # Add events that should be filtered out by our guards
        class MockBadVEvent:
            """VEvent with missing critical properties"""
            def __init__(self, missing_dtstart=False, missing_both_end_props=False):
                if not missing_dtstart:
                    self.dtstart = MagicMock()
                    self.dtstart.value = datetime(2023, 12, 1, 10, 0, 0)

                if not missing_both_end_props:
                    self.dtend = MagicMock()
                    self.dtend.value = datetime(2023, 12, 1, 11, 0, 0)

        class MockBadVObjectInstance:
            def __init__(self, missing_dtstart=False, missing_both_end_props=False):
                self.vevent = MockBadVEvent(missing_dtstart, missing_both_end_props)

        class MockBadEvent:
            def __init__(self, missing_dtstart=False, missing_both_end_props=False):
                self.icalendar_component = {'status': 'confirmed'}
                self.vobject_instance = MockBadVObjectInstance(missing_dtstart, missing_both_end_props)

            def get_duration(self):
                from datetime import timedelta
                return timedelta(hours=1)

        # Add events that should be filtered out
        mock_events.extend([
            MockBadEvent(missing_dtstart=True),           # Missing dtstart - should be filtered
            MockBadEvent(missing_both_end_props=True),    # Missing both dtend and duration - should be filtered
        ])

        def mock_search(start, end, event=True, expand=True):
            return mock_events

        def mock_calendar(url):
            calendar_mock = MagicMock()
            calendar_mock.search = mock_search
            return calendar_mock

        def mock_client_calendar(url):
            return mock_calendar(url)

        # Set up the CalDavConnector with mocked components
        connector = CalDavConnector(
            db=None,
            subscriber_id=1,
            calendar_id=1,
            redis_instance=None,
            url="https://test.com/caldav",
            user="test",
            password="test"
        )

        # Mock the client.calendar method
        connector.client = MagicMock()
        connector.client.calendar = mock_client_calendar

        # Mock the caching methods
        connector.get_cached_events = MagicMock(return_value=None)
        connector.put_cached_events = MagicMock()

        # Test the method with problematic events
        start_str = "2023-12-01"
        end_str = "2023-12-02"

        # This should not raise any exceptions despite missing properties
        events = connector.list_events(start_str, end_str)

        # Verify the results - should only process 4 valid events, filtering out 2 bad ones
        assert len(events) == 4, "Should process 4 valid events and filter out 2 invalid ones"

        # Check that events with missing summary get default title
        events_with_default_title = [e for e in events if 'event-summary-default' in e.title]
        assert len(events_with_default_title) == 2, "Events without summary should get default title"

        # Check that all events have required fields
        for event in events:
            assert event.title is not None
            assert event.start is not None
            assert event.end is not None
            assert isinstance(event.all_day, bool)
            assert isinstance(event.tentative, bool)

    def test_get_remote_caldav_events_invalid_calendar(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        path = f'/rmt/cal/{generated_appointment.calendar_id + 999}/' + DAY1 + '/' + DAY3
        response = with_client.get(path, headers=auth_headers)
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail']['id'] == 'CALENDAR_NOT_FOUND'

    def test_get_invitation_ics_file(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f'/apmt/serve/ics/{generated_appointment.slug}/{generated_appointment.slots[0].id}')
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['name'] == 'invite'
        assert data['content_type'] == 'text/calendar'
        assert 'data' in data

    def test_get_invitation_ics_file_for_missing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(
            f'/apmt/serve/ics/{generated_appointment.slug}-doesnt-exist/{generated_appointment.slots[0].id}'
        )
        assert response.status_code == 404, response.text

    def test_get_invitation_ics_file_for_missing_slot(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(
            f'/apmt/serve/ics/{generated_appointment.slug}/{generated_appointment.slots[0].id + 1}'
        )
        assert response.status_code == 404, response.text

    @pytest.mark.skip(reason='feature still being scoped')
    def test_modify_my_appointment(self, with_client, make_appointment, with_db):
        """
        Test modifying an appointment's title and slot start time via /apmt/{id}/modify.
        """
        from appointment.database import schemas, models
        from datetime import timedelta

        # Create an appointment with a slot
        appointment = make_appointment()
        slot = appointment.slots[0]
        new_title = 'Updated Appointment Title'
        new_start = slot.start + timedelta(hours=1)
        payload = schemas.AppointmentModifyRequest(
            title=new_title, slot_id=slot.id, start=new_start, notes='Rescheduled by user.'
        ).model_dump(mode='json')

        response = with_client.put(f'/apmt/{appointment.id}/modify', json=payload, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['title'] == new_title

        # Find the modified slot
        modified_slot = next((s for s in data['slots'] if s['id'] == slot.id), None)
        assert modified_slot is not None
        assert modified_slot['start'] == new_start.isoformat()
        assert modified_slot['booking_status'] == models.BookingStatus.modified.value

        # Double-check in DB
        with with_db() as db:
            db_slot = db.get(models.Slot, slot.id)
            assert db_slot.start == new_start
            assert db_slot.booking_status == models.BookingStatus.modified


class TestMyAppointments:
    def test_appointments_default_pagination(self, with_client, make_appointment, make_google_calendar):
        """Test default pagination behavior (no parameters)"""
        appointment_count = 5

        calendar = make_google_calendar(subscriber_id=TEST_USER_ID)
        [make_appointment(calendar_id=calendar.id) for _ in range(appointment_count)]

        response = with_client.get('/me/appointments', headers=auth_headers)

        assert response.status_code == 200, response.text

        data = response.json()

        # Should return paginated response with default values
        assert 'items' in data
        assert 'page_meta' in data
        assert len(data['items']) == appointment_count
        assert data['page_meta']['page'] == 1
        assert data['page_meta']['per_page'] == 50

    def test_dont_show_other_subscribers_appointments(
        self, with_client, make_basic_subscriber, make_appointment, make_google_calendar
    ):
        """Only show my appointments in the /me/appointments route"""
        # The other subscriber / appointment
        other = make_basic_subscriber()
        other_calendar = make_google_calendar(subscriber_id=other.id)
        other_appointment = make_appointment(calendar_id=other_calendar.id)

        # My Appointment
        calendar = make_google_calendar(subscriber_id=TEST_USER_ID)
        appointment = make_appointment(calendar_id=calendar.id)

        response = with_client.get('/me/appointments', headers=auth_headers)

        assert response.status_code == 200, response.text

        data = response.json()

        assert len(data['items']) == 1
        assert other_appointment.id != data['items'][0]['id']
        assert appointment.id == data['items'][0]['id']

    def test_appointments_paginated(self, with_client, make_appointment, make_google_calendar):
        """Test paginated appointments endpoint"""
        appointment_count = 25
        per_page = 10

        calendar = make_google_calendar(subscriber_id=TEST_USER_ID)
        [make_appointment(calendar_id=calendar.id) for _ in range(appointment_count)]

        # Test first page
        response = with_client.get(f'/me/appointments?page=1&per_page={per_page}', headers=auth_headers)

        assert response.status_code == 200, response.text

        data = response.json()

        assert len(data['items']) == per_page
        assert data['page_meta']['page'] == 1
        assert data['page_meta']['per_page'] == per_page
        assert data['page_meta']['count'] == per_page
        assert data['page_meta']['total_pages'] == 3  # 25 appointments / 10 per page = 3 pages

        # Test second page
        response = with_client.get(f'/me/appointments?page=2&per_page={per_page}', headers=auth_headers)

        assert response.status_code == 200, response.text

        data = response.json()

        assert len(data['items']) == per_page
        assert data['page_meta']['page'] == 2

        # Test third page (should have 5 remaining appointments)
        response = with_client.get(f'/me/appointments?page=3&per_page={per_page}', headers=auth_headers)

        assert response.status_code == 200, response.text

        data = response.json()

        assert len(data['items']) == 5  # 25 - (2 * 10) = 5 remaining
        assert data['page_meta']['page'] == 3

    def test_pending_appointments_count(
        self, with_client, make_appointment, make_google_calendar, make_attendee, make_appointment_slot
    ):
        """Test pending appointments count endpoint"""
        calendar = make_google_calendar(subscriber_id=TEST_USER_ID)
        attendee = make_attendee()

        # Create appointments with different booking statuses
        appointment1 = make_appointment(calendar_id=calendar.id)
        appointment2 = make_appointment(calendar_id=calendar.id)
        appointment3 = make_appointment(calendar_id=calendar.id)

        # Create slots with different booking statuses
        slot1 = make_appointment_slot(
            appointment_id=appointment1.id, attendee_id=attendee.id, booking_status=BookingStatus.requested
        )[0]

        slot2 = make_appointment_slot(
            appointment_id=appointment2.id, attendee_id=attendee.id, booking_status=BookingStatus.booked
        )[0]

        slot3 = make_appointment_slot(
            appointment_id=appointment3.id, attendee_id=attendee.id, booking_status=BookingStatus.requested
        )[0]

        # Update appointments to have the slots
        appointment1.slots = [slot1]
        appointment2.slots = [slot2]
        appointment3.slots = [slot3]

        response = with_client.get('/me/appointments_count_by_status?status=requested', headers=auth_headers)

        assert response.status_code == 200, response.text

        data = response.json()

        # Should count only appointments with requested booking status
        assert data['count'] == 2  # appointment1 and appointment3 have requested status

    def test_appointments_with_status_filters(
        self, with_client, make_appointment, make_google_calendar, make_attendee, make_appointment_slot
    ):
        """Test filtering appointments by booking status"""
        calendar = make_google_calendar(subscriber_id=TEST_USER_ID)
        attendee = make_attendee()

        # Create appointments with different booking statuses
        appointment1 = make_appointment(calendar_id=calendar.id)
        appointment2 = make_appointment(calendar_id=calendar.id)
        appointment3 = make_appointment(calendar_id=calendar.id)
        appointment4 = make_appointment(calendar_id=calendar.id)

        # Create slots with different booking statuses
        slot1 = make_appointment_slot(
            appointment_id=appointment1.id, attendee_id=attendee.id, booking_status=BookingStatus.requested
        )[0]

        slot2 = make_appointment_slot(
            appointment_id=appointment2.id, attendee_id=attendee.id, booking_status=BookingStatus.booked
        )[0]

        slot3 = make_appointment_slot(
            appointment_id=appointment3.id, attendee_id=attendee.id, booking_status=BookingStatus.declined
        )[0]

        slot4 = make_appointment_slot(
            appointment_id=appointment4.id, attendee_id=attendee.id, booking_status=BookingStatus.cancelled
        )[0]

        # Update appointments to have the slots
        appointment1.slots = [slot1]
        appointment2.slots = [slot2]
        appointment3.slots = [slot3]
        appointment4.slots = [slot4]

        # Test filtering by single status
        response = with_client.get('/me/appointments?status=requested', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data['items']) == 1
        assert data['items'][0]['id'] == appointment1.id

        # Test filtering by multiple statuses
        response = with_client.get('/me/appointments?status=requested&status=booked', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data['items']) == 2
        appointment_ids = [item['id'] for item in data['items']]
        assert appointment1.id in appointment_ids
        assert appointment2.id in appointment_ids

        # Test filtering by declined and cancelled
        response = with_client.get('/me/appointments?status=declined&status=cancelled', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data['items']) == 2
        appointment_ids = [item['id'] for item in data['items']]
        assert appointment3.id in appointment_ids
        assert appointment4.id in appointment_ids

        # Test with invalid filter (should be ignored)
        response = with_client.get('/me/appointments?status=invalid_status&status=requested', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data['items']) == 1
        assert data['items'][0]['id'] == appointment1.id

        # Test without filters (should return all appointments)
        response = with_client.get('/me/appointments', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data['items']) == 4


class TestCancelAppointment:
    def test_cancel_appointment(self, with_client, make_appointment, with_db):
        appointment = make_appointment()
        payload = {'reason': 'Test cancellation'}

        with patch('appointment.routes.api.Tools') as mock_tools:
            response = with_client.post(f'/apmt/{appointment.id}/cancel', headers=auth_headers, json=payload)

            assert response.status_code == 200
            assert mock_tools().send_cancel_vevent.call_count == len(appointment.slots)

        with with_db() as db:
            appointment = appointment_repo.get(db, appointment.id)
            assert appointment is not None
            assert appointment.slots[0].booking_status == BookingStatus.cancelled

    def test_cancel_appointment_not_found(self, with_client):
        payload = {'reason': 'Test cancellation'}
        response = with_client.post('/apmt/9999/cancel', headers=auth_headers, json=payload)
        assert response.status_code == 404
        assert response.json()['detail']['id'] == 'APPOINTMENT_NOT_FOUND'

    def test_cancel_appointment_not_authorized(
        self, with_client, make_appointment, make_basic_subscriber, make_google_calendar
    ):
        # The other subscriber / appointment
        other = make_basic_subscriber()
        other_calendar = make_google_calendar(subscriber_id=other.id)
        other_appointment = make_appointment(calendar_id=other_calendar.id)

        payload = {'reason': 'Test cancellation'}

        response = with_client.post(f'/apmt/{other_appointment.id}/cancel', headers=auth_headers, json=payload)

        assert response.status_code == 403
        assert response.json()['detail']['id'] == 'APPOINTMENT_NOT_AUTH'

    def test_cancel_appointment_with_zoom_meeting(
        self,
        monkeypatch,
        with_client,
        make_appointment,
        make_external_connections,
        make_google_calendar,
        make_attendee,
        make_appointment_slot,
    ):
        make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.zoom,
        )

        # Patch GoogleConnector to track delete_event calls
        from appointment.controller.calendar import GoogleConnector

        mock_delete_event = MagicMock()
        monkeypatch.setattr(GoogleConnector, '__init__', lambda self, *a, **kw: None)
        monkeypatch.setattr(GoogleConnector, 'delete_event', mock_delete_event)

        ec = make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.google,
        )

        calendar = make_google_calendar(subscriber_id=TEST_USER_ID, external_connection_id=ec.id)
        attendee = make_attendee()
        appointment = make_appointment(
            calendar.id, status=AppointmentStatus.closed, meeting_link_provider=MeetingLinkProviderType.zoom, slots=[]
        )

        slot: Slot = make_appointment_slot(
            appointment_id=appointment.id,
            attendee_id=attendee.id,
            booking_status=BookingStatus.booked,
            booking_tkn='abcd',
            meeting_link_id='12345',
        )[0]

        appointment.slots = [slot]
        payload = {'reason': 'Test cancellation'}

        with patch('appointment.routes.api.get_zoom_client') as mock_get_zoom_client:
            mock_zoom_client = MagicMock()
            mock_get_zoom_client.return_value = mock_zoom_client

            response = with_client.post(f'/apmt/{appointment.id}/cancel', headers=auth_headers, json=payload)

            assert response.status_code == 200
            mock_get_zoom_client.assert_called_once()
            mock_zoom_client.delete_meeting.assert_called_with('12345')
            mock_delete_event.assert_called_once()

    def test_cancel_appointment_with_google_sends_email(
        self, monkeypatch, with_client, make_google_calendar, make_appointment, make_external_connections
    ):
        ec = make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.google,
        )

        # Patch GoogleConnector to track delete_event calls
        from appointment.controller.calendar import GoogleConnector

        mock_delete_event = MagicMock()
        monkeypatch.setattr(GoogleConnector, '__init__', lambda self, *a, **kw: None)
        monkeypatch.setattr(GoogleConnector, 'delete_event', mock_delete_event)

        calendar = make_google_calendar(subscriber_id=TEST_USER_ID, external_connection_id=ec.id)
        appointment = make_appointment(calendar_id=calendar.id)
        payload = {'reason': 'Test cancellation'}

        with patch('appointment.controller.calendar.Tools.send_cancel_vevent') as mock_send_cancel:
            response = with_client.post(f'/apmt/{appointment.id}/cancel', headers=auth_headers, json=payload)

            assert response.status_code == 200
            assert mock_send_cancel.call_count == len(appointment.slots)
            mock_delete_event.assert_called_once()

    def test_cancel_appointment_with_caldav_sends_email(
        self, monkeypatch, with_client, make_caldav_calendar, make_appointment, make_external_connections
    ):
        make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.caldav,
        )

        # Patch CalDavConnector to track delete_event calls
        from appointment.controller.calendar import CalDavConnector

        mock_delete_event = MagicMock()
        monkeypatch.setattr(CalDavConnector, 'delete_event', mock_delete_event)

        calendar = make_caldav_calendar(subscriber_id=TEST_USER_ID)
        appointment = make_appointment(calendar_id=calendar.id)
        payload = {'reason': 'Test cancellation'}

        with patch('appointment.controller.calendar.Tools.send_cancel_vevent') as mock_send_cancel:
            response = with_client.post(f'/apmt/{appointment.id}/cancel', headers=auth_headers, json=payload)

            assert response.status_code == 200
            assert mock_send_cancel.call_count == len(appointment.slots)
            assert mock_delete_event.call_count == len(appointment.slots)


class TestSyncRemoteCalendars:
    def test_sync_remote_calendars_with_multiple_google_connections(
        self, monkeypatch, with_client, make_external_connections
    ):
        """Test that sync_remote_calendars calls sync_calendars() for each Google external connection"""

        # Create two Google external connections
        make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.google,
        )
        make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.google,
        )

        # Patch GoogleConnector to track sync_calendars calls
        from appointment.controller.calendar import GoogleConnector

        mock_sync_calendars = MagicMock(return_value=False)
        monkeypatch.setattr(GoogleConnector, '__init__', lambda self, *a, **kw: None)
        monkeypatch.setattr(GoogleConnector, 'sync_calendars', mock_sync_calendars)

        response = with_client.post('/rmt/sync', headers=auth_headers)

        assert response.status_code == 200

        # Verify sync_calendars was called twice (once for each external connection)
        assert mock_sync_calendars.call_count == 2

    def test_sync_remote_calendars_with_mixed_connections(self, monkeypatch, with_client, make_external_connections):
        """Test that sync_remote_calendars handles both Google and CalDAV connections"""

        # Create one Google and one CalDAV external connection
        make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.google,
        )
        make_external_connections(
            subscriber_id=TEST_USER_ID,
            type=ExternalConnectionType.caldav,
            type_id='["https://caldav.example.com", "user1"]',
        )

        # Patch both connectors to track sync_calendars calls
        from appointment.controller.calendar import GoogleConnector, CalDavConnector

        mock_google_sync = MagicMock(return_value=False)
        mock_caldav_sync = MagicMock(return_value=False)

        monkeypatch.setattr(GoogleConnector, '__init__', lambda self, *a, **kw: None)
        monkeypatch.setattr(GoogleConnector, 'sync_calendars', mock_google_sync)
        monkeypatch.setattr(CalDavConnector, 'sync_calendars', mock_caldav_sync)

        response = with_client.post('/rmt/sync', headers=auth_headers)

        assert response.status_code == 200

        # Verify both sync_calendars methods were called once
        assert mock_google_sync.call_count == 1
        assert mock_caldav_sync.call_count == 1
