from sqlalchemy.orm import Session

from . import models, schemas


def get_subscriber(db: Session, subscriber_id: int):
  return db.query(models.Subscriber).filter(models.Subscriber.id == subscriber_id).first()


def get_subscriber_by_email(db: Session, email: str):
  return db.query(models.Subscriber).filter(models.Subscriber.email == email).first()


def get_subscriber_by_username(db: Session, username: str):
  return db.query(models.Subscriber).filter(models.Subscriber.username == username).first()


def create_subscriber(db: Session, subscriber: schemas.SubscriberCreate):
  db_subscriber = models.Subscriber(**subscriber.dict())
  db.add(db_subscriber)
  db.commit()
  db.refresh(db_subscriber)
  return db_subscriber


def get_calendar_by_subscriber(db: Session, subscriber_id: int):
  return db.query(models.Calendar).filter(models.Calendar.owner_id == subscriber_id).all()


def create_subscriber_calendar(db: Session, calendar: schemas.CalendarCreate, subscriber_id: int):
  hashed = calendar.password # TODO: hashing/encrypting
  db_calendar = models.Calendar(url=calendar.url, user=calendar.user, password=hashed, owner_id=subscriber_id)
  db.add(db_calendar)
  db.commit()
  db.refresh(db_calendar)
  return db_calendar
