"""Module: repo.availability

Repository providing CRUD functions for availability database models.
"""

from sqlalchemy.orm import Session
from .. import models, schemas


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


# def update(db: Session, availability: schemas.AvailabilityBase):
#     """create new availability for schedule of given id"""
#     db_availability = models.Availability(**availability.model_dump())
#     db.add(db_availability)
#     db.commit()
#     db.refresh(db_availability)
#     return db_availability


def save_multiple(db: Session, availabilities: list[schemas.AvailabilityBase]):
    """create new availability for schedule of given id"""
    # TODO: handle update
    for record in availabilities:
        create(db, record)


# def exists_on_schedule(db: Session, availability: schemas.AvailabilityBase, schedule_id: int):
#     """check if given availability already exists for schedule of given id"""
#     db_availability = (
#         db.query(models.Availability)
#         .filter(models.Availability.schedule_id == schedule_id)
#         .filter(models.Availability.day_of_week == availability.day_of_week)
#         # TODO: This will be needed later if we implement multiple time slots per day
#         # .filter(models.Availability.start_time == availability.start_time)
#         # .filter(models.Availability.end_time == availability.end_time)
#         .first()
#     )
#     return db_availability is not None


def delete(db: Session, availability_id: int):
    """remove existing availability by id"""
    db_availability = get(db, availability_id)
    db.delete(db_availability)
    db.commit()
    return db_availability
