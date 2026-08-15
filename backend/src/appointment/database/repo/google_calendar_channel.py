"""Module: repo.google_calendar_channel

Repository providing CRUD functions for GoogleCalendarChannel database models.
"""

from datetime import datetime, UTC

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


def get_stale(db: Session, synced_before: datetime) -> list[models.GoogleCalendarChannel]:
    """Channels that either have never completed a sync, or haven't synced recently enough.

    Used by the reconciliation sweep to bound how long a dropped push notification can go
    unnoticed: anything this returns gets synced regardless of whether push claims to be alive.
    """
    return (
        db.query(models.GoogleCalendarChannel)
        .filter(
            (models.GoogleCalendarChannel.last_synced_at.is_(None))
            | (models.GoogleCalendarChannel.last_synced_at < synced_before)
        )
        .all()
    )


def record_sync(
    db: Session, channel: models.GoogleCalendarChannel, sync_token: str | None = None
) -> models.GoogleCalendarChannel:
    """Stamp a successful sync. is_push_active() trusts this watermark, so callers must only
    call this after the corresponding changes have actually been applied locally."""
    channel.last_synced_at = datetime.now(tz=UTC).replace(tzinfo=None)
    if sync_token is not None:
        channel.sync_token = sync_token
    db.commit()
    db.refresh(channel)
    return channel


def record_notification(
    db: Session,
    channel: models.GoogleCalendarChannel,
    message_number: int | None = None,
    expiration: datetime | None = None,
) -> int | None:
    """Record an inbound push notification.

    Returns the previously-seen message number so the caller can spot gaps (dropped deliveries)
    and replays (duplicate deliveries).

    Google re-states the channel expiration on every notification, so we take the opportunity to
    correct our stored copy for free.
    """
    previous = channel.last_message_number

    # Never let a replayed or out-of-order delivery walk the high-water mark backwards.
    if message_number is not None and (previous is None or message_number > previous):
        channel.last_message_number = message_number

    if expiration is not None:
        channel.expiration = expiration.replace(tzinfo=None) if expiration.tzinfo else expiration

    channel.last_notification_at = datetime.now(tz=UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(channel)
    return previous


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
