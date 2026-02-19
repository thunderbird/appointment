import math
import os
from datetime import datetime

from appointment.database import repo
from defines import auth_headers, TEST_USER_ID
from appointment.database.models import SubscriberLevel


class TestSubscriber:
    def test_get_all_subscribers(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        response = with_client.post(
            '/subscriber',
            headers=auth_headers,
            json={
                'page': 1,
            },
        )

        assert response.status_code == 200, response.text
        data = response.json()['items']
        number_of_subscribers = len(data)
        assert number_of_subscribers > 0

        # verify values
        test_subscriber = data[TEST_USER_ID - 1]
        assert test_subscriber['username'] == os.getenv('TEST_USER_EMAIL')
        assert test_subscriber['email'] == os.getenv('TEST_USER_EMAIL')
        assert test_subscriber['preferred_email'] == os.getenv('TEST_USER_EMAIL')
        assert test_subscriber['name'] == 'Test Account'
        assert test_subscriber['short_link_hash'] == 'abc1234'
        assert test_subscriber['id'] == TEST_USER_ID
        assert test_subscriber['language'] == 'en'
        assert test_subscriber['timezone'] == 'America/Vancouver'
        assert test_subscriber['is_setup'] is False
        assert test_subscriber['ftue_level'] == 0
        assert test_subscriber['level'] == SubscriberLevel.pro.value

        # now make a new basic subscriber
        new_subscriber = make_basic_subscriber()

        # get subscribers again
        response = with_client.post(
            '/subscriber',
            headers=auth_headers,
            json={
                'page': 1,
            },
        )

        assert response.status_code == 200, response.text
        data = response.json()['items']

        # the last subscriber in the returned list is the latest one we created, verify values
        assert len(data) == number_of_subscribers + 1
        subscriber_ret = data[len(data) - 1]
        assert subscriber_ret['username'] == new_subscriber.username
        assert subscriber_ret['email'] == new_subscriber.email
        assert subscriber_ret['preferred_email'] == new_subscriber.preferred_email
        assert subscriber_ret['name'] == new_subscriber.name
        assert subscriber_ret['short_link_hash'] == new_subscriber.short_link_hash
        assert subscriber_ret['id'] == number_of_subscribers + 1
        assert subscriber_ret['language'] == new_subscriber.language
        assert subscriber_ret['timezone'] == new_subscriber.timezone
        assert subscriber_ret['is_setup'] == new_subscriber.is_setup
        assert subscriber_ret['ftue_level'] == new_subscriber.ftue_level
        assert subscriber_ret['level'] == new_subscriber.level.value

    def test_get_all_subscribers_no_admin(self, with_client):
        # ensure our current subscriber is not admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.post('/subscriber', headers=auth_headers)
        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'

    def test_get_all_subscribers_paginated(self, with_client, with_db, make_pro_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'
        subscribers = {}
        for _ in range(0, 50):
            sub = make_pro_subscriber()
            subscribers[sub.id] = sub

        # Add ourselves to the mix
        with with_db() as db:
            sub = repo.subscriber.get(db, TEST_USER_ID)
            subscribers[sub.id] = sub

        assert len(subscribers) == 51

        # Calculate the amount of pages we'll need
        per_page = 5
        start_page = 1
        total_pages = math.ceil(len(subscribers) / per_page)

        for page in range(start_page, total_pages + 1):  # Inclusive
            response = with_client.post(
                '/subscriber',
                headers=auth_headers,
                json={
                    'page': page,
                    'per_page': per_page,
                },
            )

            assert response.status_code == 200, response.text

            expected_subscribers = per_page if page < total_pages else 1

            data = response.json()
            paginator = data.get('page_meta')
            paged_subscribers = data.get('items')

            assert len(paged_subscribers) == expected_subscribers
            assert paginator
            assert paginator.get('page') == page
            assert paginator.get('per_page') == per_page
            assert paginator.get('count') == expected_subscribers
            assert paginator.get('total_pages') == total_pages

            for _sub in paged_subscribers:
                assert _sub.get('id') in subscribers, f'Failed on page {page}!'
                del subscribers[_sub.get('id')]

        assert len(subscribers) == 0

    def test_get_all_subscribers_paginated_oddly(self, with_client, with_db, make_pro_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'
        subscribers = {}
        for _ in range(0, 37):
            sub = make_pro_subscriber()
            subscribers[sub.id] = sub

        # Add ourselves to the mix
        with with_db() as db:
            sub = repo.subscriber.get(db, TEST_USER_ID)
            subscribers[sub.id] = sub

        assert len(subscribers) == 38

        # Calculate the amount of pages we'll need
        per_page = 6
        start_page = 1
        total_pages = math.ceil(len(subscribers) / per_page)

        for page in range(start_page, total_pages + 1):  # Inclusive
            response = with_client.post(
                '/subscriber',
                headers=auth_headers,
                json={
                    'page': page,
                    'per_page': per_page,
                },
            )

            assert response.status_code == 200, response.text

            expected_subscribers = per_page if page < total_pages else 2  # Left-over

            data = response.json()
            paginator = data.get('page_meta')
            paged_subscribers = data.get('items')

            assert len(paged_subscribers) == expected_subscribers
            assert paginator
            assert paginator.get('page') == page
            assert paginator.get('per_page') == per_page
            assert paginator.get('count') == expected_subscribers
            assert paginator.get('total_pages') == total_pages

            for _sub in paged_subscribers:
                assert _sub.get('id') in subscribers, f'Failed on page {page}!'
                del subscribers[_sub.get('id')]

        assert len(subscribers) == 0

    def test_disable_enable_subscriber(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # make a new subscriber
        new_subscriber = make_basic_subscriber()
        assert new_subscriber.time_deleted is None

        # disable our new subscriber and verify
        response = with_client.put(f'/subscriber/disable/{new_subscriber.id}', headers=auth_headers)

        assert response.status_code == 200, response.text
        response = with_client.post('/subscriber', json={'page': 1}, headers=auth_headers)

        assert response.status_code == 200, response.text
        data = response.json()['items']
        subscriber_ret = data[len(data) - 1]
        assert subscriber_ret['time_deleted'] is not None

        today = today = datetime.today().date()
        date_deleted = datetime.fromisoformat(subscriber_ret['time_deleted']).date()
        assert date_deleted == today

        # attempt to disable same subscriber again, expect fail
        response = with_client.put(f'/subscriber/disable/{new_subscriber.id}', headers=auth_headers)

        assert response.status_code == 400, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_ALREADY_DELETED'

        # now enable the deleted subscriber and verify
        response = with_client.put(f'/subscriber/enable/{new_subscriber.id}', headers=auth_headers)

        assert response.status_code == 200, response.text
        response = with_client.post('/subscriber', json={'page': 1}, headers=auth_headers)

        assert response.status_code == 200, response.text
        data = response.json()['items']
        subscriber_ret = data[len(data) - 1]
        assert subscriber_ret['time_deleted'] is None

        # attempt to enable the same subscriber again, expect fail
        response = with_client.put(f'/subscriber/enable/{new_subscriber.id}', headers=auth_headers)

        assert response.status_code == 400, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_ALREADY_ENABLED'

    def test_disable_subscriber_self_delete_failure(self, with_client):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # disable our current subscriber and verify
        response = with_client.put(f'/subscriber/disable/{TEST_USER_ID}', headers=auth_headers)

        assert response.status_code == 403, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_SELF_DELETE'

    def test_disable_subscriber_not_found(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # disable a subscriber that doesn't exist
        response = with_client.put('/subscriber/disable/999999999999', headers=auth_headers)

        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_NOT_FOUND'

    def test_disable_subscriber_no_admin(self, with_client):
        # ensure our current subscriber is not admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.put(f'/subscriber/disable/{TEST_USER_ID}', headers=auth_headers)

        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'

    def test_enable_subscriber_not_found(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # disable a subscriber that doesn't exist
        response = with_client.put('/subscriber/enable/8888888888888888888', headers=auth_headers)

        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_NOT_FOUND'

    def test_enable_subscriber_no_admin(self, with_client):
        # ensure our current subscriber is not admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.put(f'/subscriber/enable/{TEST_USER_ID}', headers=auth_headers)

        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'

    def test_hard_delete_no_admin(self, with_client):
        # ensure our current subscriber is not admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.put(f'/subscriber/hard-delete/{TEST_USER_ID}', headers=auth_headers)

        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'

    def test_hard_delete_not_disabled_first(self, with_client, make_pro_subscriber):
        # ensure our current subscriber is not admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        hans = make_pro_subscriber()

        response = with_client.put(f'/subscriber/hard-delete/{hans.id}', headers=auth_headers)

        assert response.status_code == 400, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_NOT_DISABLED'

    def test_hard_delete_subscriber(
        self,
        with_client,
        with_db,
        make_pro_subscriber,
        make_caldav_calendar,
        make_schedule,
    ):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # make up a guy
        steve = make_pro_subscriber(name='steve')
        steves_calendar = make_caldav_calendar(subscriber_id=steve.id)
        steves_schedule = make_schedule(calendar_id=steves_calendar.id)

        # disable steves account
        response = with_client.put(f'/subscriber/disable/{steve.id}', headers=auth_headers)

        assert response.status_code == 200, response.json()

        with with_db() as db:
            steve_check = repo.subscriber.get(db, steve.id)
            assert steve_check
            assert steve_check.is_deleted
            assert steve_check.time_deleted

        # hard-delete our current subscriber and verify
        response = with_client.put(f'/subscriber/hard-delete/{steve.id}', headers=auth_headers)

        assert response.status_code == 200, response.json()
        assert response.json() is True

        with with_db() as db:
            steve_check = repo.subscriber.get(db, steve.id)
            assert not steve_check

            steves_calendar = repo.calendar.get(db, steves_calendar.id)
            assert not steves_calendar

            steves_schedule = repo.schedule.get(db, steves_schedule.id)
            assert not steves_schedule
