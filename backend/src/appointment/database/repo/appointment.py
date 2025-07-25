"""Module: repo.appointment

Repository providing CRUD functions for appointment database models.
"""

from sqlalchemy.orm import Session
from .. import models, schemas, repo


def exists(db: Session, appointment_id: int):
    """true if appointment of given id exists"""
    return True if db.get(models.Appointment, appointment_id) is not None else False


def create(db: Session, appointment: schemas.AppointmentFull, slots: list[schemas.SlotBase] = []):
    """create new appointment with slots for calendar"""
    db_appointment = models.Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    if len(slots) > 0:
        repo.slot.add_for_appointment(db, slots, db_appointment.id)
    return db_appointment


def get(db: Session, appointment_id: int) -> models.Appointment | None:
    """retrieve appointment by id (private)"""
    if appointment_id:
        return db.get(models.Appointment, appointment_id)
    return None


def get_public(db: Session, slug: str):
    """retrieve appointment by appointment slug (public)"""
    if slug:
        return db.query(models.Appointment).filter(models.Appointment.slug == slug).first()
    return None


def get_by_subscriber(db: Session, subscriber_id: int):
    """retrieve list of appointments by owner id"""
    return db.query(models.Appointment).join(models.Calendar).filter(models.Calendar.owner_id == subscriber_id).all()


def is_owned(db: Session, appointment_id: int, subscriber_id: int):
    """check if appointment belongs to subscriber"""
    db_appointment = get(db, appointment_id)
    return repo.calendar.is_owned(db, db_appointment.calendar_id, subscriber_id)


def has_slot(db: Session, appointment_id: int, slot_id: int):
    """check if appointment belongs to subscriber"""
    db_slot = repo.slot.get(db, slot_id)
    return db_slot and db_slot.appointment_id == appointment_id


def update(
    db: Session,
    appointment: schemas.AppointmentFull,
    slots: list[schemas.SlotBase],
    appointment_id: int,
):
    """update existing appointment by id"""
    db_appointment = get(db, appointment_id)
    for key, value in appointment:
        setattr(db_appointment, key, value)
    db.commit()
    db.refresh(db_appointment)
    repo.slot.delete(db, appointment_id)
    repo.slot.add_for_appointment(db, slots, appointment_id)
    return db_appointment


def delete(db: Session, appointment_id: int):
    """remove existing appointment by id"""
    db_appointment = get(db, appointment_id)
    db.delete(db_appointment)
    db.commit()
    return db_appointment


def delete_by_subscriber(db: Session, subscriber_id: int):
    """Delete all appointments by subscriber"""
    appointments = get_by_subscriber(db, subscriber_id=subscriber_id)
    for appointment in appointments:
        delete(db, appointment_id=appointment.id)
    return True


def update_status(db: Session, appointment_id: int, status: models.AppointmentStatus):
    appointment = get(db, appointment_id)
    if not appointment:
        return False

    appointment.status = status
    db.commit()


def update_title(db: Session, appointment_id: int, title: str):
    db_appointment = get(db, appointment_id)
    if not db_appointment:
        return False

    db_appointment.title = title
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def update_external_id(db: Session, appointment: models.Appointment, external_id: str):
    """Update appointment's external id field
    Note: This requires a full appointment model to prevent a needless db lookup"""
    db.add(appointment)

    appointment.external_id = external_id
    db.commit()
    db.refresh(appointment)
    return appointment


def update_external_id_by_id(db: Session, appointment_id: int, external_id: str):
    appointment = get(db, appointment_id)
    if not appointment:
        return False
    return update_external_id(db, appointment, external_id)


def update_title_and_slot(db: Session, appointment_id: int, appointment_data: schemas.AppointmentModifyRequest):
    """Update an existing appointment's title and slot."""
    db_appointment = get(db, appointment_id)
    if not db_appointment:
        return None

    db_appointment.title = appointment_data.title
    db.commit()

    slot_update = schemas.SlotUpdate(
        start=appointment_data.start,
        title=appointment_data.title,
        booking_status=models.BookingStatus.modified,
    )

    repo.slot.update(db, appointment_data.slot_id, slot_update)

    db.refresh(db_appointment)
    return db_appointment
