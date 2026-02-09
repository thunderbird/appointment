"""Module: repo.schedule

Repository providing CRUD functions for schedule database models.
"""

import uuid
import zoneinfo

from datetime import datetime, time, timezone
from sqlalchemy.orm import Session
from .. import models, schemas, repo
from ... import utils
from ...controller.auth import signed_url_by_subscriber


def create(db: Session, schedule: schemas.ScheduleBase):
    """create a new schedule with slots for calendar"""
    db_schedule = models.Schedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_by_subscriber(db: Session, subscriber_id: int) -> list[models.Schedule]:
    """Get schedules by subscriber id"""
    return (
        db.query(models.Schedule)
        .join(models.Calendar, models.Schedule.calendar_id == models.Calendar.id)
        .filter(models.Calendar.owner_id == subscriber_id)
        .all()
    )


def get_by_slug(db: Session, slug: str, subscriber_id: int) -> models.Schedule | None:
    """Get schedule by slug"""
    return (
        db.query(models.Schedule)
        .filter(models.Schedule.slug == slug)
        .join(models.Schedule.calendar)
        .filter(models.Calendar.owner_id == subscriber_id)
        .first()
    )


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
        if key == 'availabilities':
            # If we have custom availabilities and they are activated, save them
            repo.availability.sync_multiple(db, schedule.availabilities, schedule_id)
            continue
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


def all_availability_is_valid(schedule: schemas.ScheduleValidationIn):
    """check if availability is valid"""
    size = len(schedule.availabilities)
    if size <= 0:
        return True

    # The frontend converts local times to UTC before sending. We need to convert
    # back to the schedule's local timezone for validation, because UTC times may
    # cross midnight boundaries (e.g. 5pm-7pm CST-6 becomes 23:00-01:00 UTC).
    tz = schedule.timezone or 'UTC'
    tz_info = zoneinfo.ZoneInfo(tz)

    def to_local_time(utc_time: time) -> time:
        """Convert a UTC time to the schedule's local timezone."""
        utc_dt = datetime.combine(schedule.start_date, utc_time, tzinfo=timezone.utc)
        local_dt = utc_dt.astimezone(tz_info)
        return local_dt.time()

    # Make sure, that the availabilities are sorted by weekday AND by start time. This is important for checking
    # validity of times of adjacent availabilities at the same day
    availabilities = sorted(schedule.availabilities, key=lambda x: (x.day_of_week.value, to_local_time(x.start_time)))
    for i, a in enumerate(availabilities):
        local_start = to_local_time(a.start_time)
        local_end = to_local_time(a.end_time)

        # Check valid times (start time before end time) and duration (end time at least x minutes after start)
        if not utils.is_valid_time_range(local_start, local_end, schedule.slot_duration):
            return False
        # If a previous slot exists on that day, fail if the times overlap
        if (
            i > 0
            and (a.day_of_week.value == availabilities[i - 1].day_of_week.value)
            and not utils.is_valid_time_range(to_local_time(availabilities[i - 1].end_time), local_start)
        ):
            return False
        # If a next slot exists on that day, fail if the times overlap
        if (
            i < size - 1
            and (a.day_of_week.value == availabilities[i + 1].day_of_week.value)
            and not utils.is_valid_time_range(local_end, to_local_time(availabilities[i + 1].start_time))
        ):
            return False

    return True


def generate_slug(db: Session, schedule_id: int) -> str | None:
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

    # If we're a signed url, then early exit here to avoid slug checks
    is_signed_url = signed_url_by_subscriber(subscriber) == url
    if is_signed_url:
        return subscriber

    if slug:
        schedule = get_by_slug(db, slug, subscriber.id)

        if not schedule:
            return None
    elif not slug:
        schedules = get_by_subscriber(db, subscriber.id)

        # If there's no schedules (we can't display anything)
        # or if there's a slug in the first schedule, but it's not provided (upper condition)
        # then error out!
        if not schedules or schedules[0].slug:
            return None

    return subscriber
