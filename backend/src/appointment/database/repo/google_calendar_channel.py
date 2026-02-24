"""Module: repo.google_calendar_channel

Repository providing CRUD functions for GoogleCalendarChannel database models.
"""

from datetime import datetime

from sqlalchemy.orm import Session
from .. import models


def get_by_calendar_id(db: Session, calendar_id: int) -> models.GoogleCalendarChannel | None:
    return (
        db.query(models.GoogleCalendarChannel)
        .filter(models.GoogleCalendarChannel.calendar_id == calendar_id)
        .first()
    )


def get_by_channel_id(db: Session, channel_id: str) -> models.GoogleCalendarChannel | None:
    return (
        db.query(models.GoogleCalendarChannel)
        .filter(models.GoogleCalendarChannel.channel_id == channel_id)
        .first()
    )


def get_expiring(db: Session, before: datetime) -> list[models.GoogleCalendarChannel]:
    return (
        db.query(models.GoogleCalendarChannel)
        .filter(models.GoogleCalendarChannel.expiration < before)
        .all()
    )


def create(
    db: Session,
    calendar_id: int,
    channel_id: str,
    resource_id: str,
    expiration: datetime,
    sync_token: str | None = None,
) -> models.GoogleCalendarChannel:
    channel = models.GoogleCalendarChannel(
        calendar_id=calendar_id,
        channel_id=channel_id,
        resource_id=resource_id,
        expiration=expiration,
        sync_token=sync_token,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def update_sync_token(db: Session, channel: models.GoogleCalendarChannel, sync_token: str):
    channel.sync_token = sync_token
    db.commit()
    db.refresh(channel)
    return channel


def update_expiration(
    db: Session,
    channel: models.GoogleCalendarChannel,
    new_channel_id: str,
    new_resource_id: str,
    new_expiration: datetime,
):
    channel.channel_id = new_channel_id
    channel.resource_id = new_resource_id
    channel.expiration = new_expiration
    db.commit()
    db.refresh(channel)
    return channel


def delete(db: Session, channel: models.GoogleCalendarChannel):
    db.delete(channel)
    db.commit()
