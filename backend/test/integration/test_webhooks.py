import os

import pytest
from appointment.database import models, repo
from appointment.database.models import ExternalConnectionType


class TestZoomWebhooks:
    @pytest.fixture
    def setup_deauthorization(self, make_pro_subscriber, make_external_connections):
        zoom_user_id = 'z9jkdsfsdfjhdkfjQ'

        request_body = {
            'event': 'app_deauthorized',
            'payload': {
                'account_id': 'EabCDEFghiLHMA',
                'user_id': zoom_user_id,
                'signature': '827edc3452044f0bc86bdd5684afb7d1e6becfa1a767f24df1b287853cf73000',
                'deauthorization_time': '2019-06-17T13:52:28.632Z',
                'client_id': 'ADZ9k9bTWmGUoUbECUKU_a',
            },
        }

        zoom_signature = 'v0=cc6857f5b05fea4fb0f2057912c14a68996cfcf36a4267c65f15a3e9f1602477'
        zoom_timestamp = '2019-06-17T13:52:28.632Z'
        request_headers = {'x-zm-signature': zoom_signature, 'x-zm-request-timestamp': zoom_timestamp}

        fake_secret = 'cake'
        os.environ['ZOOM_API_SECRET'] = fake_secret

        subscriber = make_pro_subscriber()
        external_connection = make_external_connections(
            subscriber_id=subscriber.id, type=models.ExternalConnectionType.zoom.value, type_id=zoom_user_id
        )

        return request_body, request_headers, subscriber, external_connection

    def test_deauthorization(self, with_client, with_db, setup_deauthorization):
        """Test a successful deauthorization (i.e. deleting the zoom connection)"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization
        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            zoom_user_id = external_connection.type_id

            response = with_client.post('/webhooks/zoom-deauthorization', json=request_body, headers=request_headers)
            assert response.status_code == 200, response.text

            db.refresh(subscriber)
            external_connection = repo.external_connection.get_by_type(
                db, subscriber.id, type=ExternalConnectionType.zoom, type_id=zoom_user_id
            )

            assert subscriber
            assert not external_connection

    def test_deauthorization_silent_fail_due_to_no_connection(self, with_client, with_db, setup_deauthorization):
        """Test that a missing zoom connection doesn't crash the webhook"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization

        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            # Remove our external connection
            db.delete(external_connection)
            db.commit()

            response = with_client.post('/webhooks/zoom-deauthorization', json=request_body, headers=request_headers)
            assert response.status_code == 200, response.text

    def test_deauthorization_silent_fail_due_to_no_user(self, with_client, with_db, setup_deauthorization):
        """Test that a missing subscriber doesn't crash the webhook"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization

        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            # Remove our external connection AND subscriber
            db.delete(external_connection)
            db.delete(subscriber)
            db.commit()

            response = with_client.post('/webhooks/zoom-deauthorization', json=request_body, headers=request_headers)
            assert response.status_code == 200, response.text

    def test_deauthorization_with_invalid_webhook(self, with_client, with_db):
        """Test that an invalid request doesn't crash the webhook"""
        response = with_client.post(
            '/webhooks/zoom-deauthorization',
            json={'event': 'im-a-fake-event-woo!'},
        )
        assert response.status_code == 200, response.text

    def test_deauthorization_with_invalid_webhook_headers(self, with_client, with_db, setup_deauthorization):
        """Test that a valid response body with invalid headers doesn't remove the connection"""
        request_body, request_headers, subscriber, external_connection = setup_deauthorization

        with with_db() as db:
            assert subscriber
            assert external_connection

            db.add(subscriber)
            db.add(external_connection)

            response = with_client.post(
                '/webhooks/zoom-deauthorization',
                json=request_body,
                headers={'x-zm-signature': 'bad-signature', 'x-zm-signature-timestamp': 'bad-timestamp'},
            )
            assert response.status_code == 200, response.text

            # Ensure that our connection still exists
            db.refresh(subscriber)
            db.refresh(external_connection)

            assert subscriber
            assert external_connection
