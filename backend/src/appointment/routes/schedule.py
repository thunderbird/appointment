from fastapi import APIRouter, Depends, HTTPException, Body
import logging

from sqlalchemy.orm import Session
from ..controller.calendar import CalDavConnector, Tools, GoogleConnector
from ..controller.apis.google_client import GoogleClient
from ..database import repo, schemas
from ..database.models import Subscriber, Schedule, CalendarProvider
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db
from ..dependencies.google import get_google_client
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/", response_model=schemas.Schedule)
def create_calendar_schedule(
    schedule: schemas.ScheduleBase,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to add a new schedule for a given calendar"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if not repo.calendar_exists(db, calendar_id=schedule.calendar_id):
        raise HTTPException(status_code=404, detail="Calendar not found")
    if not repo.calendar_is_owned(db, calendar_id=schedule.calendar_id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
    if not repo.calendar_is_connected(db, calendar_id=schedule.calendar_id):
        raise HTTPException(status_code=403, detail="Calendar connection is not active")
    return repo.create_calendar_schedule(db=db, schedule=schedule)


@router.get("/", response_model=list[schemas.Schedule])
def read_schedules(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Gets all of the available schedules for the logged in subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    return repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)


@router.get("/{id}", response_model=schemas.Schedule)
def read_schedule(
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Gets information regarding a specific schedule"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    schedule = repo.get_schedule(db, schedule_id=id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if not repo.schedule_is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Schedule not owned by subscriber")
    return schedule


@router.put("/{id}", response_model=schemas.Schedule)
def update_schedule(
    id: int,
    schedule: schemas.ScheduleBase,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    if not repo.schedule_exists(db, schedule_id=id):
        raise HTTPException(status_code=404, detail="Schedule not found")
    if not repo.schedule_is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Schedule not owned by subscriber")
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
        raise HTTPException(status_code=401, detail="Invalid profile link")
    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except IndexError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # check if schedule is enabled
    if not schedule.active:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # calculate theoretically possible slots from schedule config
    availableSlots = Tools.available_slots_from_schedule(schedule)
    # get all events from all connected calendars in scheduled date range
    existingEvents = []
    calendars = repo.get_calendars_by_subscriber(db, subscriber.id, False)
    if not calendars or len(calendars) == 0:
        raise HTTPException(status_code=404, detail="No calendars found")
    for calendar in calendars:
        if calendar is None:
            raise HTTPException(status_code=404, detail="Calendar not found")
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
        farthest_end = datetime.utcnow() + timedelta(minutes=schedule.farthest_booking)
        start = schedule.start_date.strftime("%Y-%m-%d")
        end = schedule.end_date.strftime("%Y-%m-%d") if schedule.end_date else farthest_end.strftime("%Y-%m-%d")
        existingEvents.extend(con.list_events(start, end))
    actualSlots = Tools.events_set_difference(availableSlots, existingEvents)
    if not actualSlots or len(actualSlots) == 0:
        raise HTTPException(status_code=404, detail="No possible booking slots found")
    return schemas.AppointmentOut(
        title=schedule.name,
        details=schedule.details,
        owner_name=subscriber.name,
        slots=actualSlots,
    )


@router.put("/public/availability", response_model=schemas.AvailabilitySlotAttendee)
def update_schedule_availability_slot(
    s_a: schemas.AvailabilitySlotAttendee,
    url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    google_client: GoogleClient = Depends(get_google_client),
):
    """endpoint to update a time slot for a schedule via public link and create an event in remote calendar"""
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
    event = schemas.Event(
        title=schedule.name,
        start=s_a.slot.start.isoformat(),
        end=(s_a.slot.start + timedelta(minutes=s_a.slot.duration)).isoformat(),
        description=schedule.details,
        location=schemas.EventLocation(
            type=schedule.location_type,
            url=schedule.location_url,
            name=None,
        ),
    )
    # create remote event
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
    con.create_event(event=event, attendee=s_a.attendee, organizer=subscriber)

    # send mail with .ics attachment to attendee
    appointment = schemas.AppointmentBase(title=schedule.name, details=schedule.details)
    Tools().send_vevent(appointment, s_a.slot, subscriber, s_a.attendee)

    return s_a


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
    appointment = schemas.AppointmentBase(title=schedule.name, details=schedule.details)
    return schemas.FileDownload(
        name="invite",
        content_type="text/calendar",
        data=Tools().create_vevent(appointment=appointment, slot=s_a.slot, organizer=subscriber).decode("utf-8"),
    )
