import datetime

from freezegun import freeze_time

from appointment.database import schemas
from appointment.routes.schedule import is_this_a_valid_booking_time
from appointment.utils import retrieve_user_url_data


class TestRetrieveUserUrlData:
    def test_success(self):
        original_username = 'mycoolusername'
        original_signature = 'hello-world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature == signature
        assert original_clean_url == clean_url

    def test_success_with_extra_slashes(self):
        original_username = 'mycoolusername'
        original_signature = 'hello-world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}////////////////////////'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature == signature
        assert original_clean_url == clean_url

    def test_success_with_uriencoded_signature(self):
        original_username = 'mycoolusername'
        original_signature = 'hello%20world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username == username
        assert original_signature != signature
        assert 'hello world' == signature
        assert original_clean_url == clean_url

    def test_failure(self):
        original_username = 'mycoolusername'
        original_signature = 'hello world'
        original_clean_url = f'https://appointment.local/user/{original_username}/'
        url = f'{original_clean_url}/{original_signature}/other-junk/'

        username, signature, clean_url = retrieve_user_url_data(url)

        assert original_username != username
        assert original_signature != signature
        assert original_clean_url != clean_url


class TestIsAValidBookingTime:
    def test_bug_735(self, make_schedule):
        # Request data submitted from bug and anonymized.
        request_data = {
            's_a': {
                'attendee': {'email': 'email@example.org', 'name': 'Email Example', 'timezone': 'Europe/London'},
                'slot': {'duration': 45, 'start': '2024-11-11T17:00:00.000Z'},
            },
            'url': 'https://appointment.day/user/fake/example/',
        }

        s_a = schemas.AvailabilitySlotAttendee(**request_data['s_a'])

        schedule = make_schedule(
            active=True,
            start_date=datetime.date(2024, 11, 1),
            end_date=None,
            earliest_booking=2880,
            farthest_booking=10080,
            weekdays=[1, 2, 3, 4, 5],
            slot_duration=45,
            start_time=17,
            end_time=0,
            timezone='America/Vancouver',
            # This is not accurate, but it was probably saved before Nov 3rd.
            time_updated=datetime.datetime(2024, 11, 1, 12, 0,0, tzinfo=datetime.UTC),
        )

        # Freeze on the datetime that the error occurred on
        with freeze_time('2024-11-04T09:09:29.530Z'):
            is_valid = is_this_a_valid_booking_time(
                schedule,
                s_a.slot
            )

        assert is_valid is True
