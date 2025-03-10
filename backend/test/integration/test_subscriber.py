import os
from datetime import datetime
from defines import auth_headers, TEST_USER_ID
from appointment.database.models import SubscriberLevel


class TestSubscriber:
    def test_get_all_subscribers(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        response = with_client.get(
            '/subscriber', headers=auth_headers
        )

        assert response.status_code == 200, response.text
        data = response.json()
        number_of_subscribers = len(data)
        assert number_of_subscribers > 0

        # verify values
        test_subscriber = data[TEST_USER_ID -1]
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
        response = with_client.get(
            '/subscriber', headers=auth_headers
        )

        assert response.status_code == 200, response.text
        data = response.json()

        # the last subscriber in the returned list is the latest one we created, verify values
        assert len(data) == number_of_subscribers + 1
        subscriber_ret = data[len(data) -1]
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

        response = with_client.get(
            '/subscriber', headers=auth_headers
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'

    def test_disable_enable_subscriber(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # make a new subscriber
        new_subscriber = make_basic_subscriber()
        assert new_subscriber.time_deleted is None

        # disable our new subscriber and verify
        response = with_client.put(
            f'/subscriber/disable/{new_subscriber.email}', headers=auth_headers
        )

        assert response.status_code == 200, response.text
        response = with_client.get(
            '/subscriber', headers=auth_headers
        )

        assert response.status_code == 200, response.text
        data = response.json()
        subscriber_ret = data[len(data) -1]
        assert subscriber_ret['time_deleted'] is not None

        today = today = datetime.today().date()
        date_deleted = datetime.fromisoformat(subscriber_ret['time_deleted']).date()
        assert date_deleted == today

        # attempt to disable same subscriber again, expect fail
        response = with_client.put(
            f'/subscriber/disable/{new_subscriber.email}', headers=auth_headers
        )

        assert response.status_code == 400, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_ALREADY_DELETED'

        # now enable the deleted subscriber and verify
        response = with_client.put(
            f'/subscriber/enable/{new_subscriber.email}', headers=auth_headers
        )

        assert response.status_code == 200, response.text
        response = with_client.get(
            '/subscriber', headers=auth_headers
        )

        assert response.status_code == 200, response.text
        data = response.json()
        subscriber_ret = data[len(data) -1]
        assert subscriber_ret['time_deleted'] is None

        # attempt to enable the same subscriber again, expect fail
        response = with_client.put(
            f'/subscriber/enable/{new_subscriber.email}', headers=auth_headers
        )

        assert response.status_code == 400, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_ALREADY_ENABLED'

    def test_disable_subscriber_self_delete_failure(self, with_client):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # disable our current subscriber and verify
        response = with_client.put(
            f'/subscriber/disable/{os.getenv('TEST_USER_EMAIL')}', headers=auth_headers
        )

        assert response.status_code == 403, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_SELF_DELETE'

    def test_disable_subscriber_not_found(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # disable a subscriber that doesn't exist
        response = with_client.put(
            '/subscriber/disable/this-user-does-not-exist@someemail.com', headers=auth_headers
        )

        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_NOT_FOUND'

    def test_disable_subscriber_no_admin(self, with_client):
        # ensure our current subscriber is not admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.put(
            f'/subscriber/disable/{os.getenv('TEST_USER_EMAIL')}', headers=auth_headers
        )

        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'


    def test_enable_subscriber_not_found(self, with_client, make_basic_subscriber):
        # make our current subscriber admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@example.org'

        # disable a subscriber that doesn't exist
        response = with_client.put(
            '/subscriber/enable/this-user-does-not-exist@someemail.com', headers=auth_headers
        )

        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail']['id'] == 'SUBSCRIBER_NOT_FOUND'


    def test_enable_subscriber_no_admin(self, with_client):
        # ensure our current subscriber is not admin
        os.environ['APP_ADMIN_ALLOW_LIST'] = '@notexample.org'

        response = with_client.put(
            f'/subscriber/enable/{os.getenv('TEST_USER_EMAIL')}', headers=auth_headers
        )

        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail']['id'] == 'INVALID_PERMISSION_LEVEL'
