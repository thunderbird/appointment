import json

from os import getenv as conf
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from datetime import date
from http.client import HTTPSConnection
from urllib.parse import quote_plus

from ..src.database import models
from ..src.main import app
from ..src.dependencies.database import get_db
from ..src.database.models import CalendarProvider

# from ..src.controller.calendar import CalDavConnector

SQLALCHEMY_DATABASE_URL = "sqlite:///test/test.db"
# TODO: setup dedicated testing CalDAV server
# TESTING_CALDAV_PRINCIPAL = "https://calendar.robur.coop/principals/"
# TESTING_CALDAV_CALENDAR = "https://calendar.robur.coop/calendars/mozilla/"
# TESTING_CALDAV_USER = "mozilla"
# TESTING_CALDAV_PASS = "thunderbird"

YYYYMM = str(date.today())[:-3]

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

# handle authentication
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
    response = client.get("/rmt/cal/1/" + YYYYMM + "-09/" + YYYYMM + "-11")
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


""" TODO: The following tests are old test cases from an earlier version of the application
          and need to be updated to work with the current authentication flow
"""


# def test_create_calendar_appointment():
#     response = client.post(
#         "/apmt",
#         json={
#             "appointment": {
#                 "calendar_id": 5,
#                 "title": "Testing new Application feature",
#                 "duration": 180,
#                 "location_type": 2,
#                 "location_url": "https://test.com",
#                 "details": "Lorem Ipsum",
#                 "status": 2,
#             },
#             "slots": [
#                 {"start": YYYYMM + "-01 09:00:00", "duration": 60},
#                 {"start": YYYYMM + "-02 09:00:00", "duration": 15},
#                 {"start": YYYYMM + "-03 09:00:00", "duration": 275},
#             ],
#         },
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["time_created"] is not None
#     assert data["time_updated"] is not None
#     assert data["calendar_id"] == 5
#     assert data["title"] == "Testing new Application feature"
#     assert data["duration"] == 180
#     assert data["location_type"] == 2
#     assert data["location_url"] == "https://test.com"
#     assert data["details"] == "Lorem Ipsum"
#     assert len(data["slug"]) > 8
#     assert data["keep_open"]
#     assert data["status"] == 2
#     assert len(data["slots"]) == 3
#     assert data["slots"][2]["start"] == YYYYMM + "-03T09:00:00"
#     assert data["slots"][2]["duration"] == 275


# def test_create_another_calendar_appointment():
#     response = client.post(
#         "/apmt",
#         json={
#             "appointment": {
#                 "calendar_id": 5,
#                 "title": "Testing again",
#                 "location_type": 1,
#                 "status": 2,
#             },
#             "slots": [
#                 {"start": YYYYMM + "-04 09:00:00", "duration": 120},
#             ],
#         },
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["time_created"] is not None
#     assert data["time_updated"] is not None
#     assert data["calendar_id"] == 5
#     assert data["title"] == "Testing again"
#     assert data["location_type"] == 1
#     assert len(data["slug"]) > 8
#     assert data["status"] == 2
#     assert len(data["slots"]) == 1
#     assert data["slots"][0]["start"] == YYYYMM + "-04T09:00:00"
#     assert data["slots"][0]["duration"] == 120


# def test_create_missing_calendar_appointment():
#     response = client.post(
#         "/apmt",
#         json={
#             "appointment": {"calendar_id": "30", "duration": "1", "title": "a"},
#             "slots": [],
#         },
#     )
#     assert response.status_code == 404, response.text


# def test_create_foreign_calendar_appointment():
#     response = client.post(
#         "/apmt",
#         json={
#             "appointment": {"calendar_id": "2", "duration": "1", "title": "a"},
#             "slots": [],
#         },
#     )
#     assert response.status_code == 403, response.text


# def test_read_my_appointments():
#     response = client.get("/me/appointments")
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) == 2
#     assert data[0]["duration"] == 180
#     assert "calendar_id" in data[0] and data[0]["calendar_id"] == 5


# def test_read_existing_appointment():
#     response = client.get("/apmt/1")
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["time_created"] is not None
#     assert data["time_updated"] is not None
#     assert data["calendar_id"] == 5
#     assert data["duration"] == 180
#     assert data["title"] == "Testing new Application feature"
#     assert data["keep_open"]
#     assert len(data["slots"]) == 3
#     assert data["slots"][2]["start"] == YYYYMM + "-03T09:00:00"
#     assert data["slots"][2]["duration"] == 275


# def test_read_missing_appointment():
#     response = client.get("/apmt/30")
#     assert response.status_code == 404, response.text


# def test_read_foreign_appointment():
#     stmt = insert(models.Appointment).values(
#         calendar_id="2",
#         duration="60",
#         title="abc",
#         slug="58fe9784f60a42bcaa94eb8f1a7e5c17",
#     )
#     db = TestingSessionLocal()
#     db.execute(stmt)
#     db.commit()
#     response = client.get("/apmt/3")
#     assert response.status_code == 403, response.text


# def test_update_existing_appointment():
#     response = client.put(
#         "/apmt/1",
#         json={
#             "appointment": {
#                 "calendar_id": "5",
#                 "duration": "90",
#                 "title": "Testing new Application featurex",
#                 "keep_open": "false",
#             },
#             "slots": [
#                 {"start": YYYYMM + "-01 09:00:00", "duration": 60},
#                 {"start": YYYYMM + "-03 10:00:00", "duration": 25},
#                 {"start": YYYYMM + "-05 09:00:00", "duration": 375},
#             ],
#         },
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["time_created"] is not None
#     assert data["time_updated"] is not None
#     assert data["duration"] == 90
#     assert data["title"] == "Testing new Application featurex"
#     assert not data["keep_open"]
#     assert len(data["slots"]) == 3
#     assert data["slots"][2]["start"] == YYYYMM + "-05T09:00:00"
#     assert data["slots"][2]["duration"] == 375


# def test_update_missing_appointment():
#     response = client.put(
#         "/apmt/30",
#         json={
#             "appointment": {"calendar_id": "2", "duration": "90", "title": "a"},
#             "slots": [],
#         },
#     )
#     assert response.status_code == 404, response.text


# def test_update_foreign_appointment():
#     response = client.put(
#         "/apmt/3",
#         json={
#             "appointment": {"calendar_id": "2", "duration": "90", "title": "a"},
#             "slots": [],
#         },
#     )
#     assert response.status_code == 403, response.text


# def test_delete_existing_appointment():
#     # response = client.delete("/apmt/1")
#     # assert response.status_code == 200, response.text
#     # data = response.json()
#     # assert data["duration"] == 90
#     # assert data["title"] == "Testing new Application featurex"
#     # response = client.get("/apmt/1")
#     # assert response.status_code == 404, response.text
#     # response = client.get("/me/appointments")
#     # data = response.json()
#     # assert len(data) == 1
#     # add appointment again for further testing
#     client.post(
#         "/apmt",
#         json={
#             "appointment": {
#                 "calendar_id": "5",
#                 "duration": "90",
#                 "title": "Testing new Application featurex",
#                 "status": 2,
#             },
#             "slots": [
#                 {"start": YYYYMM + "-01 09:00:00", "duration": 60},
#                 {"start": YYYYMM + "-03 10:00:00", "duration": 25},
#                 {"start": YYYYMM + "-05 09:00:00", "duration": 375},
#             ],
#         },
#     )


# def test_delete_missing_appointment():
#     response = client.delete("/apmt/30")
#     assert response.status_code == 404, response.text


# def test_delete_foreign_appointment():
#     response = client.delete("/apmt/3")
#     assert response.status_code == 403, response.text


# def test_read_public_existing_appointment():
#     slug = client.get("/apmt/4").json()["slug"]
#     response = client.get("/apmt/adminx/" + slug)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert "calendar_id" not in data
#     assert "status" not in data
#     assert data["title"] == "Testing new Application featurex"
#     assert data["owner_name"] == "The Admin"
#     assert len(data["slots"]) == 3
#     assert data["slots"][2]["start"] == YYYYMM + "-05T09:00:00"
#     assert data["slots"][2]["duration"] == 375


# def test_read_public_missing_appointment():
#     response = client.get("/apmt/adminx/missing")
#     assert response.status_code == 404, response.text


# def test_attendee_selects_appointment_slot():
#     slug = client.get("/apmt/4").json()["slug"]
#     response = client.put(
#         "/apmt/adminx/" + slug,
#         json={
#             "slot_id": "9",
#             "attendee": {
#                 "email": "person@test.org",
#                 "name": "John Doe",
#             },
#         },
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["email"] == "person@test.org"
#     assert data["name"] == "John Doe"


# def test_attendee_selects_unavailable_appointment_slot():
#     slug = client.get("/apmt/4").json()["slug"]
#     response = client.put(
#         "/apmt/adminx/" + slug,
#         json={"slot_id": "9", "attendee": {"email": "a", "name": "b"}},
#     )
#     assert response.status_code == 403, response.text


# def test_get_remote_events():
#     response = client.get("/rmt/cal/5/" + YYYYMM + "-09/" + YYYYMM + "-11")
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["title"] == "Testing new Application featurex"
#     assert data[0]["start"] == YYYYMM + "-03 09:00:00"
#     assert data[0]["end"] == YYYYMM + "-03 11:00:00"
#     # delete event again to prevent calendar pollution
#     con = CalDavConnector(TESTING_CALDAV_CALENDAR, TESTING_CALDAV_USER, TESTING_CALDAV_PASS)
#     n = con.delete_events(start=YYYYMM + "-10")
#     assert n == 1
