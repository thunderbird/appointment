"""Module: repo.slot

Repository providing CRUD functions for slot database models. 
"""

from sqlalchemy.orm import Session
from .. import models, schemas, repo


""" SLOT repository functions
"""


def get(db: Session, slot_id: int) -> models.Slot | None:
    """retrieve slot by id"""
    if slot_id:
        return db.get(models.Slot, slot_id)
    return None


def get_by_subscriber(db: Session, subscriber_id: int):
    """retrieve list of slots by subscriber id"""

    # We need to walk through Calendars to attach Appointments, and Appointments to get Slots
    return (
        db.query(models.Slot)
        .join(models.Appointment)
        .join(models.Calendar)
        .filter(models.Calendar.owner_id == subscriber_id)
        .filter(models.Appointment.calendar_id == models.Calendar.id)
        .filter(models.Slot.appointment_id == models.Appointment.id)
        .all()
    )


def add_for_appointment(db: Session, slots: list[schemas.SlotBase], appointment_id: int):
    """create new slots for appointment of given id"""
    for slot in slots:
        db_slot = models.Slot(**slot.dict())
        db_slot.appointment_id = appointment_id
        db.add(db_slot)
    db.commit()
    return slots


def add_for_schedule(db: Session, slot: schemas.SlotBase, schedule_id: int):
    """create new slot for schedule of given id"""
    db_slot = models.Slot(**slot.dict())
    db_slot.schedule_id = schedule_id
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot


def exists_on_schedule(db: Session, slot: schemas.SlotBase, schedule_id: int):
    """check if given slot already exists for schedule of given id"""
    db_slot = (
        db.query(models.Slot)
            .filter(models.Slot.schedule_id == schedule_id)
            .filter(models.Slot.start == slot.start)
            .filter(models.Slot.duration == slot.duration)
            .filter(models.Slot.booking_status != models.BookingStatus.none)
            .first()
    )
    return db_slot is not None


def book(db: Session, slot_id: int) -> models.Slot | None:
    """update booking status for slot of given id"""
    db_slot = get(db, slot_id)
    db_slot.booking_status = models.BookingStatus.booked
    db.commit()
    db.refresh(db_slot)
    return db_slot


def delete_all_for_appointment(db: Session, appointment_id: int):
    """delete all slots for appointment of given id"""
    return db.query(models.Slot).filter(models.Slot.appointment_id == appointment_id).delete()


def delete_all_for_subscriber(db: Session, subscriber_id: int):
    """Delete all slots by subscriber"""
    slots = get_by_subscriber(db, subscriber_id)

    for slot in slots:
        db.delete(slot)
    db.commit()

    return True


def update(db: Session, slot_id: int, attendee: schemas.Attendee):
    """update existing slot by id and create corresponding attendee"""
    # create attendee
    db_attendee = models.Attendee(**attendee.dict())
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    # update slot
    db_slot = get(db, slot_id)
    # TODO: additionally handle subscriber_id here for already logged in users
    setattr(db_slot, "attendee_id", db_attendee.id)
    db.commit()
    return db_attendee


def delete(db: Session, slot_id: int):
    """remove existing slot by id"""
    db_slot = get(db, slot_id)
    db.delete(db_slot)
    db.commit()
    return db_slot


def is_available(db: Session, slot_id: int):
    """check if slot is still available for booking"""
    slot = get(db, slot_id)
    if slot.schedule:
        return slot and slot.booking_status == models.BookingStatus.requested
    return False
