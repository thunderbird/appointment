"""Module: repo

Repository providing CRUD functions for all database models. 
"""
import os
from datetime import timedelta, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas

"""ATTENDEES repository functions"""


def get_attendees_by_subscriber(db: Session, subscriber_id: int):
    """For use with the data download. Get attendees by subscriber id."""
    # We need to walk through Calendars to attach Appointments, and Appointments to get Slots
    slots = db.query(models.Slot) \
        .join(models.Appointment) \
        .join(models.Calendar) \
        .filter(models.Calendar.owner_id == subscriber_id) \
        .filter(models.Appointment.calendar_id == models.Calendar.id) \
        .filter(models.Slot.appointment_id == models.Appointment.id) \
        .all()

    attendee_ids = list(map(lambda slot: slot.attendee_id if slot.attendee_id is not None else None, slots))
    attendee_ids = filter(lambda attendee: attendee is not None, attendee_ids)
    return db.query(models.Attendee).filter(models.Attendee.id.in_(attendee_ids)).all()


def delete_attendees_by_subscriber(db: Session, subscriber_id: int):
    """Delete all attendees by subscriber"""
    attendees = get_attendees_by_subscriber(db, subscriber_id)

    for attendee in attendees:
        db.delete(attendee)
    db.commit()

    return True


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


def get_subscriber_by_appointment(db: Session, appointment_id: int):
    """retrieve appointment by subscriber username and appointment slug (public)"""
    if appointment_id:
        return (
            db.query(models.Subscriber)
            .join(models.Calendar)
            .join(models.Appointment)
            .filter(models.Appointment.id == appointment_id)
            .first()
        )
    return None


def get_subscriber_by_google_state(db: Session, state: str):
    """retrieve subscriber by google state, you'll have to manually check the google_state_expire_at!"""
    if state is None:
        return None
    return db.query(models.Subscriber).filter(models.Subscriber.google_state == state).first()


def create_subscriber(db: Session, subscriber: schemas.SubscriberBase):
    """create new subscriber"""
    db_subscriber = models.Subscriber(**subscriber.dict())
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def update_subscriber(db: Session, data: schemas.SubscriberIn, subscriber_id: int):
    """update all subscriber attributes, they can edit themselves"""
    db_subscriber = get_subscriber(db, subscriber_id)
    for key, value in data:
        setattr(db_subscriber, key, value)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def delete_subscriber(db: Session, subscriber: models.Subscriber):
    """Delete a subscriber by subscriber id"""
    db.delete(subscriber)
    db.commit()
    return True


def set_subscriber_google_tkn(db: Session, tkn: str, subscriber_id: int):
    """update all subscriber attributes, they can edit themselves"""
    db_subscriber = get_subscriber(db, subscriber_id)
    db_subscriber.google_tkn = tkn
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def set_subscriber_google_state(db: Session, state: str | None, subscriber_id: int):
    """temp store the google state so we can refer to it when we get back"""
    db_subscriber = get_subscriber(db, subscriber_id)
    db_subscriber.google_state = state

    if state is None:
        db_subscriber.google_state_expires_at = None
    else:
        db_subscriber.google_state_expires_at = datetime.now() + timedelta(minutes=3)

    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def get_connections_limit(db: Session, subscriber_id: int):
    """return the number of allowed connections for given subscriber or -1 for unlimited connections"""
    db_subscriber = get_subscriber(db, subscriber_id)
    mapping = {
        models.SubscriberLevel.basic: int(os.getenv("TIER_BASIC_CALENDAR_LIMIT")),
        models.SubscriberLevel.plus: int(os.getenv("TIER_PLUS_CALENDAR_LIMIT")),
        models.SubscriberLevel.pro: int(os.getenv("TIER_PRO_CALENDAR_LIMIT")),
        models.SubscriberLevel.admin: -1,
    }
    return mapping[db_subscriber.level]


""" CALENDAR repository functions
"""


def calendar_exists(db: Session, calendar_id: int):
    """true if calendar of given id exists"""
    return True if db.get(models.Calendar, calendar_id) is not None else False


def get_calendar(db: Session, calendar_id: int):
    """retrieve calendar by id"""
    return db.get(models.Calendar, calendar_id)


def get_calendar_by_url(db: Session, url: str):
    """retrieve calendar by calendar url"""
    return db.query(models.Calendar).filter(models.Calendar.url == url).first()


def get_calendars_by_subscriber(db: Session, subscriber_id: int):
    """retrieve list of calendars by owner id"""
    return db.query(models.Calendar).filter(models.Calendar.owner_id == subscriber_id).all()


def create_subscriber_calendar(db: Session, calendar: schemas.CalendarConnection, subscriber_id: int):
    """create new calendar for owner, if not already existing"""
    db_calendar = models.Calendar(**calendar.dict(), owner_id=subscriber_id)
    subscriber_calendars = get_calendars_by_subscriber(db, subscriber_id)
    subscriber_calendar_urls = [c.url for c in subscriber_calendars]
    # check if subscriber already holds this calendar by url
    if db_calendar.url in subscriber_calendar_urls:
        raise HTTPException(status_code=403, detail="Calendar already exists")
    # check subscription limitation
    limit = get_connections_limit(db=db, subscriber_id=subscriber_id)
    if limit > 0 and len(subscriber_calendars) >= limit:
        raise HTTPException(
            status_code=403, detail="Allowed number of calendars has been reached for this subscription"
        )
    # add new calendar
    db.add(db_calendar)
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update_subscriber_calendar(db: Session, calendar: schemas.CalendarConnection, calendar_id: int):
    """update existing calendar by id"""
    db_calendar = get_calendar(db, calendar_id)
    for key, value in calendar:
        # if no password is given, keep existing one
        if not (key == "password" and len(value) == 0):
            setattr(db_calendar, key, value)
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update_or_create_subscriber_calendar(
    db: Session, calendar: schemas.CalendarConnection, calendar_url: str, subscriber_id: int
):
    """update or create a subscriber calendar"""
    subscriber_calendar = get_calendar_by_url(db, calendar_url)

    if subscriber_calendar is None:
        return create_subscriber_calendar(db, calendar, subscriber_id)

    return update_subscriber_calendar(db, calendar, subscriber_calendar.id)


def delete_subscriber_calendar(db: Session, calendar_id: int):
    """remove existing calendar by id"""
    db_calendar = get_calendar(db, calendar_id)
    db.delete(db_calendar)
    db.commit()
    return db_calendar


def delete_subscriber_calendar_by_subscriber_id(db: Session, subscriber_id: int):
    """Delete all calendars by subscriber"""
    calendars = get_calendars_by_subscriber(db, subscriber_id=subscriber_id)
    for calendar in calendars:
        delete_subscriber_calendar(db, calendar_id=calendar.id)
    return True


def calendar_is_owned(db: Session, calendar_id: int, subscriber_id: int):
    """check if calendar belongs to subscriber"""
    return (
        db.query(models.Calendar)
        .filter(models.Calendar.id == calendar_id, models.Calendar.owner_id == subscriber_id)
        .first()
        is not None
    )


""" APPOINTMENT repository functions
"""


def create_calendar_appointment(db: Session, appointment: schemas.AppointmentFull, slots: list[schemas.SlotBase]):
    """create new appointment with slots for calendar"""
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    add_appointment_slots(db, slots, db_appointment.id)
    return db_appointment


def get_appointment(db: Session, appointment_id: int):
    """retrieve appointment by id (private)"""
    if appointment_id:
        return db.get(models.Appointment, appointment_id)
    return None


def get_public_appointment(db: Session, slug: str):
    """retrieve appointment by appointment slug (public)"""
    if slug:
        return db.query(models.Appointment).filter(models.Appointment.slug == slug).first()
    return None


def get_appointments_by_subscriber(db: Session, subscriber_id: int):
    """retrieve list of appointments by owner id"""
    return db.query(models.Appointment).join(models.Calendar).filter(models.Calendar.owner_id == subscriber_id).all()


def appointment_is_owned(db: Session, appointment_id: int, subscriber_id: int):
    """check if appointment belongs to subscriber"""
    db_appointment = get_appointment(db, appointment_id)
    return calendar_is_owned(db, db_appointment.calendar_id, subscriber_id)


def appointment_has_slot(db: Session, appointment_id: int, slot_id: int):
    """check if appointment belongs to subscriber"""
    db_slot = get_slot(db, slot_id)
    return db_slot and db_slot.appointment_id == appointment_id


def update_calendar_appointment(
    db: Session,
    appointment: schemas.AppointmentFull,
    slots: list[schemas.SlotBase],
    appointment_id: int,
):
    """update existing appointment by id"""
    db_appointment = get_appointment(db, appointment_id)
    for key, value in appointment:
        setattr(db_appointment, key, value)
    db.commit()
    db.refresh(db_appointment)
    delete_appointment_slots(db, appointment_id)
    add_appointment_slots(db, slots, appointment_id)
    return db_appointment


def delete_calendar_appointment(db: Session, appointment_id: int):
    """remove existing appointment by id"""
    db_appointment = get_appointment(db, appointment_id)
    db.delete(db_appointment)
    db.commit()
    return db_appointment


def delete_calendar_appointments_by_subscriber_id(db: Session, subscriber_id: int):
    """Delete all appointments by subscriber"""
    appointments = get_appointments_by_subscriber(db, subscriber_id=subscriber_id)
    for appointment in appointments:
        delete_calendar_appointment(db, appointment_id=appointment.id)
    return True


""" SLOT repository functions
"""


def get_slot(db: Session, slot_id: int):
    """retrieve slot by id"""
    if slot_id:
        return db.get(models.Slot, slot_id)
    return None


def get_slots_by_subscriber(db: Session, subscriber_id: int):
    """retrieve slot by subscriber id"""

    # We need to walk through Calendars to attach Appointments, and Appointments to get Slots
    return db.query(models.Slot) \
        .join(models.Appointment) \
        .join(models.Calendar) \
        .filter(models.Calendar.owner_id == subscriber_id) \
        .filter(models.Appointment.calendar_id == models.Calendar.id) \
        .filter(models.Slot.appointment_id == models.Appointment.id) \
        .all()


def add_appointment_slots(db: Session, slots: list[schemas.SlotBase], appointment_id: int):
    """create new slots for appointment of given id"""
    for slot in slots:
        db_slot = models.Slot(**slot.dict())
        db_slot.appointment_id = appointment_id
        db.add(db_slot)
    db.commit()
    return slots


def delete_appointment_slots(db: Session, appointment_id: int):
    """delete all slots for appointment of given id"""
    return db.query(models.Slot).filter(models.Slot.appointment_id == appointment_id).delete()


def delete_appointment_slots_by_subscriber_id(db: Session, subscriber_id: int):
    """Delete all slots by subscriber"""
    slots = get_slots_by_subscriber(db, subscriber_id)

    for slot in slots:
        db.delete(slot)
    db.commit()

    return True


def update_slot(db: Session, slot_id: int, attendee: schemas.Attendee):
    """update existing slot by id and create corresponding attendee"""
    # create attendee
    db_attendee = models.Attendee(**attendee.dict())
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    # update slot
    db_slot = get_slot(db, slot_id)
    setattr(db_slot, "attendee_id", db_attendee.id)
    db.commit()
    return db_attendee


def slot_is_available(db: Session, slot_id: int):
    """check if slot is still available"""
    db_slot = get_slot(db, slot_id)
    return db_slot and not db_slot.attendee_id and not db_slot.subscriber_id
