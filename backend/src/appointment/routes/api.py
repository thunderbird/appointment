import logging
import os
import secrets
from typing import Annotated

import requests.exceptions
import validators
from redis import Redis, RedisCluster
from requests import HTTPError
from sentry_sdk import capture_exception
from sqlalchemy.exc import SQLAlchemyError

# database
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from .. import utils
from ..database import repo, schemas

# authentication
from ..controller.calendar import CalDavConnector, Tools, GoogleConnector
from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks, Query, Request
from datetime import timedelta, timezone
from ..controller.apis.google_client import GoogleClient
from ..controller.auth import signed_url_by_subscriber
from ..database.models import Subscriber, CalendarProvider, MeetingLinkProviderType, ExternalConnectionType
from ..dependencies.google import get_google_client
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db, get_redis
from ..dependencies.zoom import get_zoom_client
from ..exceptions import validation
from ..exceptions.validation import RemoteCalendarConnectionError, APIException
from ..l10n import l10n
from ..tasks.emails import send_zoom_meeting_failed_email, send_support_email

router = APIRouter()


@router.get("/")
def health():
    """Small route with no processing that will be used for health checks"""
    return l10n('health-ok')


@router.put("/me", response_model=schemas.SubscriberBase)
def update_me(
    data: schemas.SubscriberIn, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)
):
    """endpoint to update data of authenticated subscriber"""
    if subscriber.username != data.username and repo.subscriber.get_by_username(db, data.username):
        raise HTTPException(status_code=403, detail=l10n('username-not-available'))

    me = repo.subscriber.update(db=db, data=data, subscriber_id=subscriber.id)
    return schemas.SubscriberBase(
        username=me.username, email=me.email, name=me.name, level=me.level, timezone=me.timezone
    )


@router.get("/me/calendars", response_model=list[schemas.CalendarOut])
def read_my_calendars(
    db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber), only_connected: bool = True
):
    """get all calendar connections of authenticated subscriber"""
    calendars = repo.calendar.get_by_subscriber(
        db, subscriber_id=subscriber.id, include_unconnected=not only_connected
    )
    return [schemas.CalendarOut(id=c.id, title=c.title, color=c.color, connected=c.connected) for c in calendars]


@router.get("/me/appointments", response_model=list[schemas.AppointmentWithCalendarOut])
def read_my_appointments(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """get all appointments of authenticated subscriber"""
    appointments = repo.appointment.get_by_subscriber(db, subscriber_id=subscriber.id)
    # Mix in calendar title and color.
    # Note because we `__dict__` any relationship values won't be carried over, so don't forget to manually add those!
    appointments = map(
        lambda x: schemas.AppointmentWithCalendarOut(**x.__dict__, slots=x.slots, calendar_title=x.calendar.title,
                                                     calendar_color=x.calendar.color), appointments)
    return appointments


@router.get("/me/signature")
def get_my_signature(subscriber: Subscriber = Depends(get_subscriber)):
    """Retrieve a subscriber's signed short link"""
    return {"url": signed_url_by_subscriber(subscriber)}


@router.post("/me/signature")
def refresh_signature(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Refresh a subscriber's signed short link"""
    repo.subscriber.update(
        db,
        schemas.SubscriberAuth(
            email=subscriber.email, username=subscriber.username, short_link_hash=secrets.token_hex(32)
        ),
        subscriber.id,
    )

    return True


@router.post("/verify/signature", deprecated=True)
def verify_signature(url: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Verify a signed short link"""
    if repo.subscriber.verify_link(db, url):
        return True

    raise validation.InvalidLinkException()


@router.post("/cal", response_model=schemas.CalendarOut)
def create_my_calendar(
    calendar: schemas.CalendarConnection,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to add a new calendar connection for authenticated subscriber"""

    # Test the connection first
    if calendar.provider == CalendarProvider.google:
        external_connection = utils.list_first(repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google))

        if external_connection is None or external_connection.token is None:
            raise RemoteCalendarConnectionError()

        # I don't believe google cal touches this route, but just in case!
        con = GoogleConnector(
            db=db,
            redis_instance=None,
            google_client=google_client,
            remote_calendar_id=calendar.user,
            calendar_id=None,
            subscriber_id=subscriber.id,
            google_tkn=external_connection.token,
        )
    else:
        con = CalDavConnector(
            redis_instance=None,
            url=calendar.url,
            user=calendar.user,
            password=calendar.password,
            subscriber_id=subscriber.id,
            calendar_id=None,
        )

    # Make sure we can connect to the calendar before we save it
    if not con.test_connection():
        raise RemoteCalendarConnectionError()

    # create calendar
    try:
        cal = repo.calendar.create(db=db, calendar=calendar, subscriber_id=subscriber.id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.get("/cal/{id}", response_model=schemas.CalendarConnectionOut)
def read_my_calendar(id: int, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to get a calendar from db"""
    cal = repo.calendar.get(db, calendar_id=id)

    if cal is None:
        raise validation.CalendarNotFoundException()
    if not repo.calendar.is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()

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
    if not repo.calendar.exists(db, calendar_id=id):
        raise validation.CalendarNotFoundException()
    if not repo.calendar.is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()

    cal = repo.calendar.update(db=db, calendar=calendar, calendar_id=id)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.post("/cal/{id}/connect", response_model=schemas.CalendarOut)
@router.post("/cal/{id}/disconnect", response_model=schemas.CalendarOut)
def change_my_calendar_connection(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing calendar connection for authenticated subscriber
    note this function handles both disconnect and connect (the double route is not a typo.)"""
    if not repo.calendar.exists(db, calendar_id=id):
        raise validation.CalendarNotFoundException()
    if not repo.calendar.is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()

    # If our path ends with /connect then connect the calendar, otherwise disconnect the calendar
    connect = request.scope.get('path', '').endswith('/connect')

    try:
        cal = repo.calendar.update_connection(db=db, calendar_id=id, is_connected=connect)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.delete("/cal/{id}", response_model=schemas.CalendarOut)
def delete_my_calendar(id: int, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to remove a calendar from db"""
    if not repo.calendar.exists(db, calendar_id=id):
        raise validation.CalendarNotFoundException()
    if not repo.calendar.is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()

    cal = repo.calendar.delete(db=db, calendar_id=id)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.post("/rmt/calendars", response_model=list[schemas.CalendarConnectionOut])
def read_remote_calendars(
    connection: schemas.CalendarConnection,
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
    db: Session = Depends(get_db),
):
    """endpoint to get calendars from a remote CalDAV server"""
    if connection.provider == CalendarProvider.google:
        external_connection = utils.list_first(repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google))

        if external_connection is None or external_connection.token is None:
            raise RemoteCalendarConnectionError()

        con = GoogleConnector(
            db=None,
            redis_instance=None,
            google_client=google_client,
            remote_calendar_id=connection.user,
            subscriber_id=subscriber.id,
            calendar_id=None,
            google_tkn=external_connection.token,
        )
    else:
        con = CalDavConnector(
            redis_instance=None,
            url=connection.url,
            user=connection.user,
            password=connection.password,
            subscriber_id=subscriber.id,
            calendar_id=None,
        )

    try:
        calendars = con.list_calendars()
    except requests.exceptions.RequestException:
        raise RemoteCalendarConnectionError()

    return calendars


@router.post("/rmt/sync")
def sync_remote_calendars(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to sync calendars from a remote server"""
    # Create a list of connections and loop through them with sync
    # TODO: Also handle CalDAV connections

    external_connection = utils.list_first(
        repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google))

    if external_connection is None or external_connection.token is None:
        raise RemoteCalendarConnectionError()

    connections = [
        GoogleConnector(
            db=db,
            redis_instance=redis,
            google_client=google_client,
            remote_calendar_id=None,
            calendar_id=None,
            subscriber_id=subscriber.id,
            google_tkn=external_connection.token,
        ),
    ]
    for connection in connections:
        error_occurred = connection.sync_calendars()
        # And then redirect back to frontend
        if error_occurred:
            raise HTTPException(500, l10n('calendar-sync-fail'))
    return True


@router.get("/rmt/cal/{id}/{start}/{end}", response_model=list[schemas.Event])
def read_remote_events(
    id: int,
    start: str,
    end: str,
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
    redis_instance: Redis | RedisCluster | None = Depends(get_redis),
):
    """endpoint to get events in a given date range from a remote calendar"""
    db_calendar = repo.calendar.get(db, calendar_id=id)

    if db_calendar is None:
        raise validation.CalendarNotFoundException()

    if db_calendar.provider == CalendarProvider.google:
        external_connection = utils.list_first(repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google))

        if external_connection is None or external_connection.token is None:
            raise RemoteCalendarConnectionError()

        con = GoogleConnector(
            db=db,
            redis_instance=redis_instance,
            google_client=google_client,
            remote_calendar_id=db_calendar.user,
            calendar_id=db_calendar.id,
            subscriber_id=subscriber.id,
            google_tkn=external_connection.token,
        )
    else:
        con = CalDavConnector(
            redis_instance=redis_instance,
            url=db_calendar.url,
            user=db_calendar.user,
            password=db_calendar.password,
            subscriber_id=subscriber.id,
            calendar_id=db_calendar.id,
        )

    try:
        events = con.list_events(start, end)
    except requests.exceptions.RequestException:
        raise RemoteCalendarConnectionError()

    for e in events:
        e.calendar_title = db_calendar.title
        e.calendar_color = db_calendar.color
    return events


@router.post("/apmt", response_model=schemas.Appointment, deprecated=True)
def create_my_calendar_appointment(
    a_s: schemas.AppointmentSlots, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)
):
    """endpoint to add a new appointment with slots for a given calendar"""
    if not repo.calendar.exists(db, calendar_id=a_s.appointment.calendar_id):
        raise validation.CalendarNotFoundException()
    if not repo.calendar.is_owned(db, calendar_id=a_s.appointment.calendar_id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()
    if not repo.calendar.is_connected(db, calendar_id=a_s.appointment.calendar_id):
        raise validation.CalendarNotConnectedException()
    if a_s.appointment.meeting_link_provider == MeetingLinkProviderType.zoom and subscriber.get_external_connection(ExternalConnectionType.zoom) is None:
        raise validation.ZoomNotConnectedException()
    return repo.appointment.create(db=db, appointment=a_s.appointment, slots=a_s.slots)


@router.get("/apmt/{id}", response_model=schemas.Appointment, deprecated=True)
def read_my_appointment(id: str, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to get an appointment from db by id"""
    db_appointment = repo.appointment.get(db, appointment_id=id)

    if db_appointment is None:
        raise validation.AppointmentNotFoundException()
    if not repo.appointment.is_owned(db, appointment_id=id, subscriber_id=subscriber.id):
        raise validation.AppointmentNotAuthorizedException()

    return db_appointment


@router.put("/apmt/{id}", response_model=schemas.Appointment, deprecated=True)
def update_my_appointment(
    id: int,
    a_s: schemas.AppointmentSlots,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing appointment with slots"""
    db_appointment = repo.appointment.get(db, appointment_id=id)

    if db_appointment is None:
        raise validation.AppointmentNotFoundException()
    if not repo.appointment.is_owned(db, appointment_id=id, subscriber_id=subscriber.id):
        raise validation.AppointmentNotAuthorizedException()

    return repo.appointment.update(db=db, appointment=a_s.appointment, slots=a_s.slots, appointment_id=id)


@router.delete("/apmt/{id}", response_model=schemas.Appointment, deprecated=True)
def delete_my_appointment(id: int, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to remove an appointment from db"""
    db_appointment = repo.appointment.get(db, appointment_id=id)

    if db_appointment is None:
        raise validation.AppointmentNotFoundException()
    if not repo.appointment.is_owned(db, appointment_id=id, subscriber_id=subscriber.id):
        raise validation.AppointmentNotAuthorizedException()

    return repo.appointment.delete(db=db, appointment_id=id)


@router.get("/apmt/public/{slug}", response_model=schemas.AppointmentOut, deprecated=True)
def read_public_appointment(slug: str, db: Session = Depends(get_db)):
    """endpoint to retrieve an appointment from db via public link and only expose necessary data"""
    a = repo.appointment.get_public(db, slug=slug)
    if a is None:
        raise validation.AppointmentNotFoundException()
    s = repo.subscriber.get_by_appointment(db=db, appointment_id=a.id)
    if s is None:
        raise validation.SubscriberNotFoundException()
    slots = [
        schemas.SlotOut(id=sl.id, start=sl.start, duration=sl.duration, attendee_id=sl.attendee_id) for sl in a.slots
    ]
    return schemas.AppointmentOut(
        id=a.id, title=a.title, details=a.details, slug=a.slug, owner_name=s.name, slots=slots, slot_duration=slots[0].duration if len(slots) > 0 else 0
    )


@router.put("/apmt/public/{slug}", response_model=schemas.SlotAttendee, deprecated=True)
def update_public_appointment_slot(
    slug: str,
    s_a: schemas.SlotAttendee,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to update a time slot for an appointment via public link and create an event in remote calendar"""
    db_appointment = repo.appointment.get_public(db, slug=slug)
    if db_appointment is None:
        raise validation.AppointmentNotFoundException()
    db_calendar = repo.calendar.get(db, calendar_id=db_appointment.calendar_id)
    if db_calendar is None:
        raise validation.CalendarNotFoundException()
    if not repo.appointment.has_slot(db, appointment_id=db_appointment.id, slot_id=s_a.slot_id):
        raise validation.SlotNotFoundException()
    if not repo.slot.is_available(db, slot_id=s_a.slot_id):
        raise validation.SlotAlreadyTakenException()
    if not validators.email(s_a.attendee.email):
        raise HTTPException(status_code=400, detail=l10n('slot-invalid-email'))

    slot = repo.slot.get(db=db, slot_id=s_a.slot_id)

    # grab the subscriber
    organizer = repo.subscriber.get_by_appointment(db=db, appointment_id=db_appointment.id)

    location_url = db_appointment.location_url

    if db_appointment.meeting_link_provider == MeetingLinkProviderType.zoom:
        try:
            zoom_client = get_zoom_client(organizer)
            response = zoom_client.create_meeting(db_appointment.title, slot.start.isoformat(), slot.duration,
                                                  organizer.timezone)
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
            background_tasks.add_task(send_zoom_meeting_failed_email, to=organizer.email,
                                      appointment=db_appointment.title)

        except SQLAlchemyError as err:  # Not fatal, but could make things tricky
            logging.error("Failed to save the zoom meeting link to the appointment: ", err)
            if os.getenv('SENTRY_DSN') != '':
                capture_exception(err)

    event = schemas.Event(
        title=db_appointment.title,
        start=slot.start.replace(tzinfo=timezone.utc),
        end=slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration),
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

    organizer_email = organizer.email

    # create remote event
    if db_calendar.provider == CalendarProvider.google:
        external_connection = utils.list_first(repo.external_connection.get_by_type(db, organizer.id, schemas.ExternalConnectionType.google))

        if external_connection is None or external_connection.token is None:
            raise RemoteCalendarConnectionError()

        organizer_email = external_connection.name

        con = GoogleConnector(
            db=db,
            redis_instance=None,
            google_client=google_client,
            remote_calendar_id=db_calendar.user,
            calendar_id=db_calendar.id,
            subscriber_id=organizer.id,
            google_tkn=external_connection.token,
        )
    else:
        con = CalDavConnector(
            redis_instance=None,
            url=db_calendar.url,
            user=db_calendar.user,
            password=db_calendar.password,
            subscriber_id=organizer.id,
            calendar_id=db_calendar.id,
        )
    con.create_event(event=event, attendee=s_a.attendee, organizer=organizer, organizer_email=organizer_email)

    # update appointment slot data
    repo.slot.update(db=db, slot_id=s_a.slot_id, attendee=s_a.attendee)

    # send mail with .ics attachment to attendee
    Tools().send_vevent(background_tasks, db_appointment, slot, organizer, s_a.attendee)

    return schemas.SlotAttendee(slot_id=s_a.slot_id, attendee=s_a.attendee)


@router.get("/apmt/serve/ics/{slug}/{slot_id}", response_model=schemas.FileDownload)
def public_appointment_serve_ics(slug: str, slot_id: int, db: Session = Depends(get_db)):
    """endpoint to serve ICS file for time slot to download"""
    db_appointment = repo.appointment.get_public(db, slug=slug)
    if db_appointment is None:
        raise validation.AppointmentNotFoundException()

    if not repo.appointment.has_slot(db, appointment_id=db_appointment.id, slot_id=slot_id):
        raise validation.SlotNotFoundException()

    slot = repo.slot.get(db=db, slot_id=slot_id)
    if slot is None:
        raise validation.SlotNotFoundException()

    organizer = repo.subscriber.get_by_appointment(db=db, appointment_id=db_appointment.id)

    return schemas.FileDownload(
        name="invite",
        content_type="text/calendar",
        data=Tools().create_vevent(appointment=db_appointment, slot=slot, organizer=organizer).decode("utf-8"),
    )


@router.post("/support")
def send_feedback(
    form_data: schemas.SupportRequest,
    background_tasks: BackgroundTasks,
    subscriber: Subscriber = Depends(get_subscriber)
):
    """Send a subscriber's support request to the configured support email address"""
    if not os.getenv("SUPPORT_EMAIL"):
        raise APIException()

    background_tasks.add_task(
        send_support_email,
        requestee=subscriber,
        topic=form_data.topic,
        details=form_data.details,
    )
    return True


@router.get('/privacy')
def privacy():
    with open(f'{os.path.dirname(__file__)}/../templates/legal/en/privacy.jinja2') as fh:
        contents = fh.read()
    return HTMLResponse(contents)


@router.get('/terms')
def terms():
    with open(f'{os.path.dirname(__file__)}/../templates/legal/en/terms.jinja2') as fh:
        contents = fh.read()
    return HTMLResponse(contents)
