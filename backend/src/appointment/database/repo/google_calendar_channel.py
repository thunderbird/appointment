"""Module: repo.google_calendar_channel

Repository providing CRUD functions for GoogleCalendarChannel database models.
"""

from datetime import datetime, timezone

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


def get_stale(db: Session, synced_before: datetime) -> list[models.GoogleCalendarChannel]:
    """Channels whose last successful sync is older than `synced_before`.

    Channels that have never synced are included: they hold no delta chain, so
    they are the staleest of all.
    """
    return (
        db.query(models.GoogleCalendarChannel)
        .filter(
            (models.GoogleCalendarChannel.last_synced_at.is_(None))
            | (models.GoogleCalendarChannel.last_synced_at < synced_before)
        )
        .all()
    )


def create(
    db: Session,
    calendar_id: int,
    channel_id: str,
    resource_id: str,
    expiration: datetime,
    state: str,
    sync_token: str | None = None,
    last_synced_at: datetime | None = None,
) -> models.GoogleCalendarChannel:
    channel = models.GoogleCalendarChannel(
        calendar_id=calendar_id,
        channel_id=channel_id,
        resource_id=resource_id,
        expiration=expiration,
        sync_token=sync_token,
        state=state,
        last_synced_at=last_synced_at,
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


def record_sync(db: Session, channel: models.GoogleCalendarChannel, sync_token: str | None = None):
    """Stamp a successful sync, optionally advancing the sync token.

    This is the watermark `is_push_active` trusts, so it must only be called
    after Google has actually answered.
    """
    if sync_token:
        channel.sync_token = sync_token
    channel.last_synced_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(channel)
    return channel


def record_notification(db: Session, channel: models.GoogleCalendarChannel):
    """Record that a push notification arrived on this channel.

    Observability only. Paired with last_synced_at it separates "Google stopped
    telling us" from "we heard, and failed to act on it", which is otherwise not
    something we can tell apart after the fact.
    """
    channel.last_notification_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(channel)
    return channel


def update_expiration(
    db: Session,
    channel: models.GoogleCalendarChannel,
    new_channel_id: str,
    new_resource_id: str,
    new_expiration: datetime,
    new_state: str,
):
    channel.channel_id = new_channel_id
    channel.resource_id = new_resource_id
    channel.expiration = new_expiration
    channel.state = new_state
    db.commit()
    db.refresh(channel)
    return channel


def delete(db: Session, channel: models.GoogleCalendarChannel):
    db.delete(channel)
    db.commit()
