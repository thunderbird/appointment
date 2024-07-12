from fastapi import APIRouter, Depends, Body, BackgroundTasks
import logging
import os

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
from ..dependencies.auth import get_subscriber, get_subscriber_from_signed_url, \
    get_subscriber_from_schedule_or_signed_url
from ..dependencies.database import get_db, get_redis
from ..dependencies.google import get_google_client
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from ..dependencies.zoom import get_zoom_client
from ..exceptions import validation
from ..exceptions.calendar import EventNotCreatedException
from ..exceptions.validation import RemoteCalendarConnectionError, EventCouldNotBeAccepted
from ..tasks.emails import (
    send_pending_email,
    send_confirmation_email,
    send_rejection_email,
    send_zoom_meeting_failed_email,
)

router = APIRouter()


@router.post('/', response_model=schemas.Schedule)
def create_calendar_schedule(
    schedule: schemas.ScheduleBase,
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

    # If slug isn't provided, give them the last 8 characters from a uuid4
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


@router.get('/{id}', response_model=schemas.Schedule, deprecated=True)
def read_schedule(
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Gets information regarding a specific schedule"""
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

    if schedule.slug is None:
        # If slug isn't provided, give them the last 8 characters from a uuid4
        schedule.slug = repo.schedule.generate_slug(db, id)
        if not schedule.slug:
            # A little extra, but things are a little out of place right now..
            raise validation.ScheduleCreationException()

    return repo.schedule.update(db=db, schedule=schedule, schedule_id=id)


@router.post("/public/url")
def get_signed_url_from_slug(
    schedule_slug: schemas.ScheduleSlug,
    db: Session = Depends(get_db),
) -> dict:
    schedule = repo.schedule.get_by_slug(db, schedule_slug.slug)
    if not schedule:
        raise validation.ScheduleNotFoundException()

    owner = schedule.owner
    if not owner:
        raise validation.ScheduleNotFoundException()

    return {
        'url': signed_url_by_subscriber(owner)
    }


@router.post('/public/availability', response_model=schemas.AppointmentOut)
def read_schedule_availabilities(
    subscriber: Subscriber = Depends(get_subscriber_from_schedule_or_signed_url),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client: GoogleClient = Depends(get_google_client),
):
    """Returns the calculated availability for the first schedule from a subscribers public profile link
    """
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
        booking_confirmation=schedule.booking_confirmation
    )


@router.put('/public/availability/request')
def request_schedule_availability_slot(
    s_a: schemas.AvailabilitySlotAttendee,
    background_tasks: BackgroundTasks,
    subscriber: Subscriber = Depends(get_subscriber_from_schedule_or_signed_url),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client=Depends(get_google_client),
):
    """endpoint to request a time slot for a schedule via public link and send confirmation mail to owner if set
    """

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

    # check if slot still available, might already be taken at this time
    slot = schemas.SlotBase(**s_a.slot.dict())
    if repo.slot.exists_on_schedule(db, slot, schedule.id):
        raise validation.SlotAlreadyTakenException()

    # We need to verify that the time is actually available on the remote calendar
    if calendar.provider == CalendarProvider.google:
        external_connection = utils.list_first(repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google))

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
    attendee_name = slot.attendee.name if slot.attendee.name is not None else slot.attendee.email
    subscriber_name = subscriber.name if subscriber.name is not None else subscriber.email
    title = f'Appointment - {subscriber_name} and {attendee_name}'
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

    # If bookings are configured to be confirmed by the owner for this schedule,
    # send emails to owner for confirmation and attendee for information
    if schedule.booking_confirmation:

        # human readable date in subscribers timezone
        # TODO: handle locale date representation
        date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(subscriber.timezone)).strftime('%c')
        date = f'{date}, {slot.duration} minutes ({subscriber.timezone})'

        # human readable date in attendee timezone
        # TODO: handle locale date representation
        attendee_date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(slot.attendee.timezone)).strftime('%c')
        attendee_date = f'{attendee_date}, {slot.duration} minutes ({slot.attendee.timezone})'

        # Sending confirmation email to owner
        background_tasks.add_task(
            send_confirmation_email, url=url, attendee_name=attendee.name, attendee_email=attendee.email, date=date,
            to=subscriber.preferred_email
        )

        # Sending pending email to attendee
        background_tasks.add_task(
            send_pending_email, owner_name=subscriber.name, date=attendee_date, to=slot.attendee.email
        )

    # If no confirmation is needed, directly confirm the booking and send invitation mail
    else:
        handle_schedule_availability_decision(
            True, calendar, schedule, subscriber, slot, db, redis, google_client, background_tasks
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
    """endpoint to react to owners decision to a request of a time slot of his public link
    """
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
        or not repo.slot.is_available(db, slot.id)
        or not repo.schedule.has_slot(db, schedule.id, slot.id)
        or slot.booking_tkn != data.slot_token
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
    confirmed: bool,
    calendar,
    schedule,
    subscriber,
    slot,
    db,
    redis,
    google_client,
    background_tasks
):
    """Actual handling of the availability decision
    if confirmed: create an event in remote calendar and send invitation mail
    """

    # TODO: check booking expiration date
    # check if request was denied
    if confirmed is False:
        # human readable date in subscribers timezone
        # TODO: handle locale date representation
        date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(subscriber.timezone)).strftime('%c')
        date = f'{date}, {slot.duration} minutes'
        # send rejection information to bookee
        background_tasks.add_task(send_rejection_email, owner_name=subscriber.name, date=date, to=slot.attendee.email)
        repo.slot.delete(db, slot.id)

        if slot.appointment_id:
            # delete the appointment, this will also delete the slot.
            repo.appointment.delete(db, slot.appointment_id)
        else:
            # delete the scheduled slot to make the time available again
            repo.slot.delete(db, slot.id)

        return True

    # otherwise, confirm slot and create event
    location_url = schedule.location_url

    attendee_name = slot.attendee.name if slot.attendee.name is not None else slot.attendee.email
    subscriber_name = subscriber.name if subscriber.name is not None else subscriber.email

    attendees = f'{subscriber_name} and {attendee_name}'

    if not slot.appointment:
        title = f'Appointment - {attendees}'
    else:
        title = slot.appointment.title
        # Update the appointment to closed
        repo.appointment.update_status(db, slot.appointment_id, models.AppointmentStatus.closed)

    # If needed: Create a zoom meeting link for this booking
    if schedule.meeting_link_provider == MeetingLinkProviderType.zoom:
        try:
            zoom_client = get_zoom_client(subscriber)
            response = zoom_client.create_meeting(attendees, slot.start.isoformat(), slot.duration, subscriber.timezone)
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
            background_tasks.add_task(send_zoom_meeting_failed_email, to=subscriber.preferred_email, appointment_title=schedule.name)
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
            type=schedule.location_type,
            url=location_url,
            name=None,
        ),
        uuid=slot.appointment.uuid if slot.appointment else None,
    )

    organizer_email = subscriber.email

    # create remote event
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
            redis_instance=redis,
            subscriber_id=subscriber.id,
            calendar_id=calendar.id,
            url=calendar.url,
            user=calendar.user,
            password=calendar.password,
        )

    try:
        con.create_event(event=event, attendee=slot.attendee, organizer=subscriber, organizer_email=organizer_email)
    except EventNotCreatedException:
        raise EventCouldNotBeAccepted

    # Book the slot at the end
    slot = repo.slot.book(db, slot.id)

    Tools().send_vevent(background_tasks, slot.appointment, slot, subscriber, slot.attendee)

    return True
