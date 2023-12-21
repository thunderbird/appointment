
from fastapi import APIRouter, Depends, HTTPException, Body
import logging
import os

from requests import HTTPError
from sentry_sdk import capture_exception
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..controller.calendar import CalDavConnector, Tools, GoogleConnector
from ..controller.apis.google_client import GoogleClient
from ..controller.mailer import ConfirmationMail, RejectionMail, ZoomMeetingFailedMail
from ..controller.auth import signed_url_by_subscriber
from ..database import repo, schemas
from ..database.models import Subscriber, CalendarProvider, random_slug, BookingStatus, MeetingLinkProviderType, ExternalConnectionType
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db
from ..dependencies.google import get_google_client
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from ..dependencies.zoom import get_zoom_client
from ..exceptions.validation import CalendarNotFoundException, CalendarNotAuthorizedException, ScheduleNotFoundException, \
    ScheduleNotAuthorizedException, ZoomNotConnectedException, CalendarNotConnectedException
from ..l10n import l10n

router = APIRouter()


@router.post("/", response_model=schemas.Schedule)
def create_calendar_schedule(
    schedule: schemas.ScheduleBase,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to add a new schedule for a given calendar"""
    if not repo.calendar_exists(db, calendar_id=schedule.calendar_id):
        raise CalendarNotFoundException()
    if not repo.calendar_is_owned(db, calendar_id=schedule.calendar_id, subscriber_id=subscriber.id):
        raise CalendarNotAuthorizedException()
    if not repo.calendar_is_connected(db, calendar_id=schedule.calendar_id):
        raise CalendarNotConnectedException()
    return repo.create_calendar_schedule(db=db, schedule=schedule)


@router.get("/", response_model=list[schemas.Schedule])
def read_schedules(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Gets all of the available schedules for the logged in subscriber"""
    return repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)


@router.get("/{id}", response_model=schemas.Schedule)
def read_schedule(
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Gets information regarding a specific schedule"""
    schedule = repo.get_schedule(db, schedule_id=id)
    if schedule is None:
        raise ScheduleNotFoundException()
    if not repo.schedule_is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise ScheduleNotAuthorizedException()
    return schedule


@router.put("/{id}", response_model=schemas.Schedule)
def update_schedule(
    id: int,
    schedule: schemas.ScheduleBase,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not repo.schedule_exists(db, schedule_id=id):
        raise ScheduleNotFoundException()
    if not repo.schedule_is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise ScheduleNotAuthorizedException()
    if schedule.meeting_link_provider == MeetingLinkProviderType.zoom and subscriber.get_external_connection(ExternalConnectionType.zoom) is None:
        raise ZoomNotConnectedException()
    return repo.update_calendar_schedule(db=db, schedule=schedule, schedule_id=id)


@router.post("/public/availability", response_model=schemas.AppointmentOut)
def read_schedule_availabilities(
    url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
):
    """Returns the calculated availability for the first schedule from a subscribers public profile link"""
    subscriber = repo.verify_subscriber_link(db, url)
    if not subscriber:
        raise HTTPException(status_code=401, detail=l10n('invalid-link'))
    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)

    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise ScheduleNotFoundException()

    # check if schedule is enabled
    if not schedule.active:
        raise ScheduleNotFoundException()

    # calculate theoretically possible slots from schedule config
    availableSlots = Tools.available_slots_from_schedule(schedule)

    # get all events from all connected calendars in scheduled date range
    calendars = repo.get_calendars_by_subscriber(db, subscriber.id, False)

    if not calendars or len(calendars) == 0:
        raise HTTPException(status_code=404, detail="No calendars found")

    existingEvents = Tools.existing_events_for_schedule(schedule, calendars, subscriber, google_client, db)
    actualSlots = Tools.events_set_difference(availableSlots, existingEvents)

    if not actualSlots or len(actualSlots) == 0:
        raise HTTPException(status_code=404, detail="No possible booking slots found")

    return schemas.AppointmentOut(
        title=schedule.name,
        details=schedule.details,
        owner_name=subscriber.name,
        slots=actualSlots,
    )


@router.put("/public/availability/request")
def request_schedule_availability_slot(
    s_a: schemas.AvailabilitySlotAttendee,
    url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """endpoint to request a time slot for a schedule via public link and send confirmation mail to owner"""
    subscriber = repo.verify_subscriber_link(db, url)
    if not subscriber:
        raise HTTPException(status_code=401, detail="Invalid profile link")
    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # check if schedule is enabled
    if not schedule.active:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # get calendar
    db_calendar = repo.get_calendar(db, calendar_id=schedule.calendar_id)
    if db_calendar is None:
        raise HTTPException(status_code=404, detail="Calendar not found")

    # check if slot still available, might already be taken at this time
    slot = schemas.SlotBase(**s_a.slot.dict())
    if repo.schedule_slot_exists(db, slot, schedule.id):
        raise HTTPException(status_code=403, detail="Slot not available")

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
    # send confirmation mail to owner
    mail = ConfirmationMail(
        f"{url}/1",
        f"{url}/0",
        attendee,
        f"{date}, {slot.duration} minutes",
        to=subscriber.email
    )
    mail.send()
    return True


@router.put("/public/availability/booking", response_model=schemas.AvailabilitySlotAttendee)
def decide_on_schedule_availability_slot(
    data: schemas.AvailabilitySlotConfirmation,
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to react to owners decision to a request of a time slot of his public link
       if confirmed: create an event in remote calendar and send invitation mail
       TODO: if denied: send information mail to bookee
    """
    subscriber = repo.verify_subscriber_link(db, data.owner_url)
    if not subscriber:
        raise HTTPException(status_code=401, detail="Invalid profile link")
    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # check if schedule is enabled
    if not schedule.active:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # get calendar
    calendar = repo.get_calendar(db, calendar_id=schedule.calendar_id)
    if calendar is None:
        raise HTTPException(status_code=404, detail="Calendar not found")
    # get slot and check if slot exists and is not booked yet and token is the same
    slot = repo.get_slot(db, data.slot_id)
    if (
        not slot
        or not repo.slot_is_available(db, slot.id)
        or not repo.schedule_has_slot(db, schedule.id, slot.id)
        or slot.booking_tkn != data.slot_token
    ):
        raise HTTPException(status_code=404, detail="Booking slot not found")
    # TODO: check booking expiration date
    # check if request was denied
    if data.confirmed is False:
        # human readable date in subscribers timezone
        # TODO: handle locale date representation
        date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(subscriber.timezone)).strftime("%c")
        # send rejection information to bookee
        mail = RejectionMail(
            owner=subscriber,
            date=f"{date}, {slot.duration} minutes",
            to=slot.attendee.email
        )
        mail.send()
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
                mail = ZoomMeetingFailedMail(to=subscriber.email,
                                             appointment_title=schedule.name)
                mail.send()
            except SQLAlchemyError as err:  # Not fatal, but could make things tricky
                logging.error("Failed to save the zoom meeting link to the appointment: ", err)
                if os.getenv('SENTRY_DSN') != '':
                    capture_exception(err)

        event = schemas.Event(
            title=schedule.name,
            start=slot.start.replace(tzinfo=timezone.utc).isoformat(),
            end=(slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration)).isoformat(),
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
        appointment = schemas.AppointmentBase(title=schedule.name, details=schedule.details, location_url=location_url)
        Tools().send_vevent(appointment, slot, subscriber, slot.attendee)

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
        raise HTTPException(status_code=401, detail="Invalid profile link")
    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # check if schedule is enabled
    if not schedule.active:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # get calendar
    db_calendar = repo.get_calendar(db, calendar_id=schedule.calendar_id)
    if db_calendar is None:
        raise HTTPException(status_code=404, detail="Calendar not found")

    appointment = schemas.AppointmentBase(title=schedule.name, details=schedule.details, location_url=schedule.location_url)
    return schemas.FileDownload(
        name="invite",
        content_type="text/calendar",
        data=Tools().create_vevent(appointment=appointment, slot=s_a.slot, organizer=subscriber).decode("utf-8"),
    )
