import os

from dotenv import load_dotenv, find_dotenv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import Request
from defines import TEST_USER_ID, TEST_CALDAV_URL, TEST_CALDAV_USER

# Factory functions
from factory.attendee_factory import make_attendee  # noqa: F401
from factory.appointment_factory import make_appointment  # noqa: F401
from factory.calendar_factory import make_caldav_calendar  # noqa: F401
from factory.slot_factory import make_appointment_slot  # noqa: F401
from factory.subscriber_factory import make_subscriber, make_basic_subscriber, make_pro_subscriber  # noqa: F401

# Load our env
load_dotenv(find_dotenv(".env.test"))

from backend.src.appointment.main import server  # noqa: E402
from backend.src.appointment.database import models, repo, schemas  # noqa: E402
from backend.src.appointment.dependencies import database, auth, google  # noqa: E402


def _patch_caldav_connector(monkeypatch):
    """Standard function to patch caldav connector"""
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
                    url=TEST_CALDAV_URL,
                    user=TEST_CALDAV_USER
                )
            ]

        @staticmethod
        def create_event(self, event, attendee, organizer):
            return True

        @staticmethod
        def delete_event(self, start):
            return True

    # Patch up the caldav constructor, and list_calendars
    from backend.src.appointment.controller.calendar import CalDavConnector
    monkeypatch.setattr(CalDavConnector, "__init__", MockCaldavConnector.__init__)
    monkeypatch.setattr(CalDavConnector, "list_calendars", MockCaldavConnector.list_calendars)
    monkeypatch.setattr(CalDavConnector, "create_event", MockCaldavConnector.create_event)
    monkeypatch.setattr(CalDavConnector, "delete_events", MockCaldavConnector.delete_event)


def _patch_mailer(monkeypatch):
    """Mocks the base mailer class to not send mail"""
    class MockMailer:
        @staticmethod
        def send(self):
            return

    from backend.src.appointment.controller.mailer import Mailer
    monkeypatch.setattr(Mailer, "send", MockMailer.send)


@pytest.fixture()
def with_db():
    engine = create_engine(os.getenv("DATABASE_URL"), connect_args={"check_same_thread": False}, poolclass=StaticPool)
    testing_local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    # Ensure we have a default subscriber
    with testing_local_session() as db:
        subscriber = models.Subscriber(
            username=os.getenv('TEST_USER_EMAIL'),
            email=os.getenv('TEST_USER_EMAIL'),
            name="Test Account",
            level=models.SubscriberLevel.pro
        )
        db.add(subscriber)
        db.commit()

        # We should re-work this later
        assert subscriber.id == TEST_USER_ID

    yield testing_local_session

    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def with_client(with_db, monkeypatch):
    def override_get_db():
        db = with_db()
        try:
            yield db
        finally:
            db.close()

    def override_get_subscriber(request : Request):
        from fastapi import HTTPException

        if 'authorization' not in request.headers:
            raise HTTPException(403, detail='Missing bearer token')

        return repo.get_subscriber_by_email(with_db(), os.getenv('TEST_USER_EMAIL'))

    def override_get_google_client():
        return None

    # Patch caldav connector
    _patch_caldav_connector(monkeypatch)
    _patch_mailer(monkeypatch)

    app = server()

    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[auth.get_subscriber] = override_get_subscriber
    app.dependency_overrides[google.get_google_client] = override_get_google_client

    client = TestClient(app)

    yield client
