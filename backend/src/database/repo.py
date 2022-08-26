"""Module: repo

Repository providing CRUD functions for all database models. 
"""
from sqlalchemy.orm import Session
from . import models, schemas


""" SUBSCRIBERS repository functions
"""
def get_subscriber(db: Session, subscriber_id: int):
  """retrieve subscriber by id"""
  return db.get(models.Subscriber, subscriber_id)


def get_subscriber_by_email(db: Session, email: str):
  """retrieve subscriber by email"""
  return db.query(models.Subscriber).filter(models.Subscriber.email == email).first()


def get_subscriber_by_username(db: Session, username: str):
  """retrieve subscriber by username"""
  return db.query(models.Subscriber).filter(models.Subscriber.username == username).first()


def create_subscriber(db: Session, subscriber: schemas.SubscriberCreate):
  """create new subscriber"""
  db_subscriber = models.Subscriber(**subscriber.dict())
  db.add(db_subscriber)
  db.commit()
  db.refresh(db_subscriber)
  return db_subscriber


def update_subscriber(db: Session, subscriber: dict, subscriber_id: int):
  """update existing subscriber by id"""
  db_subscriber = get_subscriber(db, subscriber_id)
  for key, value in subscriber.items():
    if hasattr(db_subscriber, key):
      setattr(db_subscriber, key, value)
  db.commit()
  return db_subscriber


""" CALENDAR repository functions
"""
def get_calendar(db: Session, calendar_id: int):
  """retrieve calendar by id"""
  return db.get(models.Calendar, calendar_id)


def get_calendars_by_subscriber(db: Session, subscriber_id: int):
  """retrieve list of calendars by owner id"""
  return db.query(models.Calendar).filter(models.Calendar.owner_id == subscriber_id).all()


def create_subscriber_calendar(db: Session, calendar: schemas.CalendarCreate, subscriber_id: int):
  """create new calendar for owner"""
  hashed = calendar.password # TODO: hashing/encrypting
  db_calendar = models.Calendar(url=calendar.url, user=calendar.user, password=hashed, owner_id=subscriber_id)
  db.add(db_calendar)
  db.commit()
  db.refresh(db_calendar)
  return db_calendar


def update_subscriber_calendar(db: Session, calendar: dict, calendar_id: int):
  """update existing calendar by id"""
  db_calendar = get_calendar(db, calendar_id)
  for key, value in calendar.items():
    if hasattr(db_calendar, key):
      setattr(db_calendar, key, value)
  db.commit()
  return db_calendar


def delete_subscriber_calendar(db: Session, calendar_id: int):
  """remove existing calendar by id"""
  db_calendar = get_calendar(db, calendar_id)
  db.delete(db_calendar)
  db.commit()
  return db_calendar


def calendar_is_owned(db: Session, calendar_id: int, subscriber_id: int):
  """check if calendar belongs to subscriber"""
  return db.query(models.Calendar).filter(
    models.Calendar.id == calendar_id,
    models.Calendar.owner_id == subscriber_id
  ).first() is not None
