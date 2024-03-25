import dateutil.parser

from defines import DAY1, DAY2, DAY3, auth_headers


class TestAppointment:
    @staticmethod
    def date_time_to_str(date_time):
        return str(date_time).replace(" ", "T")

    def test_create_appointment_on_connected_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar(connected=True)

        response = with_client.post(
            "/apmt",
            json={
                "appointment": {
                    "calendar_id": generated_calendar.id,
                    "title": "Appointment",
                    "duration": 180,
                    "location_type": 2,
                    "location_name": "Location",
                    "location_url": "https://test.org",
                    "location_phone": "+123456789",
                    "details": "Lorem Ipsum",
                    "status": 2,
                    "keep_open": True,
                },
                "slots": [
                    {"start": DAY1 + " 09:00:00", "duration": 60},
                    {"start": DAY2 + " 09:00:00", "duration": 15},
                    {"start": DAY3 + " 09:00:00", "duration": 275},
                ],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_calendar.id
        assert data["title"] == "Appointment"
        assert data["duration"] == 180
        assert data["location_type"] == 2
        assert data["location_name"] == "Location"
        assert data["location_url"] == "https://test.org"
        assert data["location_phone"] == "+123456789"
        assert data["details"] == "Lorem Ipsum"
        assert data["slug"] is not None, len(data["slug"]) > 8
        assert data["status"] == 2
        assert data["keep_open"]
        assert len(data["slots"]) == 3
        assert data["slots"][0]["start"] == DAY1 + "T09:00:00"
        assert data["slots"][0]["duration"] == 60
        assert data["slots"][1]["start"] == DAY2 + "T09:00:00"
        assert data["slots"][1]["duration"] == 15
        assert data["slots"][2]["start"] == DAY3 + "T09:00:00"
        assert data["slots"][2]["duration"] == 275

    def test_create_appointment_on_unconnected_calendar(self, with_client, make_caldav_calendar):
        # They're unconnected by default, but let's be explicit for the test's sake.
        generated_calendar = make_caldav_calendar(connected=False)

        response = with_client.post(
            "/apmt",
            json={
                "appointment": {"calendar_id": generated_calendar.id, "title": "a", "duration": 30},
                "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
            },
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_create_appointment_on_missing_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar(connected=True)

        response = with_client.post(
            "/apmt",
            json={
                "appointment": {"calendar_id": generated_calendar.id + 1, "title": "a", "duration": 30},
                "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
            },
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_create_appointment_on_foreign_calendar(self, with_client, make_caldav_calendar, make_pro_subscriber):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)

        response = with_client.post(
            "/apmt",
            json={
                "appointment": {"calendar_id": generated_calendar.id, "title": "a", "duration": 30},
                "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
            },
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_read_appointments(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get("/me/appointments", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 1
        data = data[0]
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_appointment.calendar_id
        assert data["title"] == generated_appointment.title
        assert data["duration"] == generated_appointment.duration
        assert data["location_type"] == generated_appointment.location_type.value
        assert data["location_name"] == generated_appointment.location_name
        assert data["location_url"] == generated_appointment.location_url
        assert data["location_phone"] == generated_appointment.location_phone
        assert data["details"] == generated_appointment.details
        assert data["slug"] is not None, len(data["slug"]) > 8
        assert data["status"] == generated_appointment.status.value
        assert data["keep_open"]
        assert len(data["slots"]) == len(generated_appointment.slots)
        assert data["slots"][0]["start"] == self.date_time_to_str(generated_appointment.slots[0].start)
        assert data["slots"][0]["duration"] == generated_appointment.slots[0].duration

    def test_read_existing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f"/apmt/{generated_appointment.id}", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_appointment.calendar_id
        assert data["title"] == generated_appointment.title
        assert data["duration"] == generated_appointment.duration
        assert data["location_type"] == generated_appointment.location_type.value
        assert data["location_name"] == generated_appointment.location_name
        assert data["location_url"] == generated_appointment.location_url
        assert data["location_phone"] == generated_appointment.location_phone
        assert data["details"] == generated_appointment.details
        assert data["slug"] is not None, len(data["slug"]) > 8
        assert data["status"] == generated_appointment.status.value
        assert data["keep_open"]
        assert len(data["slots"]) == len(generated_appointment.slots)
        assert data["slots"][0]["start"] == self.date_time_to_str(generated_appointment.slots[0].start)
        assert data["slots"][0]["duration"] == generated_appointment.slots[0].duration

    def test_read_missing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f"/apmt/{generated_appointment.id + 1}", headers=auth_headers)
        assert response.status_code == 404, response.text

    def test_read_foreign_appointment(self, with_client, make_appointment, make_pro_subscriber, make_caldav_calendar):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_appointment = make_appointment(calendar_id=generated_calendar.id)

        response = with_client.get(f"/apmt/{generated_appointment.id}", headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_update_existing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.put(
            f"/apmt/{generated_appointment.id}",
            json={
                "appointment": {
                    "calendar_id": 4,
                    "title": "Appointmentx",
                    "duration": 90,
                    "location_type": 1,
                    "location_name": "Locationx",
                    "location_url": "https://testx.org",
                    "location_phone": "+1234567890",
                    "details": "Lorem Ipsumx",
                    "status": 1,
                    "keep_open": False,
                },
                "slots": [
                    {"start": DAY1 + " 11:00:00", "duration": 30},
                    {"start": DAY2 + " 11:00:00", "duration": 30},
                    {"start": DAY3 + " 11:00:00", "duration": 30},
                ],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == 4
        assert data["title"] == "Appointmentx"
        assert data["duration"] == 90
        assert data["location_type"] == 1
        assert data["location_name"] == "Locationx"
        assert data["location_url"] == "https://testx.org"
        assert data["location_phone"] == "+1234567890"
        assert data["details"] == "Lorem Ipsumx"
        assert data["slug"] is not None, len(data["slug"]) > 8
        assert data["status"] == 1
        assert not data["keep_open"]
        assert len(data["slots"]) == 3
        assert data["slots"][0]["start"] == DAY1 + "T11:00:00"
        assert data["slots"][0]["duration"] == 30
        assert data["slots"][1]["start"] == DAY2 + "T11:00:00"
        assert data["slots"][1]["duration"] == 30
        assert data["slots"][2]["start"] == DAY3 + "T11:00:00"
        assert data["slots"][2]["duration"] == 30

    def test_update_missing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.put(
            f"/apmt/{generated_appointment.id + 1}",
            json={
                "appointment": {"calendar_id": "2", "title": "a", "duration": 30},
                "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
            },
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_update_foreign_appointment(self, with_client, make_pro_subscriber, make_caldav_calendar, make_appointment):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_appointment = make_appointment(calendar_id=generated_calendar.id)

        response = with_client.put(
            f"/apmt/{generated_appointment.id}",
            json={
                "appointment": {"calendar_id": "2", "title": "a", "duration": 30},
                "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
            },
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_delete_existing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.delete(f"/apmt/{generated_appointment.id}", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_appointment.calendar_id
        assert data["title"] == generated_appointment.title
        assert data["duration"] == generated_appointment.duration
        assert data["location_type"] == generated_appointment.location_type.value
        assert data["location_name"] == generated_appointment.location_name
        assert data["location_url"] == generated_appointment.location_url
        assert data["location_phone"] == generated_appointment.location_phone
        assert data["details"] == generated_appointment.details
        assert data["slug"] is not None, len(data["slug"]) > 8
        assert data["status"] == generated_appointment.status.value
        assert data["keep_open"]
        assert len(data["slots"]) == len(generated_appointment.slots)
        assert data["slots"][0]["start"] == self.date_time_to_str(generated_appointment.slots[0].start)
        assert data["slots"][0]["duration"] == generated_appointment.slots[0].duration

        response = with_client.get(f"/apmt/{generated_appointment.id}", headers=auth_headers)
        assert response.status_code == 404, response.text

        response = with_client.get("/me/appointments", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 0

    def test_delete_missing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.delete(f"/apmt/{generated_appointment.id + 1}", headers=auth_headers)
        assert response.status_code == 404, response.text

    def test_delete_foreign_appointment(self, with_client, make_pro_subscriber, make_caldav_calendar, make_appointment):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_appointment = make_appointment(calendar_id=generated_calendar.id)

        response = with_client.delete(f"/apmt/{generated_appointment.id}", headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_read_public_existing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f"/apmt/public/{generated_appointment.slug}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert "calendar_id" not in data
        assert "status" not in data
        assert data["title"] == generated_appointment.title
        assert data["details"] == generated_appointment.details
        assert data["slug"] == generated_appointment.slug
        assert data["owner_name"] == generated_appointment.calendar.owner.name
        assert len(data["slots"]) == len(generated_appointment.slots)
        assert data["slots"][0]["start"] == self.date_time_to_str(generated_appointment.slots[0].start)
        assert data["slots"][0]["duration"] == generated_appointment.slots[0].duration

    def test_read_public_missing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f"/apmt/public/{generated_appointment.slug}-that-isnt-real")
        assert response.status_code == 404, response.text

    def test_read_public_appointment_after_attendee_selection(self, with_db, with_client, make_appointment, make_attendee, make_appointment_slot):
        generated_appointment = make_appointment()
        generated_attendee = make_attendee()
        make_appointment_slot(generated_appointment.id, attendee_id=generated_attendee.id)

        # db.refresh doesn't work because it only refreshes instances created by the current db session?
        with with_db() as db:
            from appointment.database import models
            generated_appointment = db.get(models.Appointment, generated_appointment.id)
            # Reload slots
            generated_appointment.slots

        response = with_client.get(f"/apmt/public/{generated_appointment.slug}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["slots"]) == len(generated_appointment.slots)
        assert data["slots"][-1]["attendee_id"] == generated_attendee.id

    def test_attendee_selects_slot_of_unavailable_appointment(self, with_db, with_client, make_appointment, make_attendee, make_appointment_slot):
        generated_appointment = make_appointment()
        generated_attendee = make_attendee()
        make_appointment_slot(generated_appointment.id, attendee_id=generated_attendee.id)

        # db.refresh doesn't work because it only refreshes instances created by the current db session?
        with with_db() as db:
            from appointment.database import models
            generated_appointment = db.get(models.Appointment, generated_appointment.id)
            # Reload slots
            generated_appointment.slots

        response = with_client.put(
            f"/apmt/public/{generated_appointment.slug}",
            json={"slot_id": generated_appointment.slots[-1].id, "attendee": {"email": "a", "name": "b"}},
        )
        assert response.status_code == 403, response.text

    def test_attendee_selects_slot_of_missing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.put(
            f"/apmt/public/{generated_appointment}",
            json={"slot_id": generated_appointment.slots[0].id, "attendee": {"email": "a", "name": "b"}},
        )
        assert response.status_code == 404, response.text

    def test_attendee_selects_missing_slot_of_existing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.put(
            f"/apmt/public/{generated_appointment.id}",
            json={"slot_id": generated_appointment.slots[0].id + 1, "attendee": {"email": "a", "name": "b"}},
        )
        assert response.status_code == 404, response.text

    def test_get_remote_caldav_events(self, with_client, make_appointment, monkeypatch):
        """Test against a fake remote caldav, we're testing the route controller, not the actual caldav connector here!"""
        from appointment.controller.calendar import CalDavConnector
        generated_appointment = make_appointment()

        def list_events(self, start, end):
            end = dateutil.parser.parse(end)
            from appointment.database import schemas
            print("list events!")
            return [schemas.Event(
                title=generated_appointment.title,
                start=generated_appointment.slots[0].start,
                end=end,
                all_day=False,
                description=generated_appointment.details,
                calendar_title=generated_appointment.calendar.title,
                calendar_color=generated_appointment.calendar.color
            )]

        monkeypatch.setattr(CalDavConnector, "list_events", list_events)

        path = f"/rmt/cal/{generated_appointment.calendar_id}/" + DAY1 + "/" + DAY3
        print(f">>> {path}")
        response = with_client.get(path, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == generated_appointment.title
        assert data[0]["start"] == generated_appointment.slots[0].start.isoformat()
        assert data[0]["end"] == dateutil.parser.parse(DAY3).isoformat()

    def test_get_invitation_ics_file(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f"/apmt/serve/ics/{generated_appointment.slug}/{generated_appointment.slots[0].id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "invite"
        assert data["content_type"] == "text/calendar"
        assert "data" in data

    def test_get_invitation_ics_file_for_missing_appointment(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f"/apmt/serve/ics/{generated_appointment.slug}-doesnt-exist/{generated_appointment.slots[0].id}")
        assert response.status_code == 404, response.text

    def test_get_invitation_ics_file_for_missing_slot(self, with_client, make_appointment):
        generated_appointment = make_appointment()

        response = with_client.get(f"/apmt/serve/ics/{generated_appointment.slug}/{generated_appointment.slots[0].id + 1}")
        assert response.status_code == 404, response.text
