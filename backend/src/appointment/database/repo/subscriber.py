"""Module: repo.subscriber

Repository providing CRUD functions for subscriber database models. 
"""

import re

from sqlalchemy.orm import Session
from .. import models, schemas
from ...controller.auth import sign_url


def get(db: Session, subscriber_id: int) -> models.Subscriber | None:
    """retrieve subscriber by id"""
    return db.get(models.Subscriber, subscriber_id)


def get_by_email(db: Session, email: str) -> models.Subscriber | None:
    """retrieve subscriber by email"""
    return db.query(models.Subscriber).filter(models.Subscriber.email == email).first()


def get_by_username(db: Session, username: str):
    """retrieve subscriber by username"""
    return db.query(models.Subscriber).filter(models.Subscriber.username == username).first()


def get_by_appointment(db: Session, appointment_id: int):
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


def get_by_google_state(db: Session, state: str):
    """retrieve subscriber by google state, you'll have to manually check the google_state_expire_at!"""
    if state is None:
        return None
    return db.query(models.Subscriber).filter(models.Subscriber.google_state == state).first()


def create(db: Session, subscriber: schemas.SubscriberBase):
    """create new subscriber"""
    data = subscriber.model_dump()

    # Filter incoming data to just the available model columns
    columns = models.Subscriber().get_columns()
    data = {k: v for k, v in data.items() if k in columns}

    db_subscriber = models.Subscriber(**data)
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def update(db: Session, data: schemas.SubscriberIn, subscriber_id: int):
    """update all subscriber attributes, they can edit themselves"""
    db_subscriber = get(db, subscriber_id)
    for key, value in data:
        if value is not None:
            setattr(db_subscriber, key, value)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def delete(db: Session, subscriber: models.Subscriber):
    """Delete a subscriber by subscriber id"""
    db.delete(subscriber)
    db.commit()
    return True


def get_connections_limit(db: Session, subscriber_id: int):
    """return the number of allowed connections for given subscriber or -1 for unlimited connections"""
    # db_subscriber = get(db, subscriber_id)
    # mapping = {
    #     models.SubscriberLevel.basic: int(os.getenv("TIER_BASIC_CALENDAR_LIMIT")),
    #     models.SubscriberLevel.plus: int(os.getenv("TIER_PLUS_CALENDAR_LIMIT")),
    #     models.SubscriberLevel.pro: int(os.getenv("TIER_PRO_CALENDAR_LIMIT")),
    #     models.SubscriberLevel.admin: -1,
    # }
    # return mapping[db_subscriber.level]

    # No limit right now!
    return -1


def verify_link(db: Session, url: str):
    """Check if a given url is a valid signed subscriber profile link
    Return subscriber if valid.
    """
    # Look for a <username> followed by an optional signature that ends the string
    pattern = r"[\/]([\w\d\-_\.\@]+)[\/]?([\w\d]*)[\/]?$"
    match = re.findall(pattern, url)

    if match is None or len(match) == 0:
        return False

    # Flatten
    match = match[0]
    clean_url = url

    username = match[0]
    signature = None
    if len(match) > 1:
        signature = match[1]
        clean_url = clean_url.replace(signature, "")

    subscriber = get_by_username(db, username)
    if not subscriber:
        return False

    clean_url_with_short_link = clean_url + f"{subscriber.short_link_hash}"
    signed_signature = sign_url(clean_url_with_short_link)

    # Verify the signature matches the incoming one
    if signed_signature == signature:
        return subscriber
    return False
