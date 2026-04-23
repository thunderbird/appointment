import logging

import sentry_sdk
from sqlalchemy.orm import Session

from ..database import repo, models
from ..database.models import ExternalConnectionType
from ..dependencies.zoom import get_zoom_client


def update_schedules_meeting_link_provider(db: Session, subscriber_id: int) -> bool:
    """Updates existing schedules' meeting link provider to be zoom"""
    schedules = repo.schedule.get_by_subscriber(db, subscriber_id)
    for schedule in schedules:
        schedule.meeting_link_provider = models.MeetingLinkProviderType.zoom
        db.add(schedule)
    db.commit()
    return True


def create_meeting_link(
    db: Session,
    slot: models.Slot,
    subscriber: models.Subscriber,
    title: str,
) -> str | None:
    """Create a Zoom meeting and persist the link on the slot.

    Returns the join URL on success, or ``None`` on any failure.
    """
    try:
        zoom_client = get_zoom_client(subscriber)
        response = zoom_client.create_meeting(title, slot.start.isoformat(), slot.duration, subscriber.timezone)
        if 'id' in response:
            join_url = zoom_client.get_meeting(response['id'])['join_url']
            slot.meeting_link_id = response['id']
            slot.meeting_link_url = join_url
            db.add(slot)
            db.commit()
            return join_url
    except Exception as err:
        logging.error(f'[zoom] Zoom meeting creation error: {err}')
        sentry_sdk.capture_exception(err)
    return None


def disconnect(db: Session, subscriber_id: int, type_id: str) -> bool:
    """Disconnects a zoom external connection from a given subscriber id and zoom type id"""
    repo.external_connection.delete_by_type(db, subscriber_id, ExternalConnectionType.zoom, type_id)
    schedules = repo.schedule.get_by_subscriber(db, subscriber_id)
    for schedule in schedules:
        if schedule.meeting_link_provider == models.MeetingLinkProviderType.zoom:
            schedule.meeting_link_provider = models.MeetingLinkProviderType.none
            db.add(schedule)
    db.commit()
    return True
