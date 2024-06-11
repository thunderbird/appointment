"""Module: repo.schedule

Repository providing CRUD functions for schedule database models. 
"""
import uuid

from sqlalchemy.orm import Session
from .. import models, schemas, repo
from ... import utils


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


def get_by_slug(db: Session, slug: str, subscriber_id: int) -> models.Schedule | None:
    """Get schedule by slug"""
    return (db.query(models.Schedule)
            .filter(models.Schedule.slug == slug)
            .join(models.Schedule.calendar)
            .filter(models.Calendar.owner_id == subscriber_id)
            .first())


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


def generate_slug(db: Session, schedule_id: int) -> str|None:
    schedule = repo.schedule.get(db, schedule_id)

    if schedule.slug:
        return schedule.slug

    owner_id = schedule.owner.id

    # If slug isn't provided, give them the last 8 characters from a uuid4
    # Try up-to-3 times to create a unique slug
    for _ in range(3):
        slug = uuid.uuid4().hex[-8:]
        exists = repo.schedule.get_by_slug(db, slug, owner_id)
        if not exists:
            schedule.slug = slug
            break

    # Could not create slug due to randomness overlap
    if schedule.slug is None:
        return None

    db.add(schedule)
    db.commit()

    return schedule.slug


def hard_delete(db: Session, schedule_id: int):
    schedule = repo.schedule.get(db, schedule_id)
    db.delete(schedule)
    db.commit()

    return True


def verify_link(db: Session, url: str) -> models.Subscriber | None:
    """Verifies that an url belongs to a subscriber's schedule, and if so return the subscriber.
    Otherwise, return none."""
    username, slug, clean_url = utils.retrieve_user_url_data(url)
    subscriber = repo.subscriber.get_by_username(db, username)
    if not subscriber:
        return None

    schedule = get_by_slug(db, slug, subscriber.id)

    if not schedule:
        return None

    return subscriber
