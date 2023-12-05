import os
from defines import DAY1, DAY5, DAY14, auth_headers, DAY2


class TestSchedule:
    def test_create_schedule_on_connected_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar(connected=True)

        response = with_client.post(
            "/schedule",
            json={
                "calendar_id": generated_calendar.id,
                "name": "Schedule",
                "location_type": 2,
                "location_url": "https://test.org",
                "details": "Lorem Ipsum",
                "start_date": DAY1,
                "end_date": DAY14,
                "start_time": "10:00",
                "end_time": "18:00",
                "earliest_booking": 1440,
                "farthest_booking": 20160,
                "weekdays": [1, 2, 3, 4, 5],
                "slot_duration": 30,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_calendar.id
        assert data["name"] == "Schedule"
        assert data["location_type"] == 2
        assert data["location_url"] == "https://test.org"
        assert data["details"] == "Lorem Ipsum"
        assert data["start_date"] == DAY1
        assert data["end_date"] == DAY14
        assert data["start_time"] == "10:00"
        assert data["end_time"] == "18:00"
        assert data["earliest_booking"] == 1440
        assert data["farthest_booking"] == 20160
        assert data["weekdays"] is not None
        weekdays = data["weekdays"]
        assert len(weekdays) == 5
        assert weekdays == [1, 2, 3, 4, 5]
        assert data["slot_duration"] == 30

    def test_create_schedule_on_unconnected_calendar(self, with_client, make_caldav_calendar, make_schedule):
        generated_calendar = make_caldav_calendar(connected=False)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.post(
            "/schedule",
            json={"calendar_id": generated_schedule.calendar_id, "name": "Schedule"},
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_create_schedule_on_missing_calendar(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.post(
            "/schedule",
            json={"calendar_id": generated_schedule.id + 1, "name": "Schedule"},
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_create_schedule_on_foreign_calendar(self, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.post(
            "/schedule",
            json={"calendar_id": generated_schedule.id, "name": "Schedule"},
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_read_schedules(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.get("/schedule", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 1
        data = data[0]
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_schedule.calendar_id
        assert data["name"] == generated_schedule.name
        assert data["location_type"] == generated_schedule.location_type.value
        assert data["location_url"] == generated_schedule.location_url
        assert data["details"] == generated_schedule.details
        assert data["start_date"] == generated_schedule.start_date.isoformat()
        assert data["end_date"] == generated_schedule.end_date.isoformat()
        assert data["start_time"] == generated_schedule.start_time.isoformat('minutes')
        assert data["end_time"] == generated_schedule.end_time.isoformat('minutes')
        assert data["earliest_booking"] == generated_schedule.earliest_booking
        assert data["farthest_booking"] == generated_schedule.farthest_booking
        assert data["weekdays"] is not None
        weekdays = data["weekdays"]
        assert len(weekdays) == len(generated_schedule.weekdays)
        assert weekdays == generated_schedule.weekdays
        assert data["slot_duration"] == generated_schedule.slot_duration

    def test_read_existing_schedule(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.get(f"/schedule/{generated_schedule.id}", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_schedule.calendar_id
        assert data["name"] == generated_schedule.name
        assert data["location_type"] == generated_schedule.location_type.value
        assert data["location_url"] == generated_schedule.location_url
        assert data["details"] == generated_schedule.details
        assert data["start_date"] == generated_schedule.start_date.isoformat()
        assert data["end_date"] == generated_schedule.end_date.isoformat()
        assert data["start_time"] == generated_schedule.start_time.isoformat('minutes')
        assert data["end_time"] == generated_schedule.end_time.isoformat('minutes')
        assert data["earliest_booking"] == generated_schedule.earliest_booking
        assert data["farthest_booking"] == generated_schedule.farthest_booking
        assert data["weekdays"] is not None
        weekdays = data["weekdays"]
        assert len(weekdays) == len(generated_schedule.weekdays)
        assert weekdays == generated_schedule.weekdays
        assert data["slot_duration"] == generated_schedule.slot_duration

    def test_read_missing_schedule(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.get(f"/schedule/{generated_schedule.id + 1}", headers=auth_headers)
        assert response.status_code == 404, response.text

    def test_read_foreign_schedule(self, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.get(f"/schedule/{generated_schedule.id}", headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_update_existing_schedule(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.put(
            f"/schedule/{generated_schedule.id}",
            json={
                "calendar_id": generated_schedule.calendar_id,
                "name": "Schedulex",
                "location_type": 1,
                "location_url": "https://testx.org",
                "details": "Lorem Ipsumx",
                "start_date": DAY2,
                "end_date": DAY5,
                "start_time": "09:00",
                "end_time": "17:00",
                "earliest_booking": 1000,
                "farthest_booking": 20000,
                "weekdays": [2, 4, 6],
                "slot_duration": 60,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["time_created"] is not None
        assert data["time_updated"] is not None
        assert data["calendar_id"] == generated_schedule.calendar_id
        assert data["name"] == "Schedulex"
        assert data["location_type"] == 1
        assert data["location_url"] == "https://testx.org"
        assert data["details"] == "Lorem Ipsumx"
        assert data["start_date"] == DAY2
        assert data["end_date"] == DAY5
        assert data["start_time"] == "09:00"
        assert data["end_time"] == "17:00"
        assert data["earliest_booking"] == 1000
        assert data["farthest_booking"] == 20000
        assert data["weekdays"] is not None
        weekdays = data["weekdays"]
        assert len(weekdays) == 3
        assert weekdays == [2, 4, 6]
        assert data["slot_duration"] == 60

    def test_update_missing_schedule(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.put(
            f"/schedule/{generated_schedule.id + 1}",
            json={"calendar_id": generated_schedule.calendar_id, "name": "Schedule"},
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_update_foreign_schedule(self, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.put(
            f"/schedule/{generated_schedule.id}",
            json={"calendar_id": generated_schedule.calendar_id, "name": "Schedule"},
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text
