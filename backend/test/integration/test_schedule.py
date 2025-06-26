import zoneinfo
from datetime import date, time, datetime, timedelta, timezone, UTC
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from appointment import defines
from appointment.tasks import emails as email_tasks
from appointment.controller.auth import signed_url_by_subscriber
from appointment.controller.calendar import CalDavConnector
from appointment.database import schemas, models, repo
from appointment.exceptions import validation
from defines import DAY1, DAY5, DAY14, auth_headers, DAY2


class TestSchedule:
    @pytest.fixture
    def schedule_input(self):
        """Sample schedule input data excluding the calendar id (add that in yourself!)"""
        return {
            'name': 'Schedule',
            'location_type': 2,
            'location_url': 'https://test.org',
            'details': 'Lorem Ipsum',
            'start_date': DAY1,
            'end_date': DAY14,
            'start_time': '10:00',
            'end_time': '18:00',
            'earliest_booking': 1440,
            'farthest_booking': 20160,
            'weekdays': [1, 2, 3, 4, 5],
            'slot_duration': 30,
            'timezone': 'America/Vancouver'
        }

    def test_create_schedule_on_connected_calendar(self, with_client, make_caldav_calendar, schedule_input):
        generated_calendar = make_caldav_calendar(connected=True)

        response = with_client.post(
            '/schedule',
            json={'calendar_id': generated_calendar.id, **schedule_input},
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['time_created'] is not None
        assert data['time_updated'] is not None
        assert data['calendar_id'] == generated_calendar.id
        assert data['name'] == 'Schedule'
        assert data['location_type'] == 2
        assert data['location_url'] == 'https://test.org'
        assert data['details'] == 'Lorem Ipsum'
        assert data['start_date'] == DAY1
        assert data['end_date'] == DAY14
        assert data['start_time'] == '10:00'
        assert data['end_time'] == '18:00'
        assert data['earliest_booking'] == 1440
        assert data['farthest_booking'] == 20160
        assert data['weekdays'] is not None
        weekdays = data['weekdays']
        assert len(weekdays) == 5
        assert weekdays == [1, 2, 3, 4, 5]
        assert data['slot_duration'] == 30

    def test_create_schedule_with_end_time_before_start_time(
        self, with_client, make_caldav_calendar, make_schedule, schedule_input
    ):
        generated_calendar = make_caldav_calendar(connected=True)

        schedule_data = schedule_input
        # start_time and end_time are always in UTC
        # 9am and 8am PT
        schedule_data['start_time'] = '17:00'
        schedule_data['end_time'] = '16:00'

        response = with_client.post(
            '/schedule',
            json={'calendar_id': generated_calendar.id, **schedule_data},
            headers=auth_headers,
        )
        assert response.status_code == 422, response.text
        data = response.json()

        assert 'detail' in data
        assert len(data.get('detail')) == 1
        # Should be at least start_time + slot_duration
        # The frontend will format this because of locale and timezone concerns
        assert data.get('detail')[0]['type'] == defines.END_TIME_BEFORE_START_TIME_ERR
        assert data.get('detail')[0]['msg'] == '{field} should be at least {value}.'
        assert data.get('detail')[0]['ctx']['err_field'] == 'end_time'
        assert data.get('detail')[0]['ctx']['err_value'] == '17:30:00'

    def test_create_schedule_on_unconnected_calendar(
        self, with_client, make_caldav_calendar, make_schedule, schedule_input
    ):
        generated_calendar = make_caldav_calendar(connected=False)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.post(
            '/schedule',
            json={'calendar_id': generated_schedule.calendar_id, **schedule_input},
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_create_schedule_on_missing_calendar(self, with_client, make_schedule, schedule_input):
        generated_schedule = make_schedule()

        response = with_client.post(
            '/schedule',
            json={'calendar_id': generated_schedule.id + 1, **schedule_input},
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_create_schedule_on_foreign_calendar(
        self, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule, schedule_input
    ):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.post(
            '/schedule',
            json={
                'calendar_id': generated_schedule.id,
                **schedule_input,
            },
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_read_schedules(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.get('/schedule', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        data = data[0]
        assert data['time_created'] is not None
        assert data['time_updated'] is not None
        assert data['calendar_id'] == generated_schedule.calendar_id
        assert data['name'] == generated_schedule.name
        assert data['location_type'] == generated_schedule.location_type.value
        assert data['location_url'] == generated_schedule.location_url
        assert data['details'] == generated_schedule.details
        assert data['start_date'] == generated_schedule.start_date.isoformat()
        assert data['end_date'] == generated_schedule.end_date.isoformat()
        assert data['start_time'] == generated_schedule.start_time.isoformat('minutes')
        assert data['end_time'] == generated_schedule.end_time.isoformat('minutes')
        assert data['earliest_booking'] == generated_schedule.earliest_booking
        assert data['farthest_booking'] == generated_schedule.farthest_booking
        assert data['weekdays'] is not None
        weekdays = data['weekdays']
        assert len(weekdays) == len(generated_schedule.weekdays)
        assert weekdays == generated_schedule.weekdays
        assert data['slot_duration'] == generated_schedule.slot_duration

    def test_read_existing_schedule(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.get(f'/schedule/{generated_schedule.id}', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['time_created'] is not None
        assert data['time_updated'] is not None
        assert data['calendar_id'] == generated_schedule.calendar_id
        assert data['name'] == generated_schedule.name
        assert data['location_type'] == generated_schedule.location_type.value
        assert data['location_url'] == generated_schedule.location_url
        assert data['details'] == generated_schedule.details
        assert data['start_date'] == generated_schedule.start_date.isoformat()
        assert data['end_date'] == generated_schedule.end_date.isoformat()
        assert data['start_time'] == generated_schedule.start_time.isoformat('minutes')
        assert data['end_time'] == generated_schedule.end_time.isoformat('minutes')
        assert data['earliest_booking'] == generated_schedule.earliest_booking
        assert data['farthest_booking'] == generated_schedule.farthest_booking
        assert data['weekdays'] is not None
        weekdays = data['weekdays']
        assert len(weekdays) == len(generated_schedule.weekdays)
        assert weekdays == generated_schedule.weekdays
        assert data['slot_duration'] == generated_schedule.slot_duration

    def test_read_missing_schedule(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.get(f'/schedule/{generated_schedule.id + 1}', headers=auth_headers)
        assert response.status_code == 404, response.text

    def test_read_foreign_schedule(self, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.get(f'/schedule/{generated_schedule.id}', headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_update_existing_schedule(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={
                'calendar_id': generated_schedule.calendar_id,
                'name': 'Schedulex',
                'location_type': 1,
                'location_url': 'https://testx.org',
                'details': 'Lorem Ipsumx',
                'start_date': DAY2,
                'end_date': DAY5,
                'start_time': '09:00',
                'end_time': '17:00',
                'earliest_booking': 1000,
                'farthest_booking': 20000,
                'weekdays': [2, 4, 6],
                'slot_duration': 60,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['time_created'] is not None
        assert data['time_updated'] is not None
        assert data['calendar_id'] == generated_schedule.calendar_id
        assert data['name'] == 'Schedulex'
        assert data['location_type'] == 1
        assert data['location_url'] == 'https://testx.org'
        assert data['details'] == 'Lorem Ipsumx'
        assert data['start_date'] == DAY2
        assert data['end_date'] == DAY5
        assert data['start_time'] == '09:00'
        assert data['end_time'] == '17:00'
        assert data['earliest_booking'] == 1000
        assert data['farthest_booking'] == 20000
        assert data['weekdays'] is not None
        weekdays = data['weekdays']
        assert len(weekdays) == 3
        assert weekdays == [2, 4, 6]
        assert data['slot_duration'] == 60

    def test_update_schedule_availabilities(self, with_client, make_schedule):
        generated_schedule = make_schedule(use_custom_availabilities=True)

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={
                'calendar_id': generated_schedule.calendar_id,
                'name': 'Schedulex',
                'location_type': 1,
                'location_url': 'https://testx.org',
                'details': 'Lorem Ipsumx',
                'start_date': DAY2,
                'end_date': DAY5,
                'start_time': '09:00',
                'end_time': '17:00',
                'earliest_booking': 1000,
                'farthest_booking': 20000,
                'weekdays': [2, 4, 6],
                "use_custom_availabilities": True,
                'availabilities': [
                    {
                        'day_of_week': 2,
                        'start_time': '09:00',
                        'end_time': '15:00',
                        'schedule_id': generated_schedule.id,
                    },
                    {
                        'day_of_week': 4,
                        'start_time': '11:00',
                        'end_time': '15:00',
                        'schedule_id': generated_schedule.id,
                    },
                    {
                        'day_of_week': 6,
                        'start_time': '13:00',
                        'end_time': '15:00',
                        'schedule_id': generated_schedule.id,
                    },
                ],
                'slot_duration': 60,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['weekdays'] is not None
        assert len(data['weekdays']) == 3
        assert data['weekdays'] == [2, 4, 6]
        assert data['availabilities'] is not None
        assert len(data['availabilities']) == 3
        assert data['availabilities'][2]['day_of_week'] == 6

    def test_update_multiple_valid_schedule_availabilities_per_weekday(self, with_client, make_schedule):
        generated_schedule = make_schedule(use_custom_availabilities=True)

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={
                'calendar_id': generated_schedule.calendar_id,
                'name': 'Schedulex',
                'location_type': 1,
                'location_url': 'https://testx.org',
                'details': 'Lorem Ipsumx',
                'start_date': DAY2,
                'end_date': DAY5,
                'start_time': '09:00',
                'end_time': '17:00',
                'earliest_booking': 1000,
                'farthest_booking': 20000,
                'weekdays': [4],
                "use_custom_availabilities": True,
                'availabilities': [
                    {
                        'day_of_week': 4,
                        'start_time': '09:00',
                        'end_time': '10:00',
                        'schedule_id': generated_schedule.id,
                    },
                    {
                        'day_of_week': 4,
                        'start_time': '11:00',
                        'end_time': '13:00',
                        'schedule_id': generated_schedule.id,
                    },
                    {
                        'day_of_week': 4,
                        'start_time': '14:00',
                        'end_time': '16:00',
                        'schedule_id': generated_schedule.id,
                    },
                ],
                'slot_duration': 60,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['weekdays'] is not None
        assert len(data['weekdays']) == 1
        assert data['weekdays'] == [4]
        assert data['availabilities'] is not None
        assert len(data['availabilities']) == 3
        assert data['availabilities'][2]['day_of_week'] == 4

    def test_update_multiple_invalid_schedule_availabilities_per_weekday(self, with_client, make_schedule):
        # Test invalid adjacent time slots
        generated_schedule = make_schedule(use_custom_availabilities=True)

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={
                'calendar_id': generated_schedule.calendar_id,
                'name': 'Schedulex',
                'location_type': 1,
                'location_url': 'https://testx.org',
                'details': 'Lorem Ipsumx',
                'start_date': DAY2,
                'end_date': DAY5,
                'start_time': '09:00',
                'end_time': '17:00',
                'earliest_booking': 1000,
                'farthest_booking': 20000,
                'weekdays': [4],
                "use_custom_availabilities": True,
                'availabilities': [
                    {
                        'day_of_week': 4,
                        'start_time': '09:00',
                        'end_time': '10:00',
                        'schedule_id': generated_schedule.id,
                    },
                    {
                        'day_of_week': 4,
                        'start_time': '09:00',
                        'end_time': '11:00',
                        'schedule_id': generated_schedule.id,
                    },
                ],
                'slot_duration': 60,
            },
            headers=auth_headers,
        )
        assert response.status_code == 400, response.text

        # Test invalid start / end times
        generated_schedule = make_schedule(use_custom_availabilities=True)

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={
                'calendar_id': generated_schedule.calendar_id,
                'name': 'Schedulex',
                'location_type': 1,
                'location_url': 'https://testx.org',
                'details': 'Lorem Ipsumx',
                'start_date': DAY2,
                'end_date': DAY5,
                'start_time': '09:00',
                'end_time': '17:00',
                'earliest_booking': 1000,
                'farthest_booking': 20000,
                'weekdays': [4],
                "use_custom_availabilities": True,
                'availabilities': [
                    {
                        'day_of_week': 4,
                        'start_time': '13:00',
                        'end_time': '12:00',
                        'schedule_id': generated_schedule.id,
                    },
                ],
                'slot_duration': 60,
            },
            headers=auth_headers,
        )
        assert response.status_code == 400, response.text

        # Test duration of a slot is to small (won't fit into the configured slot_duration)
        generated_schedule = make_schedule(use_custom_availabilities=True)

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={
                'calendar_id': generated_schedule.calendar_id,
                'name': 'Schedulex',
                'location_type': 1,
                'location_url': 'https://testx.org',
                'details': 'Lorem Ipsumx',
                'start_date': DAY2,
                'end_date': DAY5,
                'start_time': '09:00',
                'end_time': '17:00',
                'earliest_booking': 1000,
                'farthest_booking': 20000,
                'weekdays': [4],
                "use_custom_availabilities": True,
                'availabilities': [
                    {
                        'day_of_week': 4,
                        'start_time': '09:00',
                        'end_time': '10:00',
                        'schedule_id': generated_schedule.id,
                    },
                    {
                        'day_of_week': 4,
                        'start_time': '13:00',
                        'end_time': '13:30',
                        'schedule_id': generated_schedule.id,
                    },
                ],
                'slot_duration': 60,
            },
            headers=auth_headers,
        )
        assert response.status_code == 400, response.text

    def test_update_existing_schedule_with_html(self, with_client, make_schedule):
        generated_schedule = make_schedule()

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={
                'calendar_id': generated_schedule.calendar_id,
                'name': '<i>Schedule</i>',
                'details': 'Lorem <p>test</p> Ipsum<br><script>run_evil();</script>',
                'start_time': '09:00',
                'end_time': '17:00',
                'start_date': DAY2,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['name'] == 'Schedule'
        assert data['details'] == 'Lorem test Ipsum'

    def test_update_missing_schedule(self, with_client, make_schedule, schedule_input):
        generated_schedule = make_schedule()

        response = with_client.put(
            f'/schedule/{generated_schedule.id + 1}',
            json={'calendar_id': generated_schedule.calendar_id, **schedule_input},
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_update_foreign_schedule(
        self, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule, schedule_input
    ):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={'calendar_id': generated_schedule.calendar_id, **schedule_input},
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text

    def test_update_schedule_unconnected_calendar(
        self, with_client, make_caldav_calendar, make_schedule, schedule_input
    ):
        generated_calendar = make_caldav_calendar(connected=False)
        generated_schedule = make_schedule(calendar_id=generated_calendar.id)

        response = with_client.put(
            f'/schedule/{generated_schedule.id}',
            json={'calendar_id': generated_schedule.calendar_id, **schedule_input},
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text
        data = response.json()
        assert data['detail']['id'] == 'CALENDAR_NOT_CONNECTED'

    def test_public_availability(
        self, monkeypatch, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule
    ):
        class MockCaldavConnector:
            @staticmethod
            def __init__(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
                """We don't want to initialize a client"""
                pass

            @staticmethod
            def get_busy_time(self, remote_calendar_ids, start, end):
                return []

        monkeypatch.setattr(CalDavConnector, '__init__', MockCaldavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, 'get_busy_time', MockCaldavConnector.get_busy_time)

        start_date = date(2024, 3, 1)
        start_time = time(16, tzinfo=UTC)
        # Next day
        end_time = time(0, tzinfo=UTC)

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
            slot_duration=30,
        )

        signed_url = signed_url_by_subscriber(subscriber)

        # Check availability at the start of the schedule
        with freeze_time(start_date):
            response = with_client.post(
                '/schedule/public/availability',
                json={'url': signed_url},
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()
            slots = data['slots']

            # Based off the earliest_booking our earliest slot is tomorrow at 9:00am
            # Note: this should be in PDT (Pacific Daylight Time)
            assert slots[0]['start'] == '2024-03-04T09:00:00-08:00'
            # Based off the farthest_booking our latest slot is 4:30pm
            # Note: This should be in PDT (Pacific Daylight Time)
            # Note2: The schedule ends at 0 UTC (or 16-07:00) so the last slot is 30 mins before that.
            assert slots[-1]['start'] == '2024-03-15T16:30:00-07:00'

        # Check availability over a year from now
        with freeze_time(date(2025, 6, 1)):
            response = with_client.post(
                '/schedule/public/availability',
                json={'url': signed_url},
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()
            slots = data['slots']

            assert slots[0]['start'] == '2025-06-02T09:00:00-07:00'
            assert slots[-1]['start'] == '2025-06-13T16:30:00-07:00'

        # Check availability with a start date day greater than the farthest_booking day
        with freeze_time(date(2025, 6, 27)):
            response = with_client.post(
                '/schedule/public/availability',
                json={'url': signed_url},
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()
            slots = data['slots']

            assert slots[0]['start'] == '2025-06-30T09:00:00-07:00'
            assert slots[-1]['start'] == '2025-07-11T16:30:00-07:00'

    def test_public_availability_with_blockers(
        self, monkeypatch, with_client, make_pro_subscriber, make_caldav_calendar, make_schedule
    ):
        """Test public availability route with blocked off times.
        Ensuring the blocked off time displays as such and is otherwise normal.
        """
        start_date = date(2024, 3, 3)
        end_date = date(2024, 3, 6)

        tz = zoneinfo.ZoneInfo('America/Vancouver')

        # In UTC... 9 - 4 Vancouver time
        schedule_start_time = time(17, tzinfo=UTC)
        schedule_end_time = time(0, tzinfo=UTC)

        # Test times are asserted against events created by blocker times.
        # Follows the format:
        # { (start_datetime, end_datetime): can we book? }
        testing_times = {
            # 10:00 - 11:00 = Blocked
            (datetime(2024, 3, 4, 10, tzinfo=tz), datetime(2024, 3, 4, 11, tzinfo=tz)): False,
            # 12:00 - 14:00 = Bookable!
            (datetime(2024, 3, 4, 12, tzinfo=tz), datetime(2024, 3, 4, 14, tzinfo=tz)): True,
            # 15:00 - 16:00 = Blocked
            (datetime(2024, 3, 4, 15, tzinfo=tz), datetime(2024, 3, 4, 16, tzinfo=tz)): False,
        }

        # Note: These must be timezoned
        blocker_times = [
            # Blocker 10:00 - 11:00
            (datetime(2024, 3, 4, 10, tzinfo=tz), datetime(2024, 3, 4, 11, tzinfo=tz)),
            # Blocker 15:30 - 16:00
            (datetime(2024, 3, 4, 15, 30, tzinfo=tz), datetime(2024, 3, 4, 16, tzinfo=tz)),
        ]

        class MockCaldavConnector:
            @staticmethod
            def __init__(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
                """We don't want to initialize a client"""
                pass

            @staticmethod
            def get_busy_time(self, calendar_ids, start, end):
                return [
                    {'start': start_end_datetimes[0], 'end': start_end_datetimes[1]}
                    for start_end_datetimes in blocker_times
                ]

        monkeypatch.setattr(CalDavConnector, '__init__', MockCaldavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, 'get_busy_time', MockCaldavConnector.get_busy_time)

        subscriber = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(subscriber.id, connected=True)
        make_schedule(
            calendar_id=generated_calendar.id,
            active=True,
            start_date=start_date,
            start_time=schedule_start_time,
            end_time=schedule_end_time,
            end_date=end_date,
            earliest_booking=1440,
            farthest_booking=20160,
            slot_duration=30,
        )

        signed_url = signed_url_by_subscriber(subscriber)

        with freeze_time(start_date):
            # Check availability at the start of the schedule
            response = with_client.post(
                '/schedule/public/availability',
                json={'url': signed_url},
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()
            slots = data['slots']

            # Remap slots into dict with start time as key
            start_dates = map(lambda s: s['start'], slots)
            slots_dict = dict(zip(start_dates, slots))

            for test_time, expected_assert in testing_times.items():
                # Format our test time as an iso date string
                iso = test_time[0].isoformat()
                assert iso in slots_dict

                slot = slots_dict[iso]
                assert (
                    slot['booking_status'] == models.BookingStatus.none.value
                    if expected_assert
                    else models.BookingStatus.booked.value
                )

    def test_public_availability_sched_not_active(self, with_client, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        signed_url = signed_url_by_subscriber(subscriber)

        # Check availability at the start of the schedule
        response = with_client.post(
            '/schedule/public/availability',
            json={'url': signed_url},
            headers=auth_headers,
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail']['id'] == 'SCHEDULE_NOT_ACTIVE'


class TestRequestScheduleAvailability:
    @pytest.fixture
    def mock_connector(self, monkeypatch):
        class MockCaldavConnector:
            @staticmethod
            def __init__(self, db, redis_instance, url, user, password, subscriber_id, calendar_id):
                """We don't want to initialize a client"""
                pass

            @staticmethod
            def list_events(self, start, end):
                return []

            @staticmethod
            def bust_cached_events(self, all_calendars=False):
                pass

        monkeypatch.setattr(CalDavConnector, '__init__', MockCaldavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, 'list_events', MockCaldavConnector.list_events)
        monkeypatch.setattr(CalDavConnector, 'bust_cached_events', MockCaldavConnector.bust_cached_events)

    @pytest.fixture
    def setup_schedule(self, make_pro_subscriber, make_caldav_calendar, make_schedule):
        self.start_date = date(2024, 4, 1)
        self.start_time = time(9, tzinfo=UTC)
        self.end_time = time(10, tzinfo=UTC)

        self.subscriber = make_pro_subscriber()
        self.calendar = make_caldav_calendar(self.subscriber.id, connected=True)
        self.schedule = make_schedule(
            calendar_id=self.calendar.id,
            active=True,
            start_date=self.start_date,
            start_time=self.start_time,
            end_time=self.end_time,
            end_date=None,
            earliest_booking=1440,
            farthest_booking=20160,
            slot_duration=30,
            booking_confirmation=False,
            use_custom_availabilities=False,
            weekdays=[1, 2, 3, 4, 5],
        )
        self.signed_url = signed_url_by_subscriber(self.subscriber)

    def test_fail_and_success(
        self,
        monkeypatch,
        with_db,
        with_client,
        make_pro_subscriber,
        make_caldav_calendar,
        make_schedule,
        mock_connector,
    ):
        """Test that a user can request a booking from a schedule"""
        start_date = date(2024, 4, 1)
        start_time = time(9, tzinfo=UTC)
        start_datetime = datetime.combine(start_date, start_time, tzinfo=timezone.utc)
        end_time = time(15, tzinfo=UTC)

        class MockCaldavConnector:
            @staticmethod
            def get_busy_time(self, calendar_ids, start, end):
                return [
                    {
                        'start': start_datetime,
                        'end': datetime.combine(start_date, start_time, tzinfo=timezone.utc) + timedelta(minutes=10),
                    },
                    {
                        'start': start_datetime + timedelta(minutes=10),
                        'end': datetime.combine(start_date, start_time, tzinfo=timezone.utc) + timedelta(minutes=20),
                    },
                ]

        # Override the fixture's list_events
        monkeypatch.setattr(CalDavConnector, 'get_busy_time', MockCaldavConnector.get_busy_time)

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
            slot_duration=30,
        )

        signed_url = signed_url_by_subscriber(subscriber)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=start_datetime, duration=30),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        # Check availability at the start of the schedule
        # This should throw "Slot taken" error
        response = with_client.put(
            '/schedule/public/availability/request',
            json={
                's_a': slot_availability,
                'url': signed_url,
            },
            headers=auth_headers,
        )

        assert response.status_code == 403, response.text
        data = response.json()

        assert data.get('detail')
        # I miss dot notation
        assert data.get('detail').get('id') == validation.SlotAlreadyTakenException.id_code

        # Okay change up the time
        slot_availability['slot']['start'] = datetime.combine(start_date, time(11), tzinfo=timezone.utc).isoformat()
        # Check availability at the start of the schedule
        # This should work
        response = with_client.put(
            '/schedule/public/availability/request',
            json={
                's_a': slot_availability,
                'url': signed_url,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get('id')

        slot_id = data.get('id')

        # Look up the slot
        with with_db() as db:
            slot = repo.slot.get(db, slot_id)
            assert slot.appointment_id

    def test_success_with_no_confirmation(
        self,
        monkeypatch,
        with_db,
        with_client,
        make_pro_subscriber,
        make_caldav_calendar,
        make_schedule,
        mock_connector,
    ):
        """Test that a user can request a booking from a schedule"""
        start_date = date(2024, 4, 1)
        start_time = time(9, tzinfo=UTC)
        start_datetime = datetime.combine(start_date, start_time, tzinfo=timezone.utc)
        end_time = time(10, tzinfo=UTC)

        class MockCaldavConnector:
            @staticmethod
            def get_busy_time(self, calendar_ids, start, end):
                return []

        # Override the fixture's list_events
        monkeypatch.setattr(CalDavConnector, 'get_busy_time', MockCaldavConnector.get_busy_time)

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
            slot_duration=30,
            booking_confirmation=False,
            use_custom_availabilities=False,
        )

        signed_url = signed_url_by_subscriber(subscriber)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=start_datetime, duration=30),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            # Check availability at the start of the schedule
            # This should work
            response = with_client.put(
                '/schedule/public/availability/request',
                json={
                    's_a': slot_availability,
                    'url': signed_url,
                },
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()

            assert data.get('id')

            slot_id = data.get('id')

            # Look up the slot
            with with_db() as db:
                slot = repo.slot.get(db, slot_id)
                assert slot.appointment_id

            # Ensure we sent out an invite email and a new booking email
            assert mock.call_count == 2
            send_invite_email_call, send_new_booking_email_call = mock.call_args_list

            # Functions are stored in a tuple as the first item on the call
            assert email_tasks.send_invite_email in send_invite_email_call[0]
            assert email_tasks.send_new_booking_email in send_new_booking_email_call[0]

    def test_fail_not_utc(self, with_client, mock_connector, setup_schedule):
        """Ensure we fail validation because we submitted a non-utc booking time"""
        booking_time = datetime.combine(self.start_date, self.start_time, tzinfo=zoneinfo.ZoneInfo('America/Vancouver'))

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=booking_time, duration=30),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            # Check availability at the start of the schedule
            # This should work
            response = with_client.put(
                '/schedule/public/availability/request',
                json={
                    's_a': slot_availability,
                    'url': self.signed_url,
                },
                headers=auth_headers,
            )
            assert response.status_code == 404, response.text

            data = response.json()

            assert data.get('detail', {}).get('id') == 'SLOT_NOT_FOUND'

            # Ensure we haven't sent out any emails
            assert mock.call_count == 0

    def test_fail_slot_duration_mismatch(self, with_client, mock_connector, setup_schedule):
        """Ensure we fail validation because we submitted a 60 min when the schedule only supports 30 minute slots"""
        booking_time = datetime.combine(self.start_date, self.start_time, tzinfo=timezone.utc)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=booking_time, duration=60),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            # Check availability at the start of the schedule
            # This should work
            response = with_client.put(
                '/schedule/public/availability/request',
                json={
                    's_a': slot_availability,
                    'url': self.signed_url,
                },
                headers=auth_headers,
            )
            assert response.status_code == 404, response.text

            data = response.json()

            assert data.get('detail', {}).get('id') == 'SLOT_NOT_FOUND'

            # Ensure we haven't sent out any emails
            assert mock.call_count == 0

    def test_fail_on_invalid_weekday(self, with_client, mock_connector, setup_schedule):
        """Ensure we fail validation because we are booking on a Saturday and the schedule only supports bookings
        Monday through Friday."""
        booking_time = datetime.combine(date(2024, 4, 6), self.start_time, tzinfo=timezone.utc)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=booking_time, duration=30),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            # Check availability at the start of the schedule
            # This should work
            response = with_client.put(
                '/schedule/public/availability/request',
                json={
                    's_a': slot_availability,
                    'url': self.signed_url,
                },
                headers=auth_headers,
            )
            assert response.status_code == 404, response.text

            data = response.json()

            assert data.get('detail', {}).get('id') == 'SLOT_NOT_FOUND'

            # Ensure we haven't sent out any emails
            assert mock.call_count == 0

    def test_fail_on_before_time_range(self, with_client, mock_connector, setup_schedule):
        """Ensure we fail validation because we're booking 30 minutes before the schedule starts."""
        booking_time = datetime.combine(self.start_date, time(8, 30), tzinfo=timezone.utc)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=booking_time, duration=30),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            # Check availability at the start of the schedule
            # This should work
            response = with_client.put(
                '/schedule/public/availability/request',
                json={
                    's_a': slot_availability,
                    'url': self.signed_url,
                },
                headers=auth_headers,
            )
            assert response.status_code == 404, response.text

            data = response.json()

            assert data.get('detail', {}).get('id') == 'SLOT_NOT_FOUND'

            # Ensure we haven't sent out any emails
            assert mock.call_count == 0

    def test_fail_on_after_time_range(self, with_client, mock_connector, setup_schedule):
        """Ensure we fail validation because we're booking on the schedule's end time."""
        booking_time = datetime.combine(self.start_date, time(10), tzinfo=timezone.utc)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=booking_time, duration=30),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            # Check availability at the start of the schedule
            # This should work
            response = with_client.put(
                '/schedule/public/availability/request',
                json={
                    's_a': slot_availability,
                    'url': self.signed_url,
                },
                headers=auth_headers,
            )
            assert response.status_code == 404, response.text

            data = response.json()

            assert data.get('detail', {}).get('id') == 'SLOT_NOT_FOUND'

            # Ensure we haven't sent out any emails
            assert mock.call_count == 0

    def test_success_with_custom_availability(
        self,
        monkeypatch,
        with_db,
        with_client,
        make_pro_subscriber,
        make_caldav_calendar,
        make_schedule,
        mock_connector,
    ):
        """Test that a user can request a booking from a schedule with custom availability slots"""
        start_date = date(2024, 4, 1)
        start_time = time(9, tzinfo=UTC)
        start_datetime = datetime.combine(start_date, start_time, tzinfo=timezone.utc)
        end_time = time(10, tzinfo=UTC)

        class MockCaldavConnector:
            @staticmethod
            def get_busy_time(self, calendar_ids, start, end):
                return []

        # Override the fixture's list_events
        monkeypatch.setattr(CalDavConnector, 'get_busy_time', MockCaldavConnector.get_busy_time)

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
            slot_duration=30,
            booking_confirmation=False,
            use_custom_availabilities=True,
        )

        signed_url = signed_url_by_subscriber(subscriber)

        slot_availability = schemas.AvailabilitySlotAttendee(
            slot=schemas.SlotBase(start=start_datetime, duration=30),
            attendee=schemas.AttendeeBase(email='hello@example.org', name='Greg', timezone='Europe/Berlin'),
        ).model_dump(mode='json')

        with patch('fastapi.BackgroundTasks.add_task') as mock:
            # Check availability at the start of the schedule
            # This should work
            response = with_client.put(
                '/schedule/public/availability/request',
                json={
                    's_a': slot_availability,
                    'url': signed_url,
                },
                headers=auth_headers,
            )
            assert response.status_code == 200, response.text
            data = response.json()

            assert data.get('id')

            slot_id = data.get('id')

            # Look up the slot
            with with_db() as db:
                slot = repo.slot.get(db, slot_id)
                assert slot.appointment_id

            # Ensure we sent out an invite email and a new booking email
            assert mock.call_count == 2
            send_invite_email_call, send_new_booking_email_call = mock.call_args_list

            # Functions are stored in a tuple as the first item on the call
            assert email_tasks.send_invite_email in send_invite_email_call[0]
            assert email_tasks.send_new_booking_email in send_new_booking_email_call[0]

class TestDecideScheduleAvailabilitySlot:
    start_date = datetime.now() - timedelta(days=4)
    start_date = start_date.date()
    start_time = time(9, tzinfo=UTC)
    start_datetime = datetime.combine(start_date, start_time)
    end_time = time(10, tzinfo=UTC)

    def test_confirm(
        self,
        with_db,
        with_client,
        make_pro_subscriber,
        make_caldav_calendar,
        make_schedule,
        make_appointment,
        make_appointment_slot,
        make_attendee,
    ):
        subscriber = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(subscriber.id, connected=True)
        schedule = make_schedule(
            calendar_id=generated_calendar.id,
            active=True,
            start_date=self.start_date,
            start_time=self.start_time,
            end_time=self.end_time,
            end_date=None,
            earliest_booking=1440,
            farthest_booking=20160,
            slot_duration=30,
        )

        signed_url = signed_url_by_subscriber(subscriber)

        # Requested booking
        attendee = make_attendee()
        appointment = make_appointment(generated_calendar.id, status=models.AppointmentStatus.draft, slots=[])
        slot: models.Slot = make_appointment_slot(
            appointment_id=appointment.id,
            attendee_id=attendee.id,
            booking_status=models.BookingStatus.requested,
            booking_tkn='abcd',
        )[0]

        with with_db() as db:
            # Bring the db slot to our db session
            db.add(slot)
            db.add(appointment)

            slot_id = slot.id
            appointment_id = appointment.id

            slot.schedule_id = schedule.id
            db.commit()

            availability = schemas.AvailabilitySlotConfirmation(
                slot_id=slot_id, slot_token=slot.booking_tkn, owner_url=signed_url, confirmed=True
            ).model_dump()

        response = with_client.put(
            '/schedule/public/availability/booking',
            json=availability,
            headers=auth_headers,
        )

        with with_db() as db:
            assert response.status_code == 200, response.content

            slot = db.get(models.Slot, slot_id)
            appointment = db.get(models.Appointment, appointment_id)

            assert slot.booking_status == models.BookingStatus.booked
            assert appointment.status == models.AppointmentStatus.closed

        # Now try to confirm the same event again
        response = with_client.put(
            '/schedule/public/availability/booking',
            json=availability,
            headers=auth_headers,
        )

        assert response.status_code == 404, response.text


    def test_deny(
        self,
        with_db,
        with_client,
        make_pro_subscriber,
        make_caldav_calendar,
        make_schedule,
        make_appointment,
        make_appointment_slot,
        make_attendee,
    ):
        subscriber = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(subscriber.id, connected=True)
        schedule = make_schedule(
            calendar_id=generated_calendar.id,
            active=True,
            start_date=self.start_date,
            start_time=self.start_time,
            end_time=self.end_time,
            end_date=None,
            earliest_booking=1440,
            farthest_booking=20160,
            slot_duration=30,
        )

        signed_url = signed_url_by_subscriber(subscriber)

        # Requested booking
        attendee = make_attendee()
        appointment = make_appointment(generated_calendar.id, status=models.AppointmentStatus.draft, slots=[])
        slot: models.Slot = make_appointment_slot(
            appointment_id=appointment.id,
            attendee_id=attendee.id,
            booking_status=models.BookingStatus.requested,
            booking_tkn='abcd',
        )[0]

        with with_db() as db:
            # Bring the db slot to our db session
            db.add(slot)
            db.add(appointment)

            slot_id = slot.id
            appointment_id = appointment.id

            slot.schedule_id = schedule.id
            db.commit()

            availability = schemas.AvailabilitySlotConfirmation(
                slot_id=slot_id, slot_token=slot.booking_tkn, owner_url=signed_url, confirmed=False
            ).model_dump()

        response = with_client.put(
            '/schedule/public/availability/booking',
            json=availability,
            headers=auth_headers,
        )

        with with_db() as db:
            assert response.status_code == 200, response.content

            slot = db.get(models.Slot, slot_id)
            appointment = db.get(models.Appointment, appointment_id)

            assert slot is None
            assert appointment is None

        # Now try to deny the same event again
        response = with_client.put(
            '/schedule/public/availability/booking',
            json=availability,
            headers=auth_headers,
        )

        assert response.status_code == 404, response.text
