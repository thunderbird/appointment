from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker

from ..src.database import models
from ..src.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///backend/test/test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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


def test_main():
    response = client.get("/login")
    assert response.status_code == 200, response.text
    assert response.json() == True


def test_create_me():
    response = client.post(
        "/me",
        json={
            "username": "ww",
            "email": "wonderwoman@example.com",
            "name": "Diana",
            "level": "2",
            "timezone": "-1"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "ww"
    assert data["email"] == "wonderwoman@example.com"
    assert data["name"] == "Diana"
    assert data["level"] == 2
    assert data["timezone"] == -1
    assert "id" in data
    assert "calendars" in data


def test_read_me():
    response = client.get("/me")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "admin"
    assert data["email"] == "admin@example.com"
    assert data["name"] == None
    assert data["level"] == 2
    assert data["timezone"] == None
    assert "id" in data
    assert "calendars" in data and isinstance(data["calendars"], list)


def test_update_me():
    response = client.put(
        "/me",
        json={
            "username": "adminx",
            "email": "admin@example.comx",
            "name": "The Admin",
            "level": "3",
            "timezone": "2"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "adminx"
    assert data["email"] == "admin@example.comx"
    assert data["name"] == "The Admin"
    assert data["level"] == 3
    assert data["timezone"] == 2


def test_create_my_calendar():
    response = client.post(
        "/cal",
        json={
            "url": "https://example.com",
            "user": "ww1984",
            "password": "d14n4"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["user"] == "ww1984"
    assert data["password"] == "d14n4"
    assert "id" in data
    assert "owner_id" in data and data["owner_id"] == 1


def test_read_my_calendars():
    response = client.get("/me/calendars")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["user"] == "ww1984"
    assert "owner_id" in data[0] and data[0]["owner_id"] == 1


def test_read_existing_calendar():
    response = client.get("/cal/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["user"] == "ww1984"
    assert data["password"] == "d14n4"


def test_read_missing_calendar():
    response = client.get("/cal/30")
    assert response.status_code == 404, response.text


def test_read_foreign_calendar():
    stmt = insert(models.Calendar).values(owner_id="2", url="https://test.org", user="abc", password="dce")
    db = TestingSessionLocal()
    db.execute(stmt)
    db.commit()
    response = client.get("/cal/2")
    assert response.status_code == 403, response.text


def test_update_existing_calendar():
    response = client.put(
        "/cal/1",
        json={
            "url": "https://example.comx",
            "user": "ww1984x",
            "password": "d14n4x"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["url"] == "https://example.comx"
    assert data["user"] == "ww1984x"
    assert data["password"] == "d14n4x"


def test_update_foreign_calendar():
    response = client.put(
        "/cal/2",
        json={
            "url": "test",
            "user": "test",
            "password": "test"
        }
    )
    assert response.status_code == 403, response.text


def test_delete_existing_calendar():
    response = client.delete("/cal/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["url"] == "https://example.comx"
    assert data["user"] == "ww1984x"
    assert data["password"] == "d14n4x"
    response = client.get("/cal/1")
    assert response.status_code == 404, response.text
    response = client.get("/me/calendars")
    data = response.json()
    assert len(data) == 0
    # add own calendar again for further testing
    client.post("/cal", json={ "url": "https://example.com", "user": "ww1984", "password": "d14n4" })


def test_delete_missing_calendar():
    response = client.delete("/cal/30")
    assert response.status_code == 404, response.text


def test_delete_foreign_calendar():
    response = client.delete("/cal/2")
    assert response.status_code == 403, response.text


def test_create_calendar_appointment():
    response = client.post(
        "/apmt",
        json={
            "appointment": {
                "calendar_id": "3",
                "duration": "180",
                "title": "Testing new Application feature",
                "slug": "lorem-ipsum",
            },
            "slots": [
                { "start": "2022-09-01 09:00:00" },
                { "start": "2022-09-02 09:00:00" },
                { "start": "2022-09-03 09:00:00" },
            ]
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] != None
    assert data["time_updated"] != None
    assert data["calendar_id"] == 3
    assert data["duration"] == 180
    assert data["title"] == "Testing new Application feature"
    assert data["slug"] == "lorem-ipsum"
    assert len(data["slots"]) == 3
    assert data["slots"][2]["start"] == "2022-09-03T09:00:00"


def test_create_missing_calendar_appointment():
    response = client.post(
        "/apmt",
        json={
            "appointment": { "calendar_id": "30", "duration": "1", "title": "a", "slug": "a" },
            "slots": []
        }
    )
    assert response.status_code == 404, response.text


def test_create_foreign_calendar_appointment():
    response = client.post(
        "/apmt",
        json={
            "appointment": { "calendar_id": "2", "duration": "1", "title": "a", "slug": "a" },
            "slots": []
        }
    )
    assert response.status_code == 403, response.text


def test_read_my_appointments():
    response = client.get("/me/appointments")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["duration"] == 180
    assert "calendar_id" in data[0] and data[0]["calendar_id"] == 3


def test_read_existing_appointment():
    response = client.get("/apmt/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] != None
    assert data["time_updated"] != None
    assert data["calendar_id"] == 3
    assert data["duration"] == 180
    assert data["title"] == "Testing new Application feature"
    assert data["slug"] == "lorem-ipsum"
    assert len(data["slots"]) == 3
    assert data["slots"][2]["start"] == "2022-09-03T09:00:00"


def test_read_missing_appointment():
    response = client.get("/apmt/2")
    assert response.status_code == 404, response.text


def test_read_foreign_appointment():
    stmt = insert(models.Appointment).values(calendar_id="2", duration="60", title="abc", slug="dce")
    db = TestingSessionLocal()
    db.execute(stmt)
    db.commit()
    response = client.get("/apmt/2")
    assert response.status_code == 403, response.text


def test_update_existing_appointment():
    response = client.put(
        "/apmt/1",
        json={
            "appointment": {
                "calendar_id": "3",
                "duration": "90",
                "title": "Testing new Application featurex",
                "slug": "lorem-ipsumx",
            },
            "slots": [
                { "start": "2022-09-01 09:00:00" },
                { "start": "2022-09-03 10:00:00" },
                { "start": "2022-09-05 09:00:00" },
            ]
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] != None
    assert data["time_updated"] != None
    assert data["duration"] == 90
    assert data["title"] == "Testing new Application featurex"
    assert data["slug"] == "lorem-ipsumx"
    assert len(data["slots"]) == 3
    assert data["slots"][2]["start"] == "2022-09-05T09:00:00"


def test_update_missing_appointment():
    response = client.put(
        "/apmt/30",
        json={
            "appointment": { "calendar_id": "2", "duration": "90", "title": "a", "slug": "b" },
            "slots": []
        }
    )
    assert response.status_code == 404, response.text


def test_update_foreign_appointment():
    response = client.put(
        "/apmt/2",
        json={
            "appointment": { "calendar_id": "2", "duration": "90", "title": "a", "slug": "b" },
            "slots": []
        }
    )
    assert response.status_code == 403, response.text


def test_delete_existing_appointment():
    response = client.delete("/apmt/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["duration"] == 90
    assert data["title"] == "Testing new Application featurex"
    assert data["slug"] == "lorem-ipsumx"
    response = client.get("/apmt/1")
    assert response.status_code == 404, response.text
    response = client.get("/me/appointments")
    data = response.json()
    assert len(data) == 0
    # add appointment again for further testing
    client.post(
        "/apmt",
        json={
            "appointment": {
                "calendar_id": "3",
                "duration": "90",
                "title": "Testing new Application featurex",
                "slug": "lorem-ipsumx",
            },
            "slots": [
                { "start": "2022-09-01 09:00:00" },
                { "start": "2022-09-03 10:00:00" },
                { "start": "2022-09-05 09:00:00" },
            ]
        }
    )


def test_delete_missing_appointment():
    response = client.delete("/apmt/30")
    assert response.status_code == 404, response.text


def test_delete_foreign_appointment():
    response = client.delete("/apmt/2")
    assert response.status_code == 403, response.text


def test_read_public_existing_appointment():
    response = client.get("/apmt/adminx/lorem-ipsumx")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["time_created"] != None
    assert data["time_updated"] != None
    assert data["calendar_id"] == 3
    assert data["duration"] == 90
    assert data["title"] == "Testing new Application featurex"
    assert data["slug"] == "lorem-ipsumx"
    assert len(data["slots"]) == 3
    assert data["slots"][2]["start"] == "2022-09-05T09:00:00"


def test_read_public_missing_appointment():
    response = client.get("/apmt/adminx/missing")
    assert response.status_code == 404, response.text


def test_attendee_selects_appointment_slot():
    response = client.put(
        "/apmt/adminx/lorem-ipsumx",
        json={
            "slot_id": "2",
            "attendee": {
                "email": "person@test.org",
                "name": "John Doe",
            }
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "person@test.org"
    assert data["name"] == "John Doe"


def test_attendee_selects_unavailable_appointment_slot():
    response = client.put(
        "/apmt/adminx/lorem-ipsumx",
        json={
            "slot_id": "2",
            "attendee": { "email": "a", "name": "b" }
        }
    )
    assert response.status_code == 403, response.text
