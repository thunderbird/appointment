"""Module: repo.schedule

Repository providing CRUD functions for schedule database models. 
"""

from sqlalchemy.orm import Session
from .. import models, schemas, repo


def create(db: Session, schedule: schemas.ScheduleBase):
    """create a new schedule with slots for calendar"""
    db_schedule = models.Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_by_subscriber(db: Session, subscriber_id: int):
    """Get schedules by subscriber id"""
    return (
        db.query(models.Schedule)
        .join(models.Calendar, models.Schedule.calendar_id == models.Calendar.id)
        .filter(models.Calendar.owner_id == subscriber_id)
        .all()
    )


def get_by_slug(db: Session, slug: str):
    """Get schedule by slug"""
    return db.query(models.Schedule).filter(models.Schedule.slug == slug).first()

def get(db: Session, schedule_id: int):
    """retrieve schedule by id"""
    if schedule_id:
        return db.get(models.Schedule, schedule_id)
    return None


def is_owned(db: Session, schedule_id: int, subscriber_id: int):
    """check if the given schedule belongs to subscriber"""
    schedules = get_by_subscriber(db, subscriber_id)
    return any(s.id == schedule_id for s in schedules)


def exists(db: Session, schedule_id: int):
    """true if schedule of given id exists"""
    return True if get(db, schedule_id) is not None else False


def is_calendar_connected(db: Session, schedule_id: int) -> bool:
    """true if the schedule's calendar is connected"""
    schedule: models.Schedule = get(db, schedule_id)
    return schedule.calendar and schedule.calendar.connected


def update(db: Session, schedule: schemas.ScheduleBase, schedule_id: int):
    """update existing schedule by id"""
    db_schedule = get(db, schedule_id)
    for key, value in schedule:
        setattr(db_schedule, key, value)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_availability(db: Session, schedule_id: int):
    """retrieve availability by schedule id"""
    return db.query(models.Availability).filter(models.Availability.schedule_id == schedule_id).all()


def has_slot(db: Session, schedule_id: int, slot_id: int):
    """check if slot belongs to schedule"""
    db_slot = repo.slot.get(db, slot_id)
    return db_slot and db_slot.schedule_id == schedule_id
