from fastapi import APIRouter, Depends, HTTPException, Body
import logging

from sqlalchemy.orm import Session
from ..controller.calendar import Tools
from ..database import repo, schemas
from ..database.models import Subscriber, Schedule
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Schedule)
def create_calendar_schedule(
    schedule: schemas.ScheduleBase, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)
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
    """Gets all of the available schedules for the logged in subscriber (only one for the time being)"""
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
def read_schedule_availabilities(url: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Returns the calculated availability for the first schedule from a subscribers public profile link"""
    subscriber = repo.verify_subscriber_link(db, url)
    if not subscriber:
        raise HTTPException(status_code=401, detail="Invalid profile link")
    schedules = repo.get_schedules_by_subscriber(db, subscriber_id=subscriber.id)
    try:
        schedule = schedules[0]  # for now we only process the first existing schedule
    except KeyError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    availableSlots = Tools.available_slots_from_schedule(schedule)
    existingEvents = []  # TODO: get events from connected calendar in scheduled date range
    return schemas.AppointmentOut(
        title=schedule.name,
        details=schedule.details,
        owner_name=subscriber.name,
        slots=Tools.events_set_difference(availableSlots, existingEvents),
    )
