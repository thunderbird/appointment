import dateutil.parser

from defines import DAY1, DAY2, DAY3, auth_headers, TEST_USER_ID


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

            print('list events!')
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
        print(f'>>> {path}')
        response = with_client.get(path, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == generated_appointment.title
        assert data[0]['start'] == generated_appointment.slots[0].start.isoformat()
        assert data[0]['end'] == dateutil.parser.parse(DAY3).isoformat()

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

    def test_dont_show_other_subscribers_appointments(self, with_client, make_basic_subscriber, make_appointment, make_google_calendar):
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
