import json

from os import getenv as conf
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from http.client import HTTPSConnection
from urllib.parse import quote_plus, urlparse, parse_qs

from ..src.database import models
from ..src.main import app
from ..src.dependencies.database import get_db
from ..src.database.models import CalendarProvider

from ..src.controller.calendar import CalDavConnector

SQLALCHEMY_DATABASE_URL = "sqlite:///test/test.db"

DAY1 = datetime.today().strftime("%Y-%m-%d")
DAY2 = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
DAY3 = (datetime.today() + timedelta(days=2)).strftime("%Y-%m-%d")
DAY4 = (datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")
DAY5 = (datetime.today() + timedelta(days=4)).strftime("%Y-%m-%d")
DAY14 = (datetime.today() + timedelta(days=13)).strftime("%Y-%m-%d")


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# handle subscriber authentication
conn = HTTPSConnection(conf("AUTH0_API_DOMAIN"))
payload = "grant_type=password&username=%s&password=%s&audience=%s&scope=%s&client_id=%s&client_secret=%s" % (
    conf("AUTH0_TEST_USER"),
    conf("AUTH0_TEST_PASS"),
    quote_plus(conf("AUTH0_API_AUDIENCE")),
    quote_plus("read:calendars"),
    conf("AUTH0_API_CLIENT_ID"),
    conf("AUTH0_API_SECRET"),
)
headers = {"content-type": "application/x-www-form-urlencoded"}
conn.request("POST", "/%s/oauth/token" % conf("AUTH0_API_DOMAIN"), payload, headers)

res = conn.getresponse()
data = res.read()
access_token = json.loads(data.decode("utf-8"))["access_token"]
headers = {"authorization": "Bearer %s" % access_token}


""" general tests for configuration and authentication
"""


def test_config():
    assert conf("AUTH0_TEST_USER")
    assert conf("AUTH0_TEST_PASS")
    assert conf("CALDAV_TEST_PRINCIPAL_URL")
    assert conf("CALDAV_TEST_CALENDAR_URL")
    assert conf("CALDAV_TEST_USER")
    assert conf("CALDAV_TEST_PASS")
    assert int(conf("TIER_BASIC_CALENDAR_LIMIT")) == 3
    assert int(conf("TIER_PLUS_CALENDAR_LIMIT")) == 5
    assert int(conf("TIER_PRO_CALENDAR_LIMIT")) == 10


def test_health():
    # existing root route
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()
    # undefined route
    response = client.get("/abcdefg")
    assert response.status_code == 404


def test_access_without_authentication_token():
    response = client.get("/login")
    assert response.status_code == 403
    response = client.put("/me")
    assert response.status_code == 403
    response = client.get("/me/calendars")
    assert response.status_code == 403
    response = client.get("/me/appointments")
    assert response.status_code == 403
    response = client.get("/me/signature")
    assert response.status_code == 403
    response = client.post("/me/signature")
    assert response.status_code == 403
    response = client.post("/cal")
    assert response.status_code == 403
    response = client.get("/cal/1")
    assert response.status_code == 403
    response = client.put("/cal/1")
    assert response.status_code == 403
    response = client.post("/cal/1/connect")
    assert response.status_code == 403
    response = client.delete("/cal/1")
    assert response.status_code == 403
    response = client.post("/rmt/calendars")
    assert response.status_code == 403
    response = client.get("/rmt/cal/1/" + DAY1 + "/" + DAY5)
    assert response.status_code == 403
    response = client.post("/apmt")
    assert response.status_code == 403
    response = client.get("/apmt/1")
    assert response.status_code == 403
    response = client.put("/apmt/1")
    assert response.status_code == 403
    response = client.delete("/apmt/1")
    assert response.status_code == 403
    response = client.post("/rmt/sync")
    assert response.status_code == 403
    response = client.get("/account/download")
    assert response.status_code == 403
    response = client.delete("/account/delete")
    assert response.status_code == 403
    response = client.get("/google/auth")
    assert response.status_code == 403


""" SUBSCRIBERS tests
"""


def test_first_login():
    response = client.get("/login", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == conf("AUTH0_TEST_USER")
    assert data["email"] == conf("AUTH0_TEST_USER")
    assert data["name"] == conf("AUTH0_TEST_USER")
    assert data["level"] == 1
    assert data["timezone"] is None


def test_second_login():
    response = client.get("/login", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == conf("AUTH0_TEST_USER")
    assert data["email"] == conf("AUTH0_TEST_USER")
    assert data["name"] == conf("AUTH0_TEST_USER")
    assert data["level"] == 1
    assert data["timezone"] is None


def test_update_profile_data():
    response = client.put(
        "/me",
        json={
            "username": "test",
            "name": "Test Account",
            "timezone": "Europe/Berlin",
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "test"
    assert data["name"] == "Test Account"
    assert data["timezone"] == "Europe/Berlin"
    response = client.get("/login", headers=headers)
    data = response.json()
    assert data["username"] == "test"
    assert data["name"] == "Test Account"
    assert data["timezone"] == "Europe/Berlin"


def test_signed_short_link():
    response = client.get("/me/signature", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["url"]


def test_signed_short_link_refresh():
    response = client.get("/me/signature", headers=headers)
    assert response.status_code == 200, response.text
    url_old = response.json()["url"]
    response = client.post("/me/signature", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()
    response = client.get("/me/signature", headers=headers)
    assert response.status_code == 200, response.text
    url_new = response.json()["url"]
    assert url_old != url_new


def test_signed_short_link_verification():
    response = client.get("/me/signature", headers=headers)
    assert response.status_code == 200, response.text
    url = response.json()["url"]
    assert url
    response = client.post("/verify/signature", json={"url": url})
    assert response.status_code == 200, response.text
    assert response.json()
    response = client.post("/verify/signature", json={"url": url + "evil"})
    assert response.status_code == 400, response.text


""" CALENDARS tests (CalDAV)
"""


def test_read_remote_caldav_calendars():
    response = client.post(
        "/rmt/calendars",
        json={
            "url": conf("CALDAV_TEST_PRINCIPAL_URL"),
            "user": conf("CALDAV_TEST_USER"),
            "password": conf("CALDAV_TEST_PASS"),
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) > 0
    assert any(c["url"] == conf("CALDAV_TEST_CALENDAR_URL") for c in data)


def test_read_connected_calendars_before_creation():
    response = client.get("/me/calendars", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 0


def test_read_unconnected_calendars_before_creation():
    response = client.get("/me/calendars", params={"only_connected": False}, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 0


def test_create_first_caldav_calendar():
    response = client.post(
        "/cal",
        json={
            "title": "First CalDAV calendar",
            "color": "#123456",
            "provider": CalendarProvider.caldav.value,
            "url": conf("CALDAV_TEST_CALENDAR_URL"),
            "user": conf("CALDAV_TEST_USER"),
            "password": conf("CALDAV_TEST_PASS"),
            "connected": False,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "First CalDAV calendar"
    assert data["color"] == "#123456"
    assert not data["connected"]
    assert "url" not in data
    assert "user" not in data
    assert "password" not in data


def test_read_connected_calendars_after_creation():
    response = client.get("/me/calendars", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 0


def test_read_unconnected_calendars_after_creation():
    response = client.get("/me/calendars", params={"only_connected": False}, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 1
    calendar = data[0]
    assert calendar["title"] == "First CalDAV calendar"
    assert calendar["color"] == "#123456"
    assert not calendar["connected"]
    assert "url" not in calendar
    assert "user" not in calendar
    assert "password" not in calendar


def test_read_existing_caldav_calendar():
    response = client.get("/cal/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "First CalDAV calendar"
    assert data["color"] == "#123456"
    assert data["provider"] == CalendarProvider.caldav.value
    assert data["url"] == conf("CALDAV_TEST_CALENDAR_URL")
    assert data["user"] == conf("CALDAV_TEST_USER")
    assert not data["connected"]
    assert "password" not in data


def test_read_missing_calendar():
    response = client.get("/cal/999", headers=headers)
    assert response.status_code == 404, response.text


def test_read_foreign_calendar():
    query = insert(models.Calendar).values(owner_id="2", title="a", url="a", user="a", password="a", provider="caldav")
    db = TestingSessionLocal()
    db.execute(query)
    db.commit()
    response = client.get("/cal/2", headers=headers)
    assert response.status_code == 403, response.text


def test_update_existing_caldav_calendar_with_password():
    response = client.put(
        "/cal/1",
        json={
            "title": "First modified CalDAV calendar",
            "color": "#234567",
            "url": conf("CALDAV_TEST_CALENDAR_URL") + "x",
            "user": conf("CALDAV_TEST_USER") + "x",
            "password": conf("CALDAV_TEST_PASS") + "x",
            "connected": True,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "First modified CalDAV calendar"
    assert data["color"] == "#234567"
    assert not data["connected"]
    assert "url" not in data
    assert "user" not in data
    assert "password" not in data
    query = select(models.Calendar).where(models.Calendar.id == 1)
    db = TestingSessionLocal()
    cal = db.scalars(query).one()
    assert cal.url == conf("CALDAV_TEST_CALENDAR_URL") + "x"
    assert cal.user == conf("CALDAV_TEST_USER") + "x"
    assert cal.password == conf("CALDAV_TEST_PASS") + "x"


def test_update_existing_caldav_calendar_without_password():
    response = client.put(
        "/cal/1",
        json={
            "title": "First modified CalDAV calendar",
            "color": "#234567",
            "url": conf("CALDAV_TEST_CALENDAR_URL"),
            "user": conf("CALDAV_TEST_USER"),
            "password": "",
            "connected": True,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "First modified CalDAV calendar"
    assert data["color"] == "#234567"
    assert "url" not in data
    assert "user" not in data
    assert "password" not in data
    query = select(models.Calendar).where(models.Calendar.id == 1)
    db = TestingSessionLocal()
    cal = db.scalars(query).one()
    assert cal.url == conf("CALDAV_TEST_CALENDAR_URL")
    assert cal.user == conf("CALDAV_TEST_USER")
    assert cal.password == conf("CALDAV_TEST_PASS") + "x"


def test_update_foreign_calendar():
    response = client.put("/cal/2", json={"title": "b", "url": "b", "user": "b", "password": "b"}, headers=headers)
    assert response.status_code == 403, response.text


def test_connect_caldav_calendar():
    response = client.post("/cal/1/connect", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "First modified CalDAV calendar"
    assert data["color"] == "#234567"
    assert data["connected"]
    assert "url" not in data
    assert "user" not in data
    assert "password" not in data


def test_connect_missing_calendar():
    response = client.post("/cal/999/connect", headers=headers)
    assert response.status_code == 404, response.text


def test_connect_foreign_calendar():
    response = client.post("/cal/2/connect", headers=headers)
    assert response.status_code == 403, response.text


def test_read_connected_calendars_after_connection():
    client.post(
        "/cal",
        json={
            "title": "Second CalDAV calendar",
            "color": "#123456",
            "provider": CalendarProvider.caldav.value,
            "url": "test",
            "user": "test",
            "password": "test",
        },
        headers=headers,
    )
    response = client.get("/me/calendars", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 1
    calendar = data[0]
    assert calendar["title"] == "First modified CalDAV calendar"
    assert calendar["color"] == "#234567"
    assert calendar["connected"]
    assert "url" not in calendar
    assert "user" not in calendar
    assert "password" not in calendar


def test_read_unconnected_calendars_after_connection():
    response = client.get("/me/calendars", params={"only_connected": False}, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 2


def test_delete_existing_calendar():
    response = client.delete("/cal/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "First modified CalDAV calendar"
    assert data["color"] == "#234567"
    assert data["connected"]
    assert "url" not in data
    assert "user" not in data
    assert "password" not in data
    response = client.get("/cal/1", headers=headers)
    assert response.status_code == 404, response.text
    response = client.get("/me/calendars", headers=headers)
    data = response.json()
    assert len(data) == 0
    # add own calendar again for further testing
    client.post(
        "/cal",
        json={
            "title": "First CalDAV calendar",
            "color": "#123456",
            "provider": CalendarProvider.caldav.value,
            "url": conf("CALDAV_TEST_CALENDAR_URL"),
            "user": conf("CALDAV_TEST_USER"),
            "password": conf("CALDAV_TEST_PASS"),
            "connected": True,
        },
        headers=headers,
    )


def test_delete_missing_calendar():
    response = client.delete("/cal/999", headers=headers)
    assert response.status_code == 404, response.text


def test_delete_foreign_calendar():
    response = client.delete("/cal/2", headers=headers)
    assert response.status_code == 403, response.text


def test_connect_more_calendars_than_tier_allows():
    cal = {}
    for i in range(1, int(conf("TIER_BASIC_CALENDAR_LIMIT"))):
        cal[i] = insert(models.Calendar).values(
            owner_id="1",
            title="Calendar" + str(i),
            color="#123456",
            provider="caldav",
            url="a",
            user="a",
            password="a",
            connected=True,
        )
    db = TestingSessionLocal()
    for i in range(1, int(conf("TIER_BASIC_CALENDAR_LIMIT"))):
        db.execute(cal[i])
    db.commit()
    response = client.post("/cal/3/connect", headers=headers)
    assert response.status_code == 403, response.text


""" CALENDARS tests (Google)
"""


def test_google_auth():
    response = client.get("/google/auth?email=" + conf("GOOGLE_TEST_USER"), headers=headers)
    assert response.status_code == 200, response.text
    url = response.json()
    urlobj = urlparse(url)
    params = parse_qs(urlobj.query)
    assert urlobj.scheme == "https"
    assert urlobj.hostname == "accounts.google.com"
    assert params["client_id"][0] == conf("GOOGLE_AUTH_CLIENT_ID")
    assert params["login_hint"][0] == conf("GOOGLE_TEST_USER")


# TODO
# def test_read_remote_google_calendars():
#     response = client.post("/rmt/sync", headers=headers)
#     assert response.status_code == 200, response.text
#     assert response.json()


# TODO
# def test_create_google_calendar():
#     response = client.post(
#         "/cal",
#         json={
#             "title": "First Google calendar",
#             "color": "#123456",
#             "provider": CalendarProvider.google.value,
#             "connected": False,
#         },
#         headers=headers,
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["title"] == "First Google calendar"
#     assert data["color"] == "#123456"
#     assert not data["connected"]


# TODO
# def test_read_existing_google_calendar():
#     response = client.get("/cal/1", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["title"] == "First Google calendar"
#     assert data["color"] == "#123456"
#     assert data["provider"] == CalendarProvider.google.value
#     assert data["url"] == conf("Google_TEST_CALENDAR_URL")
#     assert data["user"] == conf("Google_TEST_USER")
#     assert not data["connected"]
#     assert "password" not in data


# TODO
# def test_connect_google_calendar():
#     response = client.post("/cal/1/connect", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["title"] == "First modified Google calendar"
#     assert data["color"] == "#234567"
#     assert data["connected"]
#     assert "url" not in data
#     assert "user" not in data
#     assert "password" not in data


""" APPOINTMENT tests
"""


def test_create_appointment_on_connected_calendar():
    response = client.post(
        "/apmt",
        json={
            "appointment": {
                "calendar_id": 4,
                "title": "Appointment",
                "duration": 180,
                "location_type": 2,
                "location_name": "Location",
                "location_url": "https://test.org",
                "location_phone": "+123456789",
                "details": "Lorem Ipsum",
                "status": 2,
                "keep_open": True,
            },
            "slots": [
                {"start": DAY1 + " 09:00:00", "duration": 60},
                {"start": DAY2 + " 09:00:00", "duration": 15},
                {"start": DAY3 + " 09:00:00", "duration": 275},
            ],
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
    assert data["title"] == "Appointment"
    assert data["duration"] == 180
    assert data["location_type"] == 2
    assert data["location_name"] == "Location"
    assert data["location_url"] == "https://test.org"
    assert data["location_phone"] == "+123456789"
    assert data["details"] == "Lorem Ipsum"
    assert data["slug"] is not None, len(data["slug"]) > 8
    assert data["status"] == 2
    assert data["keep_open"]
    assert len(data["slots"]) == 3
    assert data["slots"][0]["start"] == DAY1 + "T09:00:00"
    assert data["slots"][0]["duration"] == 60
    assert data["slots"][1]["start"] == DAY2 + "T09:00:00"
    assert data["slots"][1]["duration"] == 15
    assert data["slots"][2]["start"] == DAY3 + "T09:00:00"
    assert data["slots"][2]["duration"] == 275


def test_create_appointment_on_unconnected_calendar():
    response = client.post(
        "/apmt",
        json={
            "appointment": {"calendar_id": 3, "title": "a", "duration": 30},
            "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
        },
        headers=headers,
    )
    assert response.status_code == 403, response.text


def test_create_appointment_on_missing_calendar():
    response = client.post(
        "/apmt",
        json={
            "appointment": {"calendar_id": "999", "title": "a", "duration": 30},
            "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
        },
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_create_appointment_on_foreign_calendar():
    response = client.post(
        "/apmt",
        json={
            "appointment": {"calendar_id": "2", "title": "a", "duration": 30},
            "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
        },
        headers=headers,
    )
    assert response.status_code == 403, response.text


def test_read_appointments():
    response = client.get("/me/appointments", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 1
    data = data[0]
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
    assert data["title"] == "Appointment"
    assert data["duration"] == 180
    assert data["location_type"] == 2
    assert data["location_name"] == "Location"
    assert data["location_url"] == "https://test.org"
    assert data["location_phone"] == "+123456789"
    assert data["details"] == "Lorem Ipsum"
    assert data["slug"] is not None, len(data["slug"]) > 8
    assert data["status"] == 2
    assert data["keep_open"]
    assert len(data["slots"]) == 3
    assert data["slots"][0]["start"] == DAY1 + "T09:00:00"
    assert data["slots"][0]["duration"] == 60
    assert data["slots"][1]["start"] == DAY2 + "T09:00:00"
    assert data["slots"][1]["duration"] == 15
    assert data["slots"][2]["start"] == DAY3 + "T09:00:00"
    assert data["slots"][2]["duration"] == 275


def test_read_existing_appointment():
    response = client.get("/apmt/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
    assert data["title"] == "Appointment"
    assert data["duration"] == 180
    assert data["location_type"] == 2
    assert data["location_name"] == "Location"
    assert data["location_url"] == "https://test.org"
    assert data["location_phone"] == "+123456789"
    assert data["details"] == "Lorem Ipsum"
    assert data["slug"] is not None, len(data["slug"]) > 8
    assert data["status"] == 2
    assert data["keep_open"]
    assert len(data["slots"]) == 3
    assert data["slots"][0]["start"] == DAY1 + "T09:00:00"
    assert data["slots"][0]["duration"] == 60
    assert data["slots"][1]["start"] == DAY2 + "T09:00:00"
    assert data["slots"][1]["duration"] == 15
    assert data["slots"][2]["start"] == DAY3 + "T09:00:00"
    assert data["slots"][2]["duration"] == 275


def test_read_missing_appointment():
    response = client.get("/apmt/999", headers=headers)
    assert response.status_code == 404, response.text


def test_read_foreign_appointment():
    stmt = insert(models.Appointment).values(calendar_id="2", duration="60", title="abc", slug="test")
    db = TestingSessionLocal()
    db.execute(stmt)
    db.commit()
    response = client.get("/apmt/2", headers=headers)
    assert response.status_code == 403, response.text


def test_update_existing_appointment():
    response = client.put(
        "/apmt/1",
        json={
            "appointment": {
                "calendar_id": 4,
                "title": "Appointmentx",
                "duration": 90,
                "location_type": 1,
                "location_name": "Locationx",
                "location_url": "https://testx.org",
                "location_phone": "+1234567890",
                "details": "Lorem Ipsumx",
                "status": 1,
                "keep_open": False,
            },
            "slots": [
                {"start": DAY1 + " 11:00:00", "duration": 30},
                {"start": DAY2 + " 11:00:00", "duration": 30},
                {"start": DAY3 + " 11:00:00", "duration": 30},
            ],
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
    assert data["title"] == "Appointmentx"
    assert data["duration"] == 90
    assert data["location_type"] == 1
    assert data["location_name"] == "Locationx"
    assert data["location_url"] == "https://testx.org"
    assert data["location_phone"] == "+1234567890"
    assert data["details"] == "Lorem Ipsumx"
    assert data["slug"] is not None, len(data["slug"]) > 8
    assert data["status"] == 1
    assert not data["keep_open"]
    assert len(data["slots"]) == 3
    assert data["slots"][0]["start"] == DAY1 + "T11:00:00"
    assert data["slots"][0]["duration"] == 30
    assert data["slots"][1]["start"] == DAY2 + "T11:00:00"
    assert data["slots"][1]["duration"] == 30
    assert data["slots"][2]["start"] == DAY3 + "T11:00:00"
    assert data["slots"][2]["duration"] == 30


def test_update_missing_appointment():
    response = client.put(
        "/apmt/999",
        json={
            "appointment": {"calendar_id": "2", "title": "a", "duration": 30},
            "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
        },
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_update_foreign_appointment():
    response = client.put(
        "/apmt/2",
        json={
            "appointment": {"calendar_id": "2", "title": "a", "duration": 30},
            "slots": [{"start": DAY1 + " 09:00:00", "duration": 30}],
        },
        headers=headers,
    )
    assert response.status_code == 403, response.text


def test_delete_existing_appointment():
    response = client.delete("/apmt/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
    assert data["title"] == "Appointmentx"
    assert data["duration"] == 90
    assert data["location_type"] == 1
    assert data["location_name"] == "Locationx"
    assert data["location_url"] == "https://testx.org"
    assert data["location_phone"] == "+1234567890"
    assert data["details"] == "Lorem Ipsumx"
    assert data["slug"] is not None, len(data["slug"]) > 8
    assert data["status"] == 1
    assert not data["keep_open"]
    assert len(data["slots"]) == 3
    assert data["slots"][0]["start"] == DAY1 + "T11:00:00"
    assert data["slots"][0]["duration"] == 30
    assert data["slots"][1]["start"] == DAY2 + "T11:00:00"
    assert data["slots"][1]["duration"] == 30
    assert data["slots"][2]["start"] == DAY3 + "T11:00:00"
    assert data["slots"][2]["duration"] == 30
    response = client.get("/apmt/1", headers=headers)
    assert response.status_code == 404, response.text
    response = client.get("/me/appointments", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 0
    # add appointment again for further testing
    client.post(
        "/apmt",
        json={
            "appointment": {
                "calendar_id": 4,
                "title": "Appointment",
                "duration": 180,
                "location_type": 2,
                "location_name": "Location",
                "location_url": "https://test.org",
                "location_phone": "+123456789",
                "details": "Lorem Ipsum",
                "status": 2,
                "keep_open": True,
                "slug": "abcdef",
            },
            "slots": [
                {"start": DAY1 + " 09:00:00", "duration": 60},
                {"start": DAY2 + " 09:00:00", "duration": 15},
                {"start": DAY3 + " 09:00:00", "duration": 275},
            ],
        },
        headers=headers,
    )


def test_delete_missing_appointment():
    response = client.delete("/apmt/999", headers=headers)
    assert response.status_code == 404, response.text


def test_delete_foreign_appointment():
    response = client.delete("/apmt/2", headers=headers)
    assert response.status_code == 403, response.text


def test_read_public_existing_appointment():
    response = client.get("/apmt/public/abcdef")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "calendar_id" not in data
    assert "status" not in data
    assert data["title"] == "Appointment"
    assert data["details"] == "Lorem Ipsum"
    assert data["slug"] == "abcdef"
    assert data["owner_name"] == "Test Account"
    assert len(data["slots"]) == 3
    assert data["slots"][0]["start"] == DAY1 + "T09:00:00"
    assert data["slots"][0]["duration"] == 60
    assert data["slots"][1]["start"] == DAY2 + "T09:00:00"
    assert data["slots"][1]["duration"] == 15
    assert data["slots"][2]["start"] == DAY3 + "T09:00:00"
    assert data["slots"][2]["duration"] == 275


def test_read_public_missing_appointment():
    response = client.get("/apmt/public/missing")
    assert response.status_code == 404, response.text


def test_attendee_selects_appointment_slot():
    response = client.put(
        "/apmt/public/abcdef",
        json={
            "slot_id": 1,
            "attendee": {
                "email": "person@test.org",
                "name": "John Doe",
            },
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["slot_id"] == 1
    assert data["attendee"]["email"] == "person@test.org"
    assert data["attendee"]["name"] == "John Doe"


def test_read_public_appointment_after_attendee_selection():
    response = client.get("/apmt/public/abcdef")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["slots"]) == 3
    assert data["slots"][0]["attendee_id"] == 1


def test_attendee_selects_slot_of_unavailable_appointment():
    response = client.put(
        "/apmt/public/abcdef",
        json={"slot_id": 1, "attendee": {"email": "a", "name": "b"}},
    )
    assert response.status_code == 403, response.text


def test_attendee_selects_slot_of_missing_appointment():
    response = client.put(
        "/apmt/public/missing",
        json={"slot_id": 1, "attendee": {"email": "a", "name": "b"}},
    )
    assert response.status_code == 404, response.text


def test_attendee_selects_missing_slot_of_existing_appointment():
    response = client.put(
        "/apmt/public/abcdef",
        json={"slot_id": 999, "attendee": {"email": "a", "name": "b"}},
    )
    assert response.status_code == 404, response.text


def test_attendee_provides_invalid_email_address():
    response = client.put(
        "/apmt/public/abcdef",
        json={"slot_id": 2, "attendee": {"email": "a", "name": "b"}},
    )
    assert response.status_code == 400, response.text


def test_get_remote_caldav_events():
    response = client.get("/rmt/cal/4/" + DAY1 + "/" + DAY3, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Appointment"
    assert data[0]["start"][:19] == DAY1 + " 09:00:00"
    assert data[0]["end"][:19] == DAY1 + " 10:00:00"
    # delete event again to prevent calendar pollution
    con = CalDavConnector(conf("CALDAV_TEST_CALENDAR_URL"), conf("CALDAV_TEST_USER"), conf("CALDAV_TEST_PASS"))
    n = con.delete_events(start=DAY1)
    assert n == 1


""" SCHEDULE tests
"""


def test_create_schedule_on_connected_calendar():
    response = client.post(
        "/schedule",
        json={
            "calendar_id": 4,
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
            "weekdays": json.dumps([1, 2, 3, 4, 5]),
            "slot_duration": 30,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
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
    weekdays = json.loads(data["weekdays"])
    assert len(weekdays) == 5
    assert weekdays == [1, 2, 3, 4, 5]
    assert data["slot_duration"] == 30


def test_create_schedule_on_unconnected_calendar():
    response = client.post(
        "/schedule",
        json={"calendar_id": 3, "name": "Schedule"},
        headers=headers,
    )
    assert response.status_code == 403, response.text


def test_create_schedule_on_missing_calendar():
    response = client.post(
        "/schedule",
        json={"calendar_id": 999, "name": "Schedule"},
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_create_schedule_on_foreign_calendar():
    response = client.post(
        "/schedule",
        json={"calendar_id": 2, "name": "Schedule"},
        headers=headers,
    )
    assert response.status_code == 403, response.text


def test_read_schedules():
    response = client.get("/schedule", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert len(data) == 1
    data = data[0]
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
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
    weekdays = json.loads(data["weekdays"])
    assert len(weekdays) == 5
    assert weekdays == [1, 2, 3, 4, 5]
    assert data["slot_duration"] == 30


def test_read_existing_schedule():
    response = client.get("/schedule/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
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
    weekdays = json.loads(data["weekdays"])
    assert len(weekdays) == 5
    assert weekdays == [1, 2, 3, 4, 5]
    assert data["slot_duration"] == 30


def test_read_missing_schedule():
    response = client.get("/schedule/999", headers=headers)
    assert response.status_code == 404, response.text


def test_read_foreign_schedule():
    stmt = insert(models.Schedule).values(calendar_id=2, name="abc")
    db = TestingSessionLocal()
    db.execute(stmt)
    db.commit()
    response = client.get("/schedule/2", headers=headers)
    assert response.status_code == 403, response.text


def test_update_existing_schedule():
    response = client.put(
        "/schedule/1",
        json={
            "calendar_id": 4,
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
            "weekdays": json.dumps([2, 4, 6]),
            "slot_duration": 60,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] is not None
    assert data["time_updated"] is not None
    assert data["calendar_id"] == 4
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
    weekdays = json.loads(data["weekdays"])
    assert len(weekdays) == 3
    assert weekdays == [2, 4, 6]
    assert data["slot_duration"] == 60


def test_update_missing_schedule():
    response = client.put(
        "/schedule/999",
        json={"calendar_id": 1, "name": "Schedule"},
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_update_foreign_schedule():
    response = client.put(
        "/schedule/2",
        json={"calendar_id": 2, "name": "Schedule"},
        headers=headers,
    )
    assert response.status_code == 403, response.text


""" MISCELLANEOUS tests
"""


def test_get_invitation_ics_file():
    response = client.get("/serve/ics/abcdef/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "invite"
    assert data["content_type"] == "text/calendar"
    assert "data" in data


def test_get_invitation_ics_file_for_missing_appointment():
    response = client.get("/serve/ics/missing/1")
    assert response.status_code == 404, response.text


def test_get_invitation_ics_file_for_missing_slot():
    response = client.get("/serve/ics/abcdef/999")
    assert response.status_code == 404, response.text
