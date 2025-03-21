import json
import logging
import os
import secrets
import requests.exceptions
import sentry_sdk
from redis import Redis, RedisCluster

# database
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from .. import utils
from ..database import repo, schemas

# authentication
from ..controller.calendar import CalDavConnector, Tools, GoogleConnector
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from ..controller.apis.google_client import GoogleClient
from ..controller.auth import signed_url_by_subscriber, schedule_links_by_subscriber
from ..database.models import Subscriber, CalendarProvider, InviteStatus
from ..defines import DEFAULT_CALENDAR_COLOUR
from ..dependencies.google import get_google_client
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db, get_redis
from ..exceptions import validation
from ..exceptions.validation import RemoteCalendarConnectionError, APIException
from ..l10n import l10n
from ..tasks.emails import send_support_email

router = APIRouter()


@router.get('/')
def health(db: Session = Depends(get_db)):
    """Small route with no processing that will be used for health checks"""
    try:
        db.query(Subscriber).first()
    except Exception as ex:
        sentry_sdk.capture_exception(ex)
        return JSONResponse(content=l10n('health-bad'), status_code=503)

    if os.getenv('REDIS_URL'):
        try:
            redis_instance: Redis | RedisCluster | None = get_redis()
            if not redis_instance:
                raise RuntimeError('Redis is not available despite being configured. Check settings!')
            redis_instance.ping()
        except Exception as ex:
            sentry_sdk.capture_exception(ex)
            return JSONResponse(content=l10n('health-bad'), status_code=503)

    return JSONResponse(l10n('health-ok'), status_code=200)


@router.get('/session-info')
def session_info():
    """We can put any first-time page load information in here.
    But for now we just need it to ensure that the end-user has a cookie."""
    return True


@router.put('/me', response_model=schemas.SubscriberMeOut)
def update_me(
    data: schemas.SubscriberIn, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)
):
    """endpoint to update data of authenticated subscriber"""
    if subscriber.username != data.username and repo.subscriber.get_by_username(db, data.username):
        raise HTTPException(status_code=403, detail=l10n('username-not-available'))

    me = repo.subscriber.update(db=db, data=data, subscriber_id=subscriber.id)
    return schemas.SubscriberMeOut(
        username=me.username,
        email=me.email.lower(),
        preferred_email=me.preferred_email,
        name=me.name,
        level=me.level,
        timezone=me.timezone,
        is_setup=me.is_setup,
        avatar_url=me.avatar_url,
        schedule_links=schedule_links_by_subscriber(db, subscriber),
        unique_hash=me.unique_hash,
        language=me.language,
        colour_scheme=me.colour_scheme,
        time_mode=me.time_mode,
    )


@router.get('/me/calendars', response_model=list[schemas.CalendarOut])
def read_my_calendars(
    db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber), only_connected: bool = True
):
    """get all calendar connections of authenticated subscriber"""
    calendars = repo.calendar.get_by_subscriber(db, subscriber_id=subscriber.id, include_unconnected=not only_connected)
    return [schemas.CalendarOut(id=c.id, title=c.title, color=c.color, connected=c.connected) for c in calendars]


@router.get('/me/appointments', response_model=list[schemas.AppointmentWithCalendarOut])
def read_my_appointments(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """get all appointments of authenticated subscriber"""
    appointments = repo.appointment.get_by_subscriber(db, subscriber_id=subscriber.id)
    # Mix in calendar title and color.
    # Note because we `__dict__` any relationship values won't be carried over, so don't forget to manually add those!
    appointments = map(
        lambda x: schemas.AppointmentWithCalendarOut(
            **x.__dict__, calendar_title=x.calendar.title, calendar_color=x.calendar.color or DEFAULT_CALENDAR_COLOUR
        ),
        appointments,
    )
    return appointments


@router.get('/me/signature')
def get_my_signature(subscriber: Subscriber = Depends(get_subscriber)):
    """Retrieve a subscriber's signed short link"""
    return {'url': signed_url_by_subscriber(subscriber)}


@router.post('/me/signature')
def refresh_signature(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Refresh a subscriber's signed short link"""
    repo.subscriber.update(
        db,
        schemas.SubscriberAuth(
            email=subscriber.email, username=subscriber.username, short_link_hash=secrets.token_hex(32)
        ),
        subscriber.id,
    )

    # Update schedule slugs as well!
    # This is temp until we figure this flow out
    schedules = repo.schedule.get_by_subscriber(db, subscriber.id)
    for schedule in schedules:
        # Clear so we can generate a new one
        schedule.slug = None
        slug = repo.schedule.generate_slug(db, schedule.id)
        if not slug:
            logging.warning('Could not generate unique slug!')

    return True


@router.get('/me/invites', response_model=list[schemas.InviteOut])
def get_my_invites(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    return repo.invite.get_by_owner(db, subscriber.id, status=InviteStatus.active, only_unused=True)


@router.post('/cal', response_model=schemas.CalendarOut)
def create_my_calendar(
    calendar: schemas.CalendarConnection,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to add a new calendar connection for authenticated subscriber"""

    # Test the connection first
    if calendar.provider == CalendarProvider.google:
        external_connection = utils.list_first(
            repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google)
        )

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
            db=db,
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


@router.get('/cal/{id}', response_model=schemas.CalendarConnectionOut)
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


@router.put('/cal/{id}', response_model=schemas.CalendarOut)
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


@router.post('/cal/{id}/connect', response_model=schemas.CalendarOut)
@router.post('/cal/{id}/disconnect', response_model=schemas.CalendarOut)
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


@router.delete('/cal/{id}', response_model=schemas.CalendarOut)
def delete_my_calendar(id: int, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """endpoint to remove a calendar from db"""
    if not repo.calendar.exists(db, calendar_id=id):
        raise validation.CalendarNotFoundException()
    if not repo.calendar.is_owned(db, calendar_id=id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()

    cal = repo.calendar.delete(db=db, calendar_id=id)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.post('/rmt/calendars', response_model=list[schemas.CalendarConnectionOut])
def read_remote_calendars(
    connection: schemas.CalendarConnection,
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
    db: Session = Depends(get_db),
):
    """endpoint to get calendars from a remote CalDAV server"""
    if connection.provider == CalendarProvider.google:
        external_connection = utils.list_first(
            repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google)
        )

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
            db=None,
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


@router.post('/rmt/sync')
def sync_remote_calendars(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client: GoogleClient = Depends(get_google_client),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to sync calendars from a remote server"""
    # Create a list of connections and loop through them with sync
    google_ec = utils.list_first(
        repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google)
    )
    caldav_ecs = repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.caldav)

    # Filter out any nulls
    ecs = list(filter(lambda ec: ec, [google_ec, *caldav_ecs]))

    if len(ecs) == 0:
        raise RemoteCalendarConnectionError()

    for ec in ecs:
        if ec.type == schemas.ExternalConnectionType.google:
            connection = GoogleConnector(
                db=db,
                redis_instance=redis,
                google_client=google_client,
                remote_calendar_id=None,
                calendar_id=None,
                subscriber_id=subscriber.id,
                google_tkn=ec.token,
            )
        else:
            url, username = json.loads(ec.type_id)
            connection = CalDavConnector(
                db=db,
                subscriber_id=subscriber.id,
                redis_instance=redis,
                url=url,
                user=username,
                password=ec.token,
                calendar_id=None,
            )

        error_occurred = connection.sync_calendars()
        # And then redirect back to frontend
        if error_occurred:
            raise HTTPException(500, l10n('calendar-sync-fail'))
    return True


@router.get('/rmt/cal/{id}/{start}/{end}', response_model=list[schemas.Event])
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
        external_connection = utils.list_first(
            repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google)
        )

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
            db=db,
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


@router.get('/apmt/serve/ics/{slug}/{slot_id}', response_model=schemas.FileDownload)
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
        name='invite',
        content_type='text/calendar',
        data=Tools().create_vevent(appointment=db_appointment, slot=slot, organizer=organizer).decode('utf-8'),
    )


@router.post('/support')
def send_feedback(
    form_data: schemas.SupportRequest,
    background_tasks: BackgroundTasks,
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Send a subscriber's support request to the configured support email address"""
    if not os.getenv('SUPPORT_EMAIL'):
        # Ensure sentry at least captures it!
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_message('No SUPPORT_EMAIL is set, support messages are being ignored!')
            sentry_sdk.capture_message(f"""
            Support Email Alert!
            FROM: {subscriber.name} <{subscriber.preferred_email}>
            SUBJECT: {form_data.topic}
            MESSAGE: {form_data.details}""")
        raise APIException()

    background_tasks.add_task(
        send_support_email,
        requestee_name=subscriber.name,
        requestee_email=subscriber.preferred_email,
        topic=form_data.topic,
        details=form_data.details,
    )
    return True
