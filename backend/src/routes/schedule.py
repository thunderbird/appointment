from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
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
def read_schedules(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
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


@router.get("/{id}/availability", response_model=list[schemas.Availability])
def read_schedule_availabilities(
    id: int,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Returns the calculated availability for a given schedule"""
    # TODO calculate availability given schedule config and existing calendar events
    # create GeneralAppointment model to provide calculated data to booking page
    if not subscriber:
        raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
    schedule = repo.get_schedule(db, schedule_id=id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if not repo.schedule_is_owned(db, schedule_id=id, subscriber_id=subscriber.id):
        raise HTTPException(status_code=403, detail="Schedule not owned by subscriber")
    return repo.get_availability_by_schedule(db, schedule_id=id)
