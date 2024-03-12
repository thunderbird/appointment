from datetime import date, time, datetime

from freezegun import freeze_time

from appointment.controller.auth import signed_url_by_subscriber
from appointment.controller.calendar import CalDavConnector
from appointment.database import schemas
from appointment.exceptions import validation
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

    def test_public_availability(self, monkeypatch, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule):
        class MockCaldavConnector:
            @staticmethod
            def __init__(self, redis_instance, url, user, password, subscriber_id, calendar_id):
                """We don't want to initialize a client"""
                pass

            @staticmethod
            def list_events(self, start, end):
                return []

        monkeypatch.setattr(CalDavConnector, "__init__", MockCaldavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, "list_events", MockCaldavConnector.list_events)

        start_date = date(2024, 4, 1)
        start_time = time(9)
        end_time = time(17)

        subscriber = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(subscriber.id, connected=True)
        make_schedule(
            calendar_id=generated_calendar.id,
            active=True,
            start_date=start_date,
            start_time=start_time,
            end_time=end_time,
            end_date=None,
            earliest_booking=1440,
            farthest_booking=20160,
            slot_duration=30)

        signed_url = signed_url_by_subscriber(subscriber)

        # Check availability at the start of the schedule
        with freeze_time(start_date):
            response = with_client.post(
                "/schedule/public/availability",
                json={"url": signed_url},
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()
            slots = data['slots']

            # Based off the earliest_booking our earliest slot is tomorrow at 9:00am
            assert slots[0]['start'] == '2024-04-02T09:00:00'
            # Based off the farthest_booking our latest slot is 4:30pm
            assert slots[-1]['start'] == '2024-04-15T16:30:00'

        # Check availability over a year from now
        with freeze_time(date(2025, 6, 1)):
            response = with_client.post(
                "/schedule/public/availability",
                json={"url": signed_url},
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()
            slots = data['slots']

            assert slots[0]['start'] == '2025-06-02T09:00:00'
            assert slots[-1]['start'] == '2025-06-13T16:30:00'

        # Check availability with a start date day greater than the farthest_booking day
        with freeze_time(date(2025, 6, 27)):
            response = with_client.post(
                "/schedule/public/availability",
                json={"url": signed_url},
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()
            slots = data['slots']

            assert slots[0]['start'] == '2025-06-30T09:00:00'
            assert slots[-1]['start'] == '2025-07-11T16:30:00'

    def test_request_schedule_availability_slot(self, monkeypatch, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule):
        start_date = date(2024, 4, 1)
        start_time = time(9)
        start_datetime = datetime.combine(start_date, start_time)
        end_time = time(10)

        class MockCaldavConnector:
            @staticmethod
            def __init__(self, redis_instance, url, user, password, subscriber_id, calendar_id):
                """We don't want to initialize a client"""
                pass

            @staticmethod
            def list_events(self, start, end):
                return [
                    schemas.Event(
                        title="A blocker!",
                        start=start_datetime,
                        end=datetime.combine(start_date, end_time)
                    ),
                ]
            
            @staticmethod
            def bust_cached_events(self, all_calendars = False):
                pass

        monkeypatch.setattr(CalDavConnector, "__init__", MockCaldavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, "list_events", MockCaldavConnector.list_events)
        monkeypatch.setattr(CalDavConnector, "bust_cached_events", MockCaldavConnector.bust_cached_events)

        subscriber = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(subscriber.id, connected=True)
        make_schedule(
            calendar_id=generated_calendar.id,
            active=True,
            start_date=start_date,
            start_time=start_time,
            end_time=end_time,
            end_date=None,
            earliest_booking=1440,
            farthest_booking=20160,
            slot_duration=30)
                
        signed_url = signed_url_by_subscriber(subscriber)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(
                start=start_datetime,
                duration=30
            ),
            attendee=schemas.AttendeeBase(
                email='hello@example.org',
                name='Greg'
            )
        ).model_dump(mode='json')
        
        # Check availability at the start of the schedule
        # This should throw "Slot taken" error
        response = with_client.put(
            "/schedule/public/availability/request",
            json={
                "s_a": slot_availability,
                "url": signed_url,
            },
            headers=auth_headers,
        )
        print(response.status_code, response.json())
        assert response.status_code == 403, response.text
        data = response.json()
        
        assert data.get('detail')
        # I miss dot notation
        assert data.get('detail').get('id') == validation.SlotAlreadyTakenException.id_code

        # Okay change up the time
        start_time = time(10)

        slot_availability['slot']['start'] = datetime.combine(start_date, start_time).isoformat()

        # Check availability at the start of the schedule
        # This should work
        response = with_client.put(
            "/schedule/public/availability/request",
            json={
                "s_a": slot_availability,
                "url": signed_url,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data is True

