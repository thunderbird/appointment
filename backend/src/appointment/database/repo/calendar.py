"""Module: repo.calendar

Repository providing CRUD functions for calendar database models.
"""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, repo


def exists(db: Session, calendar_id: int):
    """true if calendar of given id exists"""
    return True if db.get(models.Calendar, calendar_id) is not None else False


def is_owned(db: Session, calendar_id: int, subscriber_id: int):
    """check if calendar belongs to subscriber"""
    return (
        db.query(models.Calendar)
        .filter(models.Calendar.id == calendar_id, models.Calendar.owner_id == subscriber_id)
        .first()
        is not None
    )


def get(db: Session, calendar_id: int):
    """retrieve calendar by id"""
    return db.get(models.Calendar, calendar_id)


def is_connected(db: Session, calendar_id: int):
    """true if calendar of given id exists"""
    return get(db, calendar_id).connected


def get_by_url(db: Session, url: str):
    """retrieve calendar by calendar url"""
    return db.query(models.Calendar).filter(models.Calendar.url == url).first()


def get_by_subscriber(db: Session, subscriber_id: int, include_unconnected: bool = True):
    """retrieve list of calendars by owner id"""
    query = db.query(models.Calendar).filter(models.Calendar.owner_id == subscriber_id)

    if not include_unconnected:
        query = query.filter(models.Calendar.connected == 1)

    return query.all()


def create(db: Session, calendar: schemas.CalendarConnection, subscriber_id: int):
    """create new calendar for owner, if not already existing"""
    db_calendar = models.Calendar(**calendar.dict(), owner_id=subscriber_id)
    subscriber_calendars = get_by_subscriber(db, subscriber_id)
    subscriber_calendar_urls = [c.url for c in subscriber_calendars]
    # check if subscriber already holds this calendar by url
    if db_calendar.url in subscriber_calendar_urls:
        raise HTTPException(status_code=403, detail='Calendar already exists')
    # add new calendar
    db.add(db_calendar)
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update(db: Session, calendar: schemas.CalendarConnection, calendar_id: int):
    """update existing calendar by id"""
    db_calendar = get(db, calendar_id)

    # list of all attributes that must never be updated
    # # because they have dedicated update functions for security reasons
    ignore = ['connected', 'connected_at']
    # list of all attributes that will keep their current value if None is passed
    keep_if_none = ['password']

    for key, value in calendar:
        # skip update, if attribute is ignored or current value should be kept if given value is falsey/empty
        if key in ignore or (key in keep_if_none and (not value or len(str(value)) == 0)):
            continue

        setattr(db_calendar, key, value)

    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update_connection(db: Session, is_connected: bool, calendar_id: int):
    """Updates the connected status of a calendar"""
    db_calendar = get(db, calendar_id)
    # check subscription limitation on connecting
    if is_connected:
        subscriber_calendars = get_by_subscriber(db, db_calendar.owner_id)
        connected_calendars = [calendar for calendar in subscriber_calendars if calendar.connected]
        limit = repo.subscriber.get_connections_limit(db=db, subscriber_id=db_calendar.owner_id)
        if limit > 0 and len(connected_calendars) >= limit:
            raise HTTPException(
                status_code=403, detail='Allowed number of connected calendars has been reached for this subscription'
            )
    if not db_calendar.connected:
        db_calendar.connected_at = datetime.now()
    elif db_calendar.connected and is_connected is False:
        db_calendar.connected_at = None
    db_calendar.connected = is_connected
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update_or_create(db: Session, calendar: schemas.CalendarConnection, calendar_url: str, subscriber_id: int):
    """update or create a subscriber calendar"""
    subscriber_calendar = get_by_url(db, calendar_url)

    if subscriber_calendar is None:
        return create(db, calendar, subscriber_id)

    return update(db, calendar, subscriber_calendar.id)


def delete(db: Session, calendar_id: int):
    """remove existing calendar by id"""
    db_calendar = get(db, calendar_id)
    db.delete(db_calendar)
    db.commit()
    return db_calendar


def delete_by_subscriber(db: Session, subscriber_id: int):
    """Delete all calendars by subscriber"""
    calendars = get_by_subscriber(db, subscriber_id=subscriber_id)
    for calendar in calendars:
        delete(db, calendar_id=calendar.id)
    return True


def delete_by_subscriber_and_provider(db: Session, subscriber_id: int, provider: models.CalendarProvider):
    """Delete all subscriber's calendar by a provider"""
    calendars = get_by_subscriber(db, subscriber_id=subscriber_id)
    for calendar in calendars:
        if calendar.provider == provider:
            delete(db, calendar_id=calendar.id)

    return True
