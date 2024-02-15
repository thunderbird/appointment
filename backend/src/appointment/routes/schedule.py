
from fastapi import APIRouter, Depends, Body, BackgroundTasks
import logging
import os

from requests import HTTPError
from sentry_sdk import capture_exception
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..controller.calendar import CalDavConnector, Tools, GoogleConnector
from ..controller.apis.google_client import GoogleClient
from ..controller.auth import signed_url_by_subscriber
from ..database import repo, schemas
from ..database.models import Subscriber, CalendarProvider, random_slug, BookingStatus, MeetingLinkProviderType, ExternalConnectionType
from ..dependencies.auth import get_subscriber, get_subscriber_from_signed_url
from ..dependencies.database import get_db
from ..dependencies.google import get_google_client
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from ..dependencies.zoom import get_zoom_client
from ..exceptions import validation
from ..tasks.emails import send_pending_email, send_confirmation_email, send_rejection_email, \
    send_zoom_meeting_failed_email

router = APIRouter()


@router.post("/", response_model=schemas.Schedule)
def create_calendar_schedule(
    schedule: schemas.ScheduleBase,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to add a new schedule for a given calendar"""
    if not repo.calendar_exists(db, calendar_id=schedule.calendar_id):
        raise validation.CalendarNotFoundException()
    if not repo.calendar_is_owned(db, calendar_id=schedule.calendar_id, subscriber_id=subscriber.id):
        raise validation.CalendarNotAuthorizedException()
    if not repo.calendar_is_connected(db, calendar_id=schedule.calendar_id):
        raise validation.CalendarNotConnectedException()
    return repo.create_calendar_schedule(db=db, schedule=schedule)


@router.get("/", response_model=list[schemas.Schedule])
def read_schedules(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Gets all of the available schedules for the logged in subscriber"""
    return repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)


@router.get("/{id}", response_model=schemas.Schedule, deprecated=True)
def read_schedule(
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Gets information regarding a specific schedule"""
    schedule = repo.get_schedule(db, schedule_id=id)
    if schedule is None:
        raise validation.ScheduleNotFoundException()
    if not repo.schedule_is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise validation.ScheduleNotAuthorizedException()
    return schedule


@router.put("/{id}", response_model=schemas.Schedule)
def update_schedule(
    id: int,
    schedule: schemas.ScheduleValidationIn,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not repo.schedule_exists(db, schedule_id=id):
        raise validation.ScheduleNotFoundException()
    if not repo.schedule_is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise validation.ScheduleNotAuthorizedException()
    if schedule.meeting_link_provider == MeetingLinkProviderType.zoom and subscriber.get_external_connection(ExternalConnectionType.zoom) is None:
        raise validation.ZoomNotConnectedException()
    return repo.update_calendar_schedule(db=db, schedule=schedule, schedule_id=id)


@router.post("/public/availability", response_model=schemas.AppointmentOut)
def read_schedule_availabilities(
    subscriber: Subscriber = Depends(get_subscriber_from_signed_url),
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
):
    """Returns the calculated availability for the first schedule from a subscribers public profile link"""
    # Raise a schedule not found exception if the schedule owner does not have a timezone set.
    if subscriber.timezone is None:
        raise validation.ScheduleNotFoundException()

    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)

    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise validation.ScheduleNotFoundException()

    # check if schedule is enabled
    if not schedule.active:
        raise validation.ScheduleNotActive()

    calendars = repo.get_calendars_by_subscriber(db, subscriber.id, False)

    if not calendars or len(calendars) == 0:
        raise validation.CalendarNotFoundException()

    # calculate theoretically possible slots from schedule config
    available_slots = Tools.available_slots_from_schedule(schedule)

    # get all events from all connected calendars in scheduled date range
    existing_slots = Tools.existing_events_for_schedule(schedule, calendars, subscriber, google_client, db)
    actual_slots = Tools.events_set_difference(available_slots, existing_slots)

    if not actual_slots or len(actual_slots) == 0:
        raise validation.SlotNotFoundException()

    return schemas.AppointmentOut(
        title=schedule.name,
        details=schedule.details,
        owner_name=subscriber.name,
        slots=actual_slots,
    )


@router.put("/public/availability/request")
def request_schedule_availability_slot(
    s_a: schemas.AvailabilitySlotAttendee,
    background_tasks: BackgroundTasks,
    subscriber: Subscriber = Depends(get_subscriber_from_signed_url),
    db: Session = Depends(get_db),
):
    """endpoint to request a time slot for a schedule via public link and send confirmation mail to owner"""

    # Raise a schedule not found exception if the schedule owner does not have a timezone set.
    if subscriber.timezone is None:
        raise validation.ScheduleNotFoundException()

    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)

    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise validation.ScheduleNotFoundException()

    # check if schedule is enabled
    if not schedule.active:
        raise validation.ScheduleNotFoundException()

    # get calendar
    db_calendar = repo.get_calendar(db, calendar_id=schedule.calendar_id)
    if db_calendar is None:
        raise validation.CalendarNotFoundException()

    # check if slot still available, might already be taken at this time
    slot = schemas.SlotBase(**s_a.slot.dict())
    if repo.schedule_slot_exists(db, slot, schedule.id):
        raise validation.SlotAlreadyTakenException()

    # create slot in db with token and expiration date
    token = random_slug()
    slot.booking_tkn = token
    slot.booking_expires_at = datetime.now() + timedelta(days=1)
    slot.booking_status = BookingStatus.requested
    slot = repo.add_schedule_slot(db, slot, schedule.id)
    # create attendee for this slot
    attendee = repo.update_slot(db, slot.id, s_a.attendee)
    # generate confirm and deny links with encoded booking token and signed owner url
    url = f"{signed_url_by_subscriber(subscriber)}/confirm/{slot.id}/{token}"
    # human readable date in subscribers timezone
    # TODO: handle locale date representation
    date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(subscriber.timezone)).strftime("%c")
    date = f"{date}, {slot.duration} minutes"

    # Sending confirmation email to owner
    background_tasks.add_task(send_confirmation_email, url=url, attendee=attendee, date=date, to=subscriber.email)

    # Sending pending email to attendee
    background_tasks.add_task(send_pending_email, owner=subscriber, date=date, to=slot.attendee.email)

    return True


@router.put("/public/availability/booking", response_model=schemas.AvailabilitySlotAttendee)
def decide_on_schedule_availability_slot(
    data: schemas.AvailabilitySlotConfirmation,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to react to owners decision to a request of a time slot of his public link
       if confirmed: create an event in remote calendar and send invitation mail
       TODO: if denied: send information mail to bookee
    """
    subscriber = repo.verify_subscriber_link(db, data.owner_url)
    if not subscriber:
        raise validation.InvalidLinkException()

    # Raise a schedule not found exception if the schedule owner does not have a timezone set.
    if subscriber.timezone is None:
        raise validation.ScheduleNotFoundException()

    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise validation.ScheduleNotFoundException()

    # check if schedule is enabled
    if not schedule.active:
        raise validation.ScheduleNotFoundException()

    # get calendar
    calendar = repo.get_calendar(db, calendar_id=schedule.calendar_id)
    if calendar is None:
        raise validation.CalendarNotFoundException()

    # get slot and check if slot exists and is not booked yet and token is the same
    slot = repo.get_slot(db, data.slot_id)
    if (
        not slot
        or not repo.slot_is_available(db, slot.id)
        or not repo.schedule_has_slot(db, schedule.id, slot.id)
        or slot.booking_tkn != data.slot_token
    ):
        raise validation.SlotNotFoundException()

    # TODO: check booking expiration date
    # check if request was denied
    if data.confirmed is False:
        # human readable date in subscribers timezone
        # TODO: handle locale date representation
        date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(subscriber.timezone)).strftime("%c")
        date = f"{date}, {slot.duration} minutes"
        # send rejection information to bookee
        background_tasks.add_task(send_rejection_email, owner=subscriber, date=date, to=slot.attendee.email)
        # delete the scheduled slot to make the time available again
        repo.delete_slot(db, slot.id)
    # otherwise, confirm slot and create event
    else:
        slot = repo.book_slot(db, slot.id)

        location_url = schedule.location_url

        # FIXME: This is just duplicated from the appointment code. We should find a nice way to merge the two.
        if schedule.meeting_link_provider == MeetingLinkProviderType.zoom:
            try:
                zoom_client = get_zoom_client(subscriber)
                response = zoom_client.create_meeting(schedule.name, slot.start.isoformat(), slot.duration,
                                                      subscriber.timezone)
                if 'id' in response:
                    location_url = zoom_client.get_meeting(response['id'])['join_url']
                    slot.meeting_link_id = response['id']
                    slot.meeting_link_url = location_url

                    db.add(slot)
                    db.commit()
            except HTTPError as err:  # Not fatal, just a bummer
                logging.error("Zoom meeting creation error: ", err)

                # Ensure sentry captures the error too!
                if os.getenv('SENTRY_DSN') != '':
                    capture_exception(err)

                # Notify the organizer that the meeting link could not be created!
                background_tasks.add_task(send_zoom_meeting_failed_email, to=subscriber.email, appointment_title=schedule.name)
            except SQLAlchemyError as err:  # Not fatal, but could make things tricky
                logging.error("Failed to save the zoom meeting link to the appointment: ", err)
                if os.getenv('SENTRY_DSN') != '':
                    capture_exception(err)

        attendee_name = slot.attendee.name if slot.attendee.name is not None else slot.attendee.email
        subscriber_name = subscriber.name if subscriber.name is not None else subscriber.email

        title = f"Appointment - {subscriber_name} and {attendee_name}"

        event = schemas.Event(
            title=title,
            start=slot.start.replace(tzinfo=timezone.utc),
            end=slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration),
            description=schedule.details,
            location=schemas.EventLocation(
                type=schedule.location_type,
                url=location_url,
                name=None,
            ),
        )
        # create remote event
        if calendar.provider == CalendarProvider.google:
            con = GoogleConnector(
                db=db,
                google_client=google_client,
                calendar_id=calendar.user,
                subscriber_id=subscriber.id,
                google_tkn=subscriber.google_tkn,
            )
        else:
            con = CalDavConnector(calendar.url, calendar.user, calendar.password)
        con.create_event(event=event, attendee=slot.attendee, organizer=subscriber)

        # send mail with .ics attachment to attendee
        appointment = schemas.AppointmentBase(title=title, details=schedule.details, location_url=location_url)
        Tools().send_vevent(background_tasks, appointment, slot, subscriber, slot.attendee)

    return schemas.AvailabilitySlotAttendee(
        slot=schemas.SlotBase(start=slot.start, duration=slot.duration),
        attendee=schemas.AttendeeBase(email=slot.attendee.email, name=slot.attendee.name)
    )


@router.put("/serve/ics", response_model=schemas.FileDownload)
def schedule_serve_ics(
    s_a: schemas.AvailabilitySlotAttendee,
    url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """endpoint to serve ICS file for availability time slot to download"""
    subscriber = repo.verify_subscriber_link(db, url)
    if not subscriber:
        raise validation.InvalidLinkException

    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise validation.ScheduleNotFoundException()

    # check if schedule is enabled
    if not schedule.active:
        raise validation.ScheduleNotFoundException()

    # get calendar
    db_calendar = repo.get_calendar(db, calendar_id=schedule.calendar_id)
    if db_calendar is None:
        raise validation.CalendarNotFoundException()

    appointment = schemas.AppointmentBase(title=schedule.name, details=schedule.details, location_url=schedule.location_url)
    return schemas.FileDownload(
        name="invite",
        content_type="text/calendar",
        data=Tools().create_vevent(appointment=appointment, slot=s_a.slot, organizer=subscriber).decode("utf-8"),
    )
