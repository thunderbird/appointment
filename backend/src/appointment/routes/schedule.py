import sentry_sdk
import logging
import os
import zoneinfo

from oauthlib.oauth2 import OAuth2Error
from requests import HTTPError
from sentry_sdk import capture_exception
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import utils
from ..controller.calendar import CalDavConnector, Tools, GoogleConnector
from ..controller.apis.google_client import GoogleClient
from ..controller.auth import signed_url_by_subscriber
from ..database import repo, schemas, models
from ..database.models import (
    Subscriber,
    CalendarProvider,
    random_slug,
    BookingStatus,
    MeetingLinkProviderType,
    ExternalConnectionType,
)
from ..database.schemas import ExternalConnection
from ..dependencies.auth import get_subscriber, get_subscriber_from_schedule_or_signed_url
from ..dependencies.database import get_db, get_redis
from ..dependencies.google import get_google_client
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from ..dependencies.zoom import get_zoom_client
from ..exceptions import validation
from ..exceptions.calendar import EventNotCreatedException, EventNotDeletedException
from ..exceptions.misc import UnexpectedBehaviourWarning
from ..exceptions.validation import RemoteCalendarConnectionError, EventCouldNotBeAccepted, EventCouldNotBeDeleted
from ..tasks.emails import (
    send_confirmation_email,
    send_zoom_meeting_failed_email,
    send_new_booking_email,
)
from ..l10n import l10n
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, BackgroundTasks, Request

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def is_this_a_valid_booking_time(schedule: models.Schedule, booking_slot: schemas.SlotBase) -> bool:
    """Checks for timezone correctness, weekday and start/end time validity.
    Booking slots are calculated for today utc, while schedule's time may be in the another tz offset"""
    # For now lets only accept utc bookings as that's what our frontend supplies us.
    if booking_slot.start.tzname() != 'UTC':
        logging.error(f'Non-UTC timezone requested: {booking_slot.start}.')
        return False

    # Now we can safely assume start is in UTC time!

    # Check for slot duration correctness
    if booking_slot.duration != schedule.slot_duration:
        return False

    schedule_tzinfo = zoneinfo.ZoneInfo(schedule.timezone)

    # Is the time requested on a day of the week they have disabled?
    # This should be based on the schedule timezone
    booking_slot_start = booking_slot.start.astimezone(schedule_tzinfo)
    iso_weekday = int(booking_slot_start.strftime('%u'))
    if iso_weekday not in schedule.weekdays:
        return False

    # Is the time requested within our booking times?
    today = booking_slot.start.date()

    # If our end time is below start time, then it's the next day.
    add_day = 1 if schedule.end_time <= schedule.start_time else 0

    # We need to compare in local time
    start_datetime = datetime.combine(today, schedule.start_time, tzinfo=schedule_tzinfo) + schedule.timezone_offset
    end_datetime = (
        datetime.combine(today, schedule.end_time, tzinfo=schedule_tzinfo)
        + timedelta(days=add_day)
        + schedule.timezone_offset
    )
    booking_slot_end = booking_slot_start + timedelta(minutes=schedule.slot_duration)

    too_early = booking_slot_start < start_datetime
    too_late = booking_slot_end > end_datetime

    if too_early or too_late:
        return False

    return True


@router.post('/', response_model=schemas.Schedule)
def create_calendar_schedule(
    schedule: schemas.ScheduleValidationIn,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to add a new schedule for a given calendar"""
    if not repo.calendar.exists(db, calendar_id=schedule.calendar_id):
        raise validation.CalendarNotFoundException()
    if not repo.calendar.is_owned(db, calendar_id=schedule.calendar_id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()
    if not repo.calendar.is_connected(db, calendar_id=schedule.calendar_id):
        raise validation.CalendarNotConnectedException()

    db_schedule = repo.schedule.create(db=db, schedule=schedule)

    # The first schedule currently is initialized without a slug to provide a username only availability link.
    # If we already have at least one schedule and slug isn't provided, give them the last 8 characters from a uuid4.
    if len(repo.schedule.get_by_subscriber(db, subscriber.id)) > 0 and not schedule.slug:
        slug = repo.schedule.generate_slug(db, db_schedule.id)
        if not slug:
            # A little extra, but things are a little out of place right now..
            repo.schedule.hard_delete(db, db_schedule.id)
            raise validation.ScheduleCreationException()

    return db_schedule


@router.get('/', response_model=list[schemas.Schedule])
def read_schedules(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Gets all of the available schedules for the logged in subscriber"""
    return repo.schedule.get_by_subscriber(db, subscriber_id=subscriber.id)


@router.get('/{id}', response_model=schemas.Schedule)
def read_schedule(
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Gets information regarding a specific schedule
    TODO: Currently unused, but we'll need it soon."""
    schedule = repo.schedule.get(db, schedule_id=id)
    if schedule is None:
        raise validation.ScheduleNotFoundException()
    if not repo.schedule.is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise validation.ScheduleNotAuthorizedException()
    return schedule


@router.put('/{id}', response_model=schemas.Schedule)
def update_schedule(
    id: int,
    schedule: schemas.ScheduleValidationIn,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not repo.schedule.exists(db, schedule_id=id):
        raise validation.ScheduleNotFoundException()
    if not repo.calendar.is_connected(db, calendar_id=schedule.calendar_id):
        raise validation.CalendarNotConnectedException()
    if not repo.schedule.is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise validation.ScheduleNotAuthorizedException()
    if (
        schedule.meeting_link_provider == MeetingLinkProviderType.zoom
        and subscriber.get_external_connection(ExternalConnectionType.zoom) is None
    ):
        raise validation.ZoomNotConnectedException()

    # If slug isn't provided, make it null in db
    if not schedule.slug:
        schedule.slug = None

    return repo.schedule.update(db=db, schedule=schedule, schedule_id=id)


@router.post('/public/availability', response_model=schemas.AppointmentOut)
@limiter.limit('20/minute')
def read_schedule_availabilities(
    request: Request,
    subscriber: Subscriber = Depends(get_subscriber_from_schedule_or_signed_url),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client: GoogleClient = Depends(get_google_client),
):
    """Returns the calculated availability for the first schedule from a subscribers public profile link"""
    # Raise a schedule not found exception if the schedule owner does not have a timezone set.
    if subscriber.timezone is None:
        raise validation.ScheduleNotFoundException()

    schedules = repo.schedule.get_by_subscriber(db, subscriber_id=subscriber.id)

    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise validation.ScheduleNotActive()

    # check if schedule is enabled
    if not schedule.active:
        raise validation.ScheduleNotActive()

    # check if calendar is connected, if its not then its a schedule not active error
    if not schedule.calendar or not schedule.calendar.connected:
        raise validation.ScheduleNotActive()

    calendars = repo.calendar.get_by_subscriber(db, subscriber.id, False)

    if not calendars or len(calendars) == 0:
        raise validation.CalendarNotFoundException()

    # calculate theoretically possible slots from schedule config
    available_slots = Tools.available_slots_from_schedule(schedule)

    # get all events from all connected calendars in scheduled date range
    existing_slots = Tools.existing_events_for_schedule(schedule, calendars, subscriber, google_client, db, redis)
    actual_slots = Tools.events_roll_up_difference(available_slots, existing_slots)

    if not actual_slots or len(actual_slots) == 0:
        raise validation.SlotNotFoundException()

    # TODO: dedicate an own schema to this endpoint
    return schemas.AppointmentOut(
        title=schedule.name,
        details=schedule.details,
        owner_name=subscriber.name,
        slots=actual_slots,
        slot_duration=schedule.slot_duration,
        booking_confirmation=schedule.booking_confirmation,
    )


@router.put('/public/availability/request')
@limiter.limit('20/minute')
def request_schedule_availability_slot(
    request: Request,
    s_a: schemas.AvailabilitySlotAttendee,
    background_tasks: BackgroundTasks,
    subscriber: Subscriber = Depends(get_subscriber_from_schedule_or_signed_url),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client=Depends(get_google_client),
):
    """endpoint to request a time slot for a schedule via public link and send confirmation mail to owner if set"""

    # Raise a schedule not found exception if the schedule owner does not have a timezone set.
    if subscriber.timezone is None:
        raise validation.ScheduleNotFoundException()

    schedules = repo.schedule.get_by_subscriber(db, subscriber_id=subscriber.id)

    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise validation.ScheduleNotFoundException()

    # check if schedule is enabled
    if not schedule.active:
        raise validation.ScheduleNotFoundException()

    # get calendar
    calendar = repo.calendar.get(db, calendar_id=schedule.calendar_id)
    if calendar is None:
        raise validation.CalendarNotFoundException()

    # Ensure the request is valid
    if not is_this_a_valid_booking_time(schedule, s_a.slot):
        # Gather the relevant information for debugging, and capture it.
        debug_obj = {
            'schedule': {
                'time_updated': schedule.time_updated,
                'start': schedule.start_time,
                'end': schedule.end_time,
                'local_start': schedule.start_time_local,
                'local_end': schedule.end_time_local,
                'weekdays': schedule.weekdays,
                'slot_duration': schedule.slot_duration,
                'start_date': schedule.start_date,
                'end_date': schedule.end_date,
                'earliest_booking': schedule.earliest_booking,
                'farthest_booking': schedule.farthest_booking,
            },
            'slot': s_a.slot,
            'submitter_timezone': s_a.attendee.timezone,
            'owner_timezone': subscriber.timezone,
        }
        # Raise and catch the unexpected behaviour warning so we can get proper stacktrace in sentry...
        try:
            sentry_sdk.set_extra('debug_object', debug_obj)
            raise UnexpectedBehaviourWarning(message='Invalid booking time warning!', info=debug_obj)
        except UnexpectedBehaviourWarning as ex:
            sentry_sdk.capture_exception(ex)

        raise validation.SlotNotFoundException()

    # check if slot still available, might already be taken at this time
    slot = schemas.SlotBase(**s_a.slot.model_dump())
    if repo.slot.exists_on_schedule(db, slot, schedule.id):
        raise validation.SlotAlreadyTakenException()

    # We need to verify that the time is actually available on the remote calendar
    if calendar.provider == CalendarProvider.google:
        external_connection = utils.list_first(
            repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google)
        )

        if external_connection is None or external_connection.token is None:
            raise RemoteCalendarConnectionError()

        con = GoogleConnector(
            db=db,
            redis_instance=redis,
            google_client=google_client,
            remote_calendar_id=calendar.user,
            subscriber_id=subscriber.id,
            calendar_id=calendar.id,
            google_tkn=external_connection.token,
        )
    else:
        con = CalDavConnector(
            db=db,
            redis_instance=redis,
            subscriber_id=subscriber.id,
            calendar_id=calendar.id,
            url=calendar.url,
            user=calendar.user,
            password=calendar.password,
        )

    # Ok we need to clear the cache for all calendars, because we need to recheck them.
    con.bust_cached_events(True)
    calendars = repo.calendar.get_by_subscriber(db, subscriber.id, False)
    existing_remote_events = Tools.existing_events_for_schedule(
        schedule, calendars, subscriber, google_client, db, redis
    )
    has_collision = Tools.events_roll_up_difference([slot], existing_remote_events)
    # If we only have booked entries in this list then it means our slot is not available.
    if all(evt.booking_status == BookingStatus.booked for evt in has_collision):
        raise validation.SlotAlreadyTakenException()

    # create slot in db with token and expiration date
    token = random_slug()
    slot.booking_tkn = token
    slot.booking_expires_at = datetime.now() + timedelta(days=1)
    slot.booking_status = BookingStatus.requested
    slot = repo.slot.add_for_schedule(db, slot, schedule.id)

    # create attendee for this slot
    attendee = repo.slot.update(db, slot.id, s_a.attendee)

    # Create a pending appointment
    prefix = f'{l10n('event-hold-prefix')} ' if schedule.booking_confirmation else ''
    title = Tools.default_event_title(slot, subscriber, prefix)
    status = models.AppointmentStatus.opened if schedule.booking_confirmation else models.AppointmentStatus.closed

    appointment = repo.appointment.create(
        db,
        schemas.AppointmentFull(
            title=title,
            details=schedule.details,
            calendar_id=calendar.id,
            duration=slot.duration,
            status=status,
            location_type=schedule.location_type,
            location_url=schedule.location_url,
        ),
    )

    # Update the slot
    slot.appointment_id = appointment.id
    db.add(slot)
    db.commit()
    db.refresh(slot)

    # generate confirm and deny links with encoded booking token and signed owner url
    url = f'{signed_url_by_subscriber(subscriber)}/confirm/{slot.id}/{token}'

    # human readable date in subscribers timezone
    # TODO: handle locale date representation
    date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(subscriber.timezone))

    # If bookings are configured to be confirmed by the owner for this schedule,
    # Create HOLD event in owners calender and send emails to owner for confirmation and attendee for information
    if schedule.booking_confirmation:
        # Sending confirmation email to owner
        background_tasks.add_task(
            send_confirmation_email,
            url=url,
            attendee_name=attendee.name,
            attendee_email=attendee.email,
            date=date,
            duration=slot.duration,
            schedule_name=schedule.name,
            to=subscriber.preferred_email,
            lang=subscriber.language,
        )

        # Create remote HOLD event
        event = schemas.Event(
            title=title,
            start=slot.start.replace(tzinfo=timezone.utc),
            end=slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration),
            description=schedule.details or '',
            location=schemas.EventLocation(
                type=models.LocationType.online,
                url=schedule.location_url,
                name=None,
            ),
            uuid=slot.appointment.uuid if slot.appointment else None,
        )

        # create HOLD event in owners calender
        event = save_remote_event(event, calendar, subscriber, slot, db, redis, google_client)
        # Add the external id if available
        if appointment and event.external_id:
            repo.appointment.update_external_id(db, appointment, event.external_id)

        # Sending confirmation pending information email to attendee with HOLD event attached
        Tools().send_hold_vevent(background_tasks, slot.appointment, slot, subscriber, slot.attendee)

    # If no confirmation is needed, directly confirm the booking and send invitation mail
    else:
        handle_schedule_availability_decision(
            True, calendar, schedule, subscriber, slot, db, redis, google_client, background_tasks
        )

        # Notify the subscriber that they have a new confirmed booking
        background_tasks.add_task(
            send_new_booking_email,
            name=attendee.name,
            email=attendee.email,
            date=date,
            duration=slot.duration,
            schedule_name=schedule.name,
            to=subscriber.preferred_email,
            lang=subscriber.language,
        )

    # Mini version of slot, so we can grab the newly created slot id for tests
    return schemas.SlotOut(
        id=slot.id,
        start=slot.start,
        duration=slot.duration,
        attendee_id=slot.attendee_id,
    )


@router.put('/public/availability/booking', response_model=schemas.AvailabilitySlotAttendee)
def decide_on_schedule_availability_slot(
    data: schemas.AvailabilitySlotConfirmation,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to react to owners decision to a request of a time slot of his public link"""
    subscriber = repo.subscriber.verify_link(db, data.owner_url)
    if not subscriber:
        raise validation.InvalidLinkException()

    # Raise a schedule not found exception if the schedule owner does not have a timezone set.
    if subscriber.timezone is None:
        raise validation.ScheduleNotFoundException()

    schedules = repo.schedule.get_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise validation.ScheduleNotFoundException()

    # check if schedule is enabled
    if not schedule.active:
        raise validation.ScheduleNotFoundException()

    # get calendar
    calendar = repo.calendar.get(db, calendar_id=schedule.calendar_id)
    if calendar is None:
        raise validation.CalendarNotFoundException()

    # get slot and check if slot exists and is not booked yet and token is the same
    slot = repo.slot.get(db, data.slot_id)
    if (
        not slot
        or not repo.schedule.has_slot(db, schedule.id, slot.id)
        or slot.booking_tkn != data.slot_token
        or slot.booking_status != BookingStatus.requested
    ):
        raise validation.SlotNotFoundException()

    # handle decision, do the actual booking if confirmed and send invitation mail
    handle_schedule_availability_decision(
        data.confirmed, calendar, schedule, subscriber, slot, db, redis, google_client, background_tasks
    )

    return schemas.AvailabilitySlotAttendee(
        slot=schemas.SlotBase(start=slot.start, duration=slot.duration),
        attendee=schemas.AttendeeBase(
            email=slot.attendee.email, name=slot.attendee.name, timezone=slot.attendee.timezone
        ),
    )


def handle_schedule_availability_decision(
    confirmed: bool, calendar, schedule, subscriber, slot, db, redis, google_client, background_tasks
):
    """Actual handling of the availability decision
    if confirmed: create an event in remote calendar and send invitation mail
    """

    appointment = None
    appointment_calendar = None
    if slot.appointment:
        # Retrieve the calendar from the appointment not the schedule
        appointment = slot.appointment
        db.add(appointment)
        appointment_calendar = appointment.calendar

    # TODO: Check booking expiration date
    # check if request was denied
    if confirmed is False:
        # send rejection information to bookee
        Tools().send_cancel_vevent(background_tasks, appointment, slot, subscriber, slot.attendee)
        repo.slot.delete(db, slot.id)

        if slot.appointment_id:
            # delete the appointment, this will also delete the slot.
            repo.appointment.delete(db, slot.appointment_id)
        else:
            # delete the scheduled slot to make the time available again
            repo.slot.delete(db, slot.id)

        # Delete remote HOLD event if existing
        if appointment:
            uuid = slot.appointment.external_id if slot.appointment.external_id else str(slot.appointment.uuid)
            delete_remote_event(uuid, appointment_calendar, subscriber, db, redis, google_client)

        return True

    # otherwise, confirm slot and create event
    location_url = schedule.location_url

    # Rebuild title to remove "HOLD: " if exists
    title = Tools.default_event_title(slot, subscriber)

    if slot.appointment:
        # Update the appointment to closed
        repo.appointment.update_status(db, slot.appointment_id, models.AppointmentStatus.closed)

    # If needed: Create a zoom meeting link for this booking
    if schedule.meeting_link_provider == MeetingLinkProviderType.zoom:
        try:
            zoom_client = get_zoom_client(subscriber)
            response = zoom_client.create_meeting(title, slot.start.isoformat(), slot.duration, subscriber.timezone)
            if 'id' in response:
                location_url = zoom_client.get_meeting(response['id'])['join_url']
                slot.meeting_link_id = response['id']
                slot.meeting_link_url = location_url

                db.add(slot)
                db.commit()
        except HTTPError as err:  # Not fatal, just a bummer
            logging.error('Zoom meeting creation error: ', err)

            # Ensure sentry captures the error too!
            if os.getenv('SENTRY_DSN') != '':
                capture_exception(err)

            # Notify the organizer that the meeting link could not be created!
            background_tasks.add_task(
                send_zoom_meeting_failed_email, to=subscriber.preferred_email, appointment_title=schedule.name
            )
        except OAuth2Error as err:
            logging.error('OAuth flow error during zoom meeting creation: ', err)
            if os.getenv('SENTRY_DSN') != '':
                capture_exception(err)

            # Notify the organizer that the meeting link could not be created!
            background_tasks.add_task(
                send_zoom_meeting_failed_email, to=subscriber.preferred_email, appointment_title=schedule.name
            )
        except SQLAlchemyError as err:  # Not fatal, but could make things tricky
            logging.error('Failed to save the zoom meeting link to the appointment: ', err)
            if os.getenv('SENTRY_DSN') != '':
                capture_exception(err)

    event = schemas.Event(
        title=title,
        start=slot.start.replace(tzinfo=timezone.utc),
        end=slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration),
        description=schedule.details or '',
        location=schemas.EventLocation(
            type=models.LocationType.online,
            url=slot.meeting_link_url if slot.meeting_link_url else location_url,
            name=None,
        ),
        uuid=slot.appointment.uuid if slot.appointment else None,
    )

    # Update HOLD event
    appointment = repo.appointment.update_title(db, slot.appointment_id, title)
    event = save_remote_event(event, appointment_calendar, subscriber, slot, db, redis, google_client)
    if appointment and event.external_id:
        repo.appointment.update_external_id(db, appointment, event.external_id)

    # Book the slot at the end
    slot = repo.slot.book(db, slot.id)

    Tools().send_invitation_vevent(background_tasks, appointment, slot, subscriber, slot.attendee)

    return True


def get_remote_connection(calendar, subscriber, db, redis, google_client):
    """Retrieves the connector for the given calendar
    Returns connector and organizer email address as tuple
    """
    organizer_email = subscriber.email

    if calendar.provider == CalendarProvider.google:
        external_connection: ExternalConnection | None = utils.list_first(
            repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google)
        )

        if external_connection is None or external_connection.token is None:
            raise RemoteCalendarConnectionError()

        # Email is stored in the name
        organizer_email = external_connection.name

        con = GoogleConnector(
            db=db,
            redis_instance=redis,
            google_client=google_client,
            remote_calendar_id=calendar.user,
            subscriber_id=subscriber.id,
            calendar_id=calendar.id,
            google_tkn=external_connection.token,
        )
    else:
        con = CalDavConnector(
            db=db,
            redis_instance=redis,
            subscriber_id=subscriber.id,
            calendar_id=calendar.id,
            url=calendar.url,
            user=calendar.user,
            password=calendar.password,
        )

    return (con, organizer_email)


def save_remote_event(event, calendar, subscriber, slot, db, redis, google_client):
    """Create or update a remote event"""
    con, organizer_email = get_remote_connection(calendar, subscriber, db, redis, google_client)

    try:
        return con.save_event(
            event=event, attendee=slot.attendee, organizer=subscriber, organizer_email=organizer_email
        )
    except EventNotCreatedException:
        raise EventCouldNotBeAccepted


def delete_remote_event(uid: str, calendar, subscriber, db, redis, google_client):
    """Create or update a remote event
    if is_hold: create an event in remote calendar and send invitation mail
    """
    con, _ = get_remote_connection(calendar, subscriber, db, redis, google_client)

    try:
        con.delete_event(uid=uid)
    except EventNotDeletedException:
        raise EventCouldNotBeDeleted
