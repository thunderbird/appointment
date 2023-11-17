import logging
import os
import secrets

import validators
from requests import HTTPError
from sentry_sdk import capture_exception
from sqlalchemy.exc import SQLAlchemyError

# database
from sqlalchemy.orm import Session

from ..controller.mailer import ZoomMeetingFailedMail
from ..database import repo, schemas

# authentication
from ..controller.calendar import CalDavConnector, Tools, GoogleConnector

from fastapi import APIRouter, Depends, HTTPException, Security, Body
from fastapi_auth0 import Auth0User
from datetime import timedelta, timezone
from ..controller.apis.google_client import GoogleClient
from ..controller.auth import signed_url_by_subscriber
from ..database.models import Subscriber, CalendarProvider, MeetingLinkProviderType, ExternalConnectionType
from ..dependencies.google import get_google_client
from ..dependencies.auth import get_subscriber, auth
from ..dependencies.database import get_db
from ..dependencies.zoom import get_zoom_client

router = APIRouter()


@router.get("/")
def health():
    """Small route with no processing that will be used for health checks"""
    return True


@router.get("/login", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.SubscriberBase)
def login(db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
    """endpoint to check frontend authed user and create user if not existing yet"""
    me = auth.persist_user(db, user)
    if not me:
        raise HTTPException(status_code=403, detail="User credentials mismatch")
    return schemas.SubscriberBase(
        username=me.username, email=me.email, name=me.name, level=me.level, timezone=me.timezone
    )


@router.put("/me", response_model=schemas.SubscriberBase)
def update_me(
    data: schemas.SubscriberIn, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)
):
    """endpoint to update data of authenticated subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if subscriber.username != data.username and repo.get_subscriber_by_username(db, data.username):
        raise HTTPException(status_code=403, detail="Username not available")
    me = repo.update_subscriber(db=db, data=data, subscriber_id=subscriber.id)
    return schemas.SubscriberBase(
        username=me.username, email=me.email, name=me.name, level=me.level, timezone=me.timezone
    )


@router.get("/me/calendars", response_model=list[schemas.CalendarOut])
def read_my_calendars(
    db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber), only_connected: bool = True
):
    """get all calendar connections of authenticated subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    calendars = repo.get_calendars_by_subscriber(
        db, subscriber_id=subscriber.id, include_unconnected=not only_connected
    )
    return [schemas.CalendarOut(id=c.id, title=c.title, color=c.color, connected=c.connected) for c in calendars]


@router.get("/me/appointments", response_model=list[schemas.Appointment])
def read_my_appointments(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """get all appointments of authenticated subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    appointments = repo.get_appointments_by_subscriber(db, subscriber_id=subscriber.id)
    return appointments


@router.get("/me/signature")
def get_my_signature(subscriber: Subscriber = Depends(get_subscriber)):
    """Retrieve a subscriber's signed short link"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    return {"url": signed_url_by_subscriber(subscriber)}


@router.post("/me/signature")
def refresh_signature(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Refresh a subscriber's signed short link"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")

    repo.update_subscriber(
        db,
        schemas.SubscriberAuth(
            email=subscriber.email, username=subscriber.username, short_link_hash=secrets.token_hex(32)
        ),
        subscriber.id,
    )

    return True


@router.post("/verify/signature")
def verify_signature(url: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Verify a signed short link"""
    if repo.verify_subscriber_link(db, url):
        return True
    raise HTTPException(400, "Invalid link")


@router.post("/cal", response_model=schemas.CalendarOut)
def create_my_calendar(
    calendar: schemas.CalendarConnection,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to add a new calendar connection for authenticated subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    # create calendar
    try:
        cal = repo.create_subscriber_calendar(db=db, calendar=calendar, subscriber_id=subscriber.id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.get("/cal/{id}", response_model=schemas.CalendarConnectionOut)
def read_my_calendar(id: int, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to get a calendar from db"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    cal = repo.get_calendar(db, calendar_id=id)
    if cal is None:
        raise HTTPException(status_code=404, detail="Calendar not found")
    if not repo.calendar_is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
    return schemas.CalendarConnectionOut(
        id=cal.id,
        title=cal.title,
        color=cal.color,
        provider=cal.provider,
        url=cal.url,
        user=cal.user,
        connected=cal.connected,
    )


@router.put("/cal/{id}", response_model=schemas.CalendarOut)
def update_my_calendar(
    id: int,
    calendar: schemas.CalendarConnection,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if not repo.calendar_exists(db, calendar_id=id):
        raise HTTPException(status_code=404, detail="Calendar not found")
    if not repo.calendar_is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
    cal = repo.update_subscriber_calendar(db=db, calendar=calendar, calendar_id=id)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.post("/cal/{id}/connect", response_model=schemas.CalendarOut)
def connect_my_calendar(
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if not repo.calendar_exists(db, calendar_id=id):
        raise HTTPException(status_code=404, detail="Calendar not found")
    if not repo.calendar_is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
    try:
        cal = repo.update_subscriber_calendar_connection(db=db, calendar_id=id, is_connected=True)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.delete("/cal/{id}", response_model=schemas.CalendarOut)
def delete_my_calendar(id: int, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to remove a calendar from db"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if not repo.calendar_exists(db, calendar_id=id):
        raise HTTPException(status_code=404, detail="Calendar not found")
    if not repo.calendar_is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
    cal = repo.delete_subscriber_calendar(db=db, calendar_id=id)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.post("/rmt/calendars", response_model=list[schemas.CalendarConnectionOut])
def read_remote_calendars(
    connection: schemas.CalendarConnection,
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to get calendars from a remote CalDAV server"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if connection.provider == CalendarProvider.google:
        con = GoogleConnector(
            db=None,
            google_client=google_client,
            calendar_id=connection.user,
            subscriber_id=subscriber.id,
            google_tkn=subscriber.google_tkn,
        )
    else:
        con = CalDavConnector(connection.url, connection.user, connection.password)
    return con.list_calendars()


@router.post("/rmt/sync")
def sync_remote_calendars(
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to sync calendars from a remote server"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    # Create a list of connections and loop through them with sync
    # TODO: Also handle CalDAV connections
    connections = [
        GoogleConnector(
            db=db,
            google_client=google_client,
            calendar_id=None,
            subscriber_id=subscriber.id,
            google_tkn=subscriber.google_tkn,
        ),
    ]
    for connection in connections:
        error_occurred = connection.sync_calendars()
        # And then redirect back to frontend
        if error_occurred:
            raise HTTPException(500, "An error occurred while syncing calendars. Please try again later.")
    return True


@router.get("/rmt/cal/{id}/{start}/{end}", response_model=list[schemas.Event])
def read_remote_events(
    id: int,
    start: str,
    end: str,
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to get events in a given date range from a remote calendar"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    db_calendar = repo.get_calendar(db, calendar_id=id)
    if db_calendar is None:
        raise HTTPException(status_code=404, detail="Calendar not found")
    if db_calendar.provider == CalendarProvider.google:
        con = GoogleConnector(
            db=db,
            google_client=google_client,
            calendar_id=db_calendar.user,
            subscriber_id=subscriber.id,
            google_tkn=subscriber.google_tkn,
        )
    else:
        con = CalDavConnector(db_calendar.url, db_calendar.user, db_calendar.password)
    events = con.list_events(start, end)
    for e in events:
        e.calendar_title = db_calendar.title
        e.calendar_color = db_calendar.color
    return events


@router.post("/apmt", response_model=schemas.Appointment)
def create_my_calendar_appointment(
    a_s: schemas.AppointmentSlots, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)
):
    """endpoint to add a new appointment with slots for a given calendar"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if not repo.calendar_exists(db, calendar_id=a_s.appointment.calendar_id):
        raise HTTPException(status_code=404, detail="Calendar not found")
    if not repo.calendar_is_owned(db, calendar_id=a_s.appointment.calendar_id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
    if not repo.calendar_is_connected(db, calendar_id=a_s.appointment.calendar_id):
        raise HTTPException(status_code=403, detail="Calendar connection is not active")
    if a_s.appointment.meeting_link_provider == MeetingLinkProviderType.zoom and subscriber.get_external_connection(ExternalConnectionType.zoom) is None:
        raise HTTPException(status_code=400, detail="You need a connected Zoom account in order to create a meeting link")
    return repo.create_calendar_appointment(db=db, appointment=a_s.appointment, slots=a_s.slots)


@router.get("/apmt/{id}", response_model=schemas.Appointment)
def read_my_appointment(id: str, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to get an appointment from db by id"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    db_appointment = repo.get_appointment(db, appointment_id=id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if not repo.appointment_is_owned(db, appointment_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Appointment not owned by subscriber")
    return db_appointment


@router.put("/apmt/{id}", response_model=schemas.Appointment)
def update_my_appointment(
    id: int,
    a_s: schemas.AppointmentSlots,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing appointment with slots"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    db_appointment = repo.get_appointment(db, appointment_id=id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if not repo.appointment_is_owned(db, appointment_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Appointment not owned by subscriber")
    return repo.update_calendar_appointment(db=db, appointment=a_s.appointment, slots=a_s.slots, appointment_id=id)


@router.delete("/apmt/{id}", response_model=schemas.Appointment)
def delete_my_appointment(id: int, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to remove an appointment from db"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    db_appointment = repo.get_appointment(db, appointment_id=id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if not repo.appointment_is_owned(db, appointment_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Appointment not owned by subscriber")
    return repo.delete_calendar_appointment(db=db, appointment_id=id)


@router.get("/apmt/public/{slug}", response_model=schemas.AppointmentOut)
def read_public_appointment(slug: str, db: Session = Depends(get_db)):
    """endpoint to retrieve an appointment from db via public link and only expose necessary data"""
    a = repo.get_public_appointment(db, slug=slug)
    if a is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    s = repo.get_subscriber_by_appointment(db=db, appointment_id=a.id)
    if s is None:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    slots = [
        schemas.SlotOut(id=sl.id, start=sl.start, duration=sl.duration, attendee_id=sl.attendee_id) for sl in a.slots
    ]
    return schemas.AppointmentOut(
        id=a.id, title=a.title, details=a.details, slug=a.slug, owner_name=s.name, slots=slots
    )


@router.put("/apmt/public/{slug}", response_model=schemas.SlotAttendee)
def update_public_appointment_slot(
    slug: str,
    s_a: schemas.SlotAttendee,
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to update a time slot for an appointment via public link and create an event in remote calendar"""
    db_appointment = repo.get_public_appointment(db, slug=slug)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db_calendar = repo.get_calendar(db, calendar_id=db_appointment.calendar_id)
    if db_calendar is None:
        raise HTTPException(status_code=404, detail="Calendar not found")
    if not repo.appointment_has_slot(db, appointment_id=db_appointment.id, slot_id=s_a.slot_id):
        raise HTTPException(status_code=404, detail="Time slot not found for Appointment")
    if not repo.slot_is_available(db, slot_id=s_a.slot_id):
        raise HTTPException(status_code=403, detail="Time slot not available anymore")
    if not validators.email(s_a.attendee.email):
        raise HTTPException(status_code=400, detail="No valid email provided")

    slot = repo.get_slot(db=db, slot_id=s_a.slot_id)

    # grab the subscriber
    organizer = repo.get_subscriber_by_appointment(db=db, appointment_id=db_appointment.id)

    location_url = db_appointment.location_url

    if db_appointment.meeting_link_provider == MeetingLinkProviderType.zoom:
        try:
            zoom_client = get_zoom_client(organizer)
            response = zoom_client.create_meeting(db_appointment.title, slot.start.isoformat(), slot.duration, organizer.timezone)
            if 'id' in response:
                slot.meeting_link_url = zoom_client.get_meeting(response['id'])['join_url']
                slot.meeting_link_id = response['id']

                location_url = slot.meeting_link_url

                # TODO: If we move to a model-based db functions replace this with a .save()
                # Save the updated slot information
                db.add(slot)
                db.commit()
        except HTTPError as err:  # Not fatal, just a bummer
            logging.error("Zoom meeting creation error: ", err)

            # Ensure sentry captures the error too!
            if os.getenv('SENTRY_DSN') != '':
                capture_exception(err)

            # Notify the organizer that the meeting link could not be created!
            mail = ZoomMeetingFailedMail(to=organizer.email, appointment_title=db_appointment.title)
            mail.send()
        except SQLAlchemyError as err:  # Not fatal, but could make things tricky
            logging.error("Failed to save the zoom meeting link to the appointment: ", err)
            if os.getenv('SENTRY_DSN') != '':
                capture_exception(err)

    event = schemas.Event(
        title=db_appointment.title,
        start=slot.start.replace(tzinfo=timezone.utc).isoformat(),
        end=(slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration)).isoformat(),
        description=db_appointment.details,
        location=schemas.EventLocation(
            type=db_appointment.location_type,
            suggestions=db_appointment.location_suggestions,
            selected=db_appointment.location_selected,
            name=db_appointment.location_name,
            url=location_url,
            phone=db_appointment.location_phone,
        ),
    )

    # create remote event
    if db_calendar.provider == CalendarProvider.google:
        con = GoogleConnector(
            db=db,
            google_client=google_client,
            calendar_id=db_calendar.user,
            subscriber_id=organizer.id,
            google_tkn=organizer.google_tkn,
        )
    else:
        con = CalDavConnector(db_calendar.url, db_calendar.user, db_calendar.password)
    con.create_event(event=event, attendee=s_a.attendee, organizer=organizer)

    # update appointment slot data
    repo.update_slot(db=db, slot_id=s_a.slot_id, attendee=s_a.attendee)

    # send mail with .ics attachment to attendee
    Tools().send_vevent(db_appointment, slot, organizer, s_a.attendee)

    return schemas.SlotAttendee(slot_id=s_a.slot_id, attendee=s_a.attendee)


@router.get("/apmt/serve/ics/{slug}/{slot_id}", response_model=schemas.FileDownload)
def public_appointment_serve_ics(slug: str, slot_id: int, db: Session = Depends(get_db)):
    """endpoint to serve ICS file for time slot to download"""
    db_appointment = repo.get_public_appointment(db, slug=slug)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if not repo.appointment_has_slot(db, appointment_id=db_appointment.id, slot_id=slot_id):
        raise HTTPException(status_code=404, detail="Time slot not found for Appointment")
    slot = repo.get_slot(db=db, slot_id=slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Time slot not found")
    organizer = repo.get_subscriber_by_appointment(db=db, appointment_id=db_appointment.id)

    return schemas.FileDownload(
        name="invite",
        content_type="text/calendar",
        data=Tools().create_vevent(appointment=db_appointment, slot=slot, organizer=organizer).decode("utf-8"),
    )
