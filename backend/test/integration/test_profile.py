import os
from defines import auth_headers
from appointment.database import repo


class TestProfile:
    def test_update_me(self, with_db, with_client):
        """Puts to `/me` for a profile update, and verifies that the data was saved in our db correctly"""
        response = with_client.put(
            '/me',
            json={
                'username': 'test',
                'name': 'Test Account',
                'timezone': 'Europe/Berlin',
                'secondary_email': 'useme@example.org',
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['username'] == 'test'
        assert data['name'] == 'Test Account'
        assert data['timezone'] == 'Europe/Berlin'
        # Response returns preferred_email
        assert data['preferred_email'] == 'useme@example.org'

        # Confirm the data was saved
        with with_db() as db:
            subscriber = repo.subscriber.get_by_email(db, os.getenv('TEST_USER_EMAIL'))
            assert subscriber.username == 'test'
            assert subscriber.name == 'Test Account'
            assert subscriber.timezone == 'Europe/Berlin'
            assert subscriber.secondary_email == 'useme@example.org'
            assert subscriber.preferred_email == 'useme@example.org'

    def test_signed_short_link(self, with_client):
        """Retrieves our unique short link, and ensures it exists"""
        response = with_client.get('/me/signature', headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['url']

    def test_signed_short_link_refresh(self, with_client):
        """Refreshes our unique short link and ensures it's new, and exists"""
        response = with_client.get('/me/signature', headers=auth_headers)
        assert response.status_code == 200, response.text
        url_old = response.json()['url']
        response = with_client.post('/me/signature', headers=auth_headers)
        assert response.status_code == 200, response.text
        assert response.json()
        response = with_client.get('/me/signature', headers=auth_headers)
        assert response.status_code == 200, response.text
        url_new = response.json()['url']
        assert url_old != url_new

    def test_update_me_username_taken(self, with_db, with_client, make_pro_subscriber):
        """Attempt to update current subscriber's profile with already existing username"""
        other_subscriber = make_pro_subscriber(username='thunderbird1')
        assert other_subscriber is not None

        response = with_client.put(
            '/me',
            json={
                'username': 'thunderbird1',
                'name': 'Changed Name',
                'secondary_email': 'adifferentone@example.org',
            },
            headers=auth_headers,
        )
        assert response.status_code == 403, response.text
