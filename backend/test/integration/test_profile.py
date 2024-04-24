import os
from defines import auth_headers
from appointment.database import repo


class TestProfile:
    def test_update_me(self, with_db, with_client):
        """Puts to `/me` for a profile update, and verifies that the data was saved in our db correctly"""
        response = with_client.put(
            "/me",
            json={
                "username": "test",
                "name": "Test Account",
                "timezone": "Europe/Berlin",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["username"] == "test"
        assert data["name"] == "Test Account"
        assert data["timezone"] == "Europe/Berlin"

        # Can't test login right now

        # response = client.get("/login", headers=headers)
        # data = response.json()
        # assert data["username"] == "test"
        # assert data["name"] == "Test Account"
        # assert data["timezone"] == "Europe/Berlin"

        # Confirm the data was saved
        with with_db() as db:
            subscriber = repo.subscriber.get_by_email(db, os.getenv('TEST_USER_EMAIL'))
            assert subscriber.username == "test"
            assert subscriber.name == "Test Account"
            assert subscriber.timezone == "Europe/Berlin"

    def test_signed_short_link(self, with_client):
        """Retrieves our unique short link, and ensures it exists"""
        response = with_client.get("/me/signature", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["url"]

    def test_signed_short_link_refresh(self, with_client):
        """Refreshes our unique short link and ensures it's new, and exists"""
        response = with_client.get("/me/signature", headers=auth_headers)
        assert response.status_code == 200, response.text
        url_old = response.json()["url"]
        response = with_client.post("/me/signature", headers=auth_headers)
        assert response.status_code == 200, response.text
        assert response.json()
        response = with_client.get("/me/signature", headers=auth_headers)
        assert response.status_code == 200, response.text
        url_new = response.json()["url"]
        assert url_old != url_new

    def test_signed_short_link_verification(self, with_client):
        """Tests our signed url functionality is working"""
        response = with_client.get("/me/signature", headers=auth_headers)
        assert response.status_code == 200, response.text
        url = response.json()["url"]
        assert url
        response = with_client.post("/verify/signature", json={"url": url})
        assert response.status_code == 200, response.text
        assert response.json()
        response = with_client.post("/verify/signature", json={"url": url + "evil"})
        assert response.status_code == 400, response.text
