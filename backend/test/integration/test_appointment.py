import dateutil.parser
from unittest.mock import patch, MagicMock

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

    def test_get_remote_caldav_events_inavlid_calendar(self, with_client, make_appointment):
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


class TestMyAppointments:
    def test_appointments(self, with_client, make_appointment, make_google_calendar):
        appointment_count = 10

        calendar = make_google_calendar(subscriber_id=TEST_USER_ID)
        appointments = [make_appointment(calendar_id=calendar.id) for _ in range(appointment_count)]

        response = with_client.get('/me/appointments', headers=auth_headers)

        assert response.status_code == 200, response.text

        data = response.json()

        assert len(data) == appointment_count

        # Should be in order
        for index, appointment in enumerate(appointments):
            assert appointment.id == data[index]['id']

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

        assert len(data) == 1
        assert other_appointment.id != data[0]['id']
        assert appointment.id == data[0]['id']


class TestCancelAppointment:
    def test_cancel_appointment(self, with_client, make_appointment, with_db):
        appointment = make_appointment()
        payload = {'reason': 'Test cancellation'}

        with patch('appointment.routes.api.Tools') as mock_tools:
            response = with_client.post(f'/apmt/{appointment.id}/cancel', headers=auth_headers, json=payload)

            assert response.status_code == 200
            assert mock_tools().send_cancel_vevent.call_count == len(appointment.slots)

        with with_db() as db:
            assert appointment_repo.get(db, appointment.id) is None

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
        
