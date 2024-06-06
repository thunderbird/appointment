import os
from defines import DAY1, DAY5, auth_headers


class TestGeneral:
    def test_config(self):
        assert int(os.getenv("TIER_BASIC_CALENDAR_LIMIT")) == 3
        assert int(os.getenv("TIER_PLUS_CALENDAR_LIMIT")) == 5
        assert int(os.getenv("TIER_PRO_CALENDAR_LIMIT")) == 10
        assert os.getenv("TEST_USER_EMAIL") is not None

    def test_health(self, with_client):
        # existing root route
        response = with_client.get("/")
        assert response.status_code == 200
        assert response.json()
        # undefined route
        response = with_client.get("/abcdefg")
        assert response.status_code == 404

    def test_health_for_locale(self, with_client):
        # Try english first
        response = with_client.get("/", headers={"accept-language": "en"})
        assert response.status_code == 200
        assert response.json() == "Health OK"

        # Try german next
        response = with_client.get("/", headers={"accept-language": "de"})
        assert response.status_code == 200
        assert response.json() == "Betriebsbereit"

    def test_access_without_authentication_token(self, with_client):
        # response = client.get("/login")
        # assert response.status_code == 401
        response = with_client.put("/me")
        assert response.status_code == 401
        response = with_client.get("/me/calendars")
        assert response.status_code == 401
        response = with_client.get("/me/appointments")
        assert response.status_code == 401
        response = with_client.get("/me/signature")
        assert response.status_code == 401
        response = with_client.post("/me/signature")
        assert response.status_code == 401
        response = with_client.post("/cal")
        assert response.status_code == 401
        response = with_client.get("/cal/1")
        assert response.status_code == 401
        response = with_client.put("/cal/1")
        assert response.status_code == 401
        response = with_client.post("/cal/1/connect")
        assert response.status_code == 401
        response = with_client.delete("/cal/1")
        assert response.status_code == 401
        response = with_client.post("/rmt/calendars")
        assert response.status_code == 401
        response = with_client.get("/rmt/cal/1/" + DAY1 + "/" + DAY5)
        assert response.status_code == 401
        response = with_client.post("/apmt")
        assert response.status_code == 401
        response = with_client.get("/apmt/1")
        assert response.status_code == 401
        response = with_client.put("/apmt/1")
        assert response.status_code == 401
        response = with_client.delete("/apmt/1")
        assert response.status_code == 401
        response = with_client.post("/rmt/sync")
        assert response.status_code == 401
        response = with_client.get("/account/download")
        assert response.status_code == 401
        response = with_client.delete("/account/delete")
        assert response.status_code == 401
        response = with_client.get("/google/auth")
        assert response.status_code == 401

    def test_send_feedback(self, with_client):
        response = with_client.post(
            "/support", json={"topic": "Hello World", "details": "Hello World but longer"}, headers=auth_headers
        )
        assert response.status_code == 200
