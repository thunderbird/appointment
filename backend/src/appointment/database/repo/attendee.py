"""Module: repo.attendee

Repository providing CRUD functions for attendee database models. 
"""

from sqlalchemy.orm import Session
from .. import models


def get_by_subscriber(db: Session, subscriber_id: int):
    """For use with the data download. Get attendees by subscriber id."""
    # We need to walk through Calendars to attach Appointments, and Appointments to get Slots
    slots = (
        db.query(models.Slot)
        .join(models.Appointment)
        .join(models.Calendar)
        .filter(models.Calendar.owner_id == subscriber_id)
        .filter(models.Appointment.calendar_id == models.Calendar.id)
        .filter(models.Slot.appointment_id == models.Appointment.id)
        .all()
    )

    attendee_ids = list(map(lambda slot: slot.attendee_id if slot.attendee_id is not None else None, slots))
    attendee_ids = filter(lambda attendee: attendee is not None, attendee_ids)
    return db.query(models.Attendee).filter(models.Attendee.id.in_(attendee_ids)).all()


def delete_by_subscriber(db: Session, subscriber_id: int):
    """Delete all attendees by subscriber"""
    attendees = get_by_subscriber(db, subscriber_id)

    for attendee in attendees:
        db.delete(attendee)
    db.commit()

    return True
