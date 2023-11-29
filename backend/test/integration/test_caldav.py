import os

from backend.src.appointment.database.models import CalendarProvider
from backend.src.appointment.controller.calendar import CalDavConnector
from backend.src.appointment.database import schemas, models, repo

from sqlalchemy import insert, select

from defines import auth_headers, TEST_USER_ID


class TestCaldav:
    def test_read_remote_caldav_calendars(self, monkeypatch, with_client):
        test_url = "https://caldav.thunderbird.net/"
        test_user = "thunderbird"

        # Create a mock caldav connector
        class MockCaldavConnector:
            @staticmethod
            def __init__(self, url, user, password):
                """We don't want to initialize a client"""
                pass

            @staticmethod
            def list_calendars(self):
                return [
                    schemas.CalendarConnectionOut(
                        url=test_url,
                        user=test_user
                    )
                ]

        # Patch up the caldav constructor, and list_calendars
        monkeypatch.setattr(CalDavConnector, "__init__", MockCaldavConnector.__init__)
        monkeypatch.setattr(CalDavConnector, "list_calendars", MockCaldavConnector.list_calendars)

        response = with_client.post(
            "/rmt/calendars",
            json={
                "url": test_url,
                "user": test_user,
                "password": "caw",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) > 0
        assert any(c["url"] == test_url for c in data)

    def test_read_connected_calendars_before_creation(self, with_client):
        response = with_client.get("/me/calendars", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 0

    def test_read_unconnected_calendars_before_creation(self, with_client):
        response = with_client.get("/me/calendars", params={"only_connected": False}, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 0

    def test_create_first_caldav_calendar(self, with_client):
        response = with_client.post(
            "/cal",
            json={
                "title": "First CalDAV calendar",
                "color": "#123456",
                "provider": CalendarProvider.caldav.value,
                "url": os.getenv("CALDAV_TEST_CALENDAR_URL"),
                "user": os.getenv("CALDAV_TEST_USER"),
                "password": os.getenv("CALDAV_TEST_PASS"),
                "connected": False,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "First CalDAV calendar"
        assert data["color"] == "#123456"
        assert not data["connected"]
        assert "url" not in data
        assert "user" not in data
        assert "password" not in data

    def test_read_connected_calendars_after_creation(self, with_client, make_caldav_calendar):
        """Get /me/calendars and ensure the list is 0 (as it only returns connected calendars by default)"""
        make_caldav_calendar()

        response = with_client.get("/me/calendars", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 0

    def test_read_unconnected_calendars_after_creation(self, with_client, make_caldav_calendar):
        """Get /me/calendars and ensure the list is 1 (as we're explicitly asking for unconnected calendars too)"""
        generated_calendar = make_caldav_calendar()

        response = with_client.get("/me/calendars", params={"only_connected": False}, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 1
        calendar = data[0]
        assert calendar["title"] == generated_calendar.title
        assert calendar["color"] == generated_calendar.color
        assert not calendar["connected"]
        assert "url" not in calendar
        assert "user" not in calendar
        assert "password" not in calendar

    def test_read_existing_caldav_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar()

        response = with_client.get("/cal/1", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == generated_calendar.title
        assert data["color"] == generated_calendar.color
        assert data["provider"] == CalendarProvider.caldav.value
        assert data["url"] == generated_calendar.url
        assert data["user"] == generated_calendar.user
        assert not data["connected"]
        assert "password" not in data

    def test_read_missing_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar()

        # Intentionally read the wrong calendar id
        response = with_client.get(f"/cal/{generated_calendar.id + 1}", headers=auth_headers)
        assert response.status_code == 404, response.text

    def test_read_foreign_calendar(self, with_client, make_caldav_calendar, make_pro_subscriber):
        """Ensure we can't read other peoples calendars"""
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)

        response = with_client.get(f"/cal/{generated_calendar.id}", headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_update_existing_caldav_calendar_with_password(self, with_client, with_db, make_caldav_calendar):
        generated_calendar = make_caldav_calendar()

        response = with_client.put(
            f"/cal/{generated_calendar.id}",
            json={
                "title": "First modified CalDAV calendar",
                "color": "#234567",
                "url": os.getenv("CALDAV_TEST_CALENDAR_URL") + "x",
                "user": os.getenv("CALDAV_TEST_USER") + "x",
                "password": os.getenv("CALDAV_TEST_PASS") + "x",
                "connected": True,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()

        assert data["title"] == "First modified CalDAV calendar"
        assert data["color"] == "#234567"
        assert not data["connected"]
        assert "url" not in data
        assert "user" not in data
        assert "password" not in data

        query = select(models.Calendar).where(models.Calendar.id == generated_calendar.id)

        with with_db() as db:
            cal = db.scalars(query).one()

        assert cal.url == os.getenv("CALDAV_TEST_CALENDAR_URL") + "x"
        assert cal.user == os.getenv("CALDAV_TEST_USER") + "x"
        assert cal.password == os.getenv("CALDAV_TEST_PASS") + "x"

    def test_update_existing_caldav_calendar_without_password(self, with_client, with_db, make_caldav_calendar):
        """Ensure if we put a blank password into the request that the calendar will update with an empty password."""
        generated_calendar = make_caldav_calendar(password='')

        response = with_client.put(
            f"/cal/{generated_calendar.id}",
            json={
                "title": "First modified CalDAV calendar",
                "color": "#234567",
                "url": os.getenv("CALDAV_TEST_CALENDAR_URL"),
                "user": os.getenv("CALDAV_TEST_USER"),
                "password": "",
                "connected": True,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "First modified CalDAV calendar"
        assert data["color"] == "#234567"
        assert "url" not in data
        assert "user" not in data
        assert "password" not in data

        query = select(models.Calendar).where(models.Calendar.id == generated_calendar.id)

        with with_db() as db:
            cal = db.scalars(query).one()

        assert cal.url == os.getenv("CALDAV_TEST_CALENDAR_URL")
        assert cal.user == os.getenv("CALDAV_TEST_USER")
        assert cal.password == ''

    def test_update_foreign_calendar(self, with_client, make_caldav_calendar, make_pro_subscriber):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)

        response = with_client.put(f"/cal/{generated_calendar.id}", json={"title": "b", "url": "b", "user": "b", "password": "b"}, headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_connect_caldav_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar()

        assert generated_calendar.connected is False

        response = with_client.post(f"/cal/{generated_calendar.id}/connect", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == generated_calendar.title
        assert data["color"] == generated_calendar.color
        assert data["connected"]
        assert "url" not in data
        assert "user" not in data
        assert "password" not in data

    def test_connect_missing_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar()

        # Intentionally use the wrong calendar id
        response = with_client.post(f"/cal/{generated_calendar.id + 1}/connect", headers=auth_headers)
        assert response.status_code == 404, response.text

    def test_connect_foreign_calendar(self, with_client, make_caldav_calendar, make_pro_subscriber):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)

        response = with_client.post(f"/cal/{generated_calendar.id}/connect", headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_read_connected_calendars_after_connection(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar(connected=True)

        with_client.post(
            "/cal",
            json={
                "title": "Second CalDAV calendar",
                "color": "#123456",
                "provider": CalendarProvider.caldav.value,
                "url": "test",
                "user": "test",
                "password": "test",
            },
            headers=auth_headers,
        )
        response = with_client.get("/me/calendars", headers=auth_headers)
        assert response.status_code == 200, response.text

        data = response.json()
        assert type(data) is list
        assert len(data) == 1

        calendar = data[0]
        assert calendar["title"] == generated_calendar.title
        assert calendar["color"] == generated_calendar.color
        assert calendar["connected"]
        assert "url" not in calendar
        assert "user" not in calendar
        assert "password" not in calendar

    def test_read_unconnected_calendars_after_connection(self, with_client, make_caldav_calendar):
        make_caldav_calendar(connected=True)
        make_caldav_calendar(connected=False)

        response = with_client.get("/me/calendars", params={"only_connected": False}, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) is list
        assert len(data) == 2

    def test_delete_existing_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar(connected=True)

        response = with_client.delete(f"/cal/{generated_calendar.id}", headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == generated_calendar.title
        assert data["color"] == generated_calendar.color
        assert data["connected"]
        assert "url" not in data
        assert "user" not in data
        assert "password" not in data

        response = with_client.get(f"/cal/{generated_calendar.id}", headers=auth_headers)
        assert response.status_code == 404, response.text

        response = with_client.get("/me/calendars", headers=auth_headers)
        data = response.json()
        assert len(data) == 0


    def test_delete_missing_calendar(self, with_client, make_caldav_calendar):
        generated_calendar = make_caldav_calendar()

        # Intentionally call the wrong id
        response = with_client.delete(f"/cal/{generated_calendar.id + 1}", headers=auth_headers)
        assert response.status_code == 404, response.text

    def test_delete_foreign_calendar(self, with_client, make_caldav_calendar, make_pro_subscriber):
        the_other_guy = make_pro_subscriber()
        generated_calendar = make_caldav_calendar(the_other_guy.id)

        response = with_client.delete(f"/cal/{generated_calendar.id}", headers=auth_headers)
        assert response.status_code == 403, response.text

    def test_connect_more_calendars_than_tier_allows(self, with_client, with_db, make_caldav_calendar, make_basic_subscriber):
        basic_user = make_basic_subscriber()

        cal = {}
        for i in range(1, int(os.getenv("TIER_BASIC_CALENDAR_LIMIT"))):
            cal[i] = make_caldav_calendar(basic_user.id, connected=True)

        response = with_client.post(f"/cal/{cal[2].id}/connect", headers=auth_headers)
        assert response.status_code == 403, response.text
