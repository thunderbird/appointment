"""Module: repo.availability

Repository providing CRUD functions for availability database models.
"""

from sqlalchemy.orm import Session
from .. import models, schemas, repo


""" AVAILABILITY repository functions
"""


def get(db: Session, availability_id: int) -> models.Availability | None:
    """retrieve availability by id"""
    if availability_id:
        return db.get(models.Availability, availability_id)
    return None


def create(db: Session, availability: schemas.AvailabilityBase):
    """create new availability for schedule of given id"""
    db_availability = models.Availability(**availability.model_dump())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability


def update(db: Session, availability_id: int, data: schemas.AvailabilityBase):
    """Update existing availability record with given data"""
    db_availability = get(db, availability_id)
    for key, value in data:
        setattr(db_availability, key, value)
    db.commit()
    db.refresh(db_availability)
    return db_availability


def delete(db: Session, availability_id: int):
    """remove existing availability by id"""
    db_availability = get(db, availability_id)
    db.delete(db_availability)
    db.commit()
    return db_availability


def sync_multiple(db: Session, availabilities: list[schemas.AvailabilityBase], schedule_id: int):
    """create, update or delete availability for a schedule of given id"""
    # Update existing records or create new records
    for entry in availabilities:
        existing_availability = find_on_schedule(db, entry, schedule_id)
        if existing_availability:
            update(db, existing_availability.id, entry)
        else:
            create(db, entry)
    # Delete all records that were removed from the availability set
    db_schedule = repo.schedule.get(db, schedule_id)
    for record in db_schedule.availabilities:
        if (
            record.day_of_week not in [a.day_of_week for a in availabilities]
            or len(
                [
                    a
                    for a in availabilities
                    if (a.day_of_week == record.day_of_week and a.start_time == record.start_time)
                ]
            )
            == 0
        ):
            delete(db, record.id)


def find_on_schedule(db: Session, availability: schemas.AvailabilityBase, schedule_id: int):
    """check if given availability already exists for schedule and return it or None"""
    db_availability = (
        db.query(models.Availability)
        .filter(models.Availability.schedule_id == schedule_id)
        .filter(models.Availability.day_of_week == availability.day_of_week)
        .filter(models.Availability.start_time == availability.start_time)
        .first()
    )
    return db_availability
