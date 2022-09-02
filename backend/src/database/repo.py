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


def create_subscriber(db: Session, subscriber: schemas.SubscriberBase):
  """create new subscriber"""
  db_subscriber = models.Subscriber(**subscriber.dict())
  db.add(db_subscriber)
  db.commit()
  db.refresh(db_subscriber)
  return db_subscriber


def update_subscriber(db: Session, subscriber: schemas.SubscriberBase, subscriber_id: int):
  """update existing subscriber by id"""
  db_subscriber = get_subscriber(db, subscriber_id)
  for key, value in subscriber:
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


def create_subscriber_calendar(db: Session, calendar: schemas.CalendarBase, subscriber_id: int):
  """create new calendar for owner"""
  hashed = calendar.password # TODO: hashing/encrypting
  db_calendar = models.Calendar(url=calendar.url, user=calendar.user, password=hashed, owner_id=subscriber_id)
  db.add(db_calendar)
  db.commit()
  db.refresh(db_calendar)
  return db_calendar


def update_subscriber_calendar(db: Session, calendar: schemas.CalendarBase, calendar_id: int):
  """update existing calendar by id"""
  db_calendar = get_calendar(db, calendar_id)
  for key, value in calendar:
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


def create_calendar_appointment(db: Session, appointment: schemas.AppointmentBase, slots: list[schemas.SlotBase]):
  """create new appointment with slots for calendar"""
  db_appointment = models.Appointment(**appointment.dict())
  db.add(db_appointment)
  db.commit()
  db.refresh(db_appointment)
  add_slots(db, slots, db_appointment.id)
  return db_appointment


""" APPOINTMENT repository functions
"""
def get_appointment(db: Session, appointment_id: int = None, appointment_slug: str = None):
  """retrieve appointment by id"""
  if appointment_id:
    return db.get(models.Appointment, appointment_id)
  if appointment_slug:
    return db.query(models.Appointment).filter(models.Appointment.slug == appointment_slug).first()
  return None


def get_appointments_by_subscriber(db: Session, subscriber_id: int):
  """retrieve list of appointments by owner id"""
  return db.query(models.Appointment).join(models.Calendar).filter(models.Calendar.owner_id == subscriber_id).all()


def appointment_is_owned(db: Session, appointment_id: int, subscriber_id: int):
  """check if appointment belongs to subscriber"""
  db_appointment = get_appointment(db, appointment_id)
  return calendar_is_owned(db, db_appointment.calendar_id, subscriber_id)


def update_calendar_appointment(db: Session, appointment: schemas.AppointmentBase, slots: list[schemas.SlotBase],
                                appointment_id: int):
  """update existing appointment by id"""
  db_appointment = get_appointment(db, appointment_id)
  for key, value in appointment:
    setattr(db_appointment, key, value)
  db.commit()
  delete_slots(db, appointment_id)
  add_slots(db, slots, appointment_id)
  return db_appointment


def delete_calendar_appointment(db: Session, appointment_id: int):
  """remove existing appointment by id"""
  db_appointment = get_appointment(db, appointment_id)
  db.delete(db_appointment)
  db.commit()
  return db_appointment


""" SLOT repository functions
"""
def add_slots(db: Session, slots: list[schemas.SlotBase], appointment_id: int):
  """create new slots for appointment of given id"""
  for slot in slots:
    db_slot = models.Slot(**slot.dict())
    db_slot.appointment_id = appointment_id
    db.add(db_slot)
  db.commit()
  return slots


def delete_slots(db: Session, appointment_id: int):
  """delete all slots for appointment of given id"""
  return db.query(models.Slot).filter(models.Slot.appointment_id == appointment_id).delete()
