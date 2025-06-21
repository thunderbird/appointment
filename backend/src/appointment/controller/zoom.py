from sqlalchemy.orm import Session

from appointment.database import repo, models
from appointment.database.models import ExternalConnectionType


def update_schedules_meeting_link_provider(db: Session, subscriber_id: int) -> bool:
    """Updates existing schedules' meeling link provider to be zoom"""
    schedules = repo.schedule.get_by_subscriber(db, subscriber_id)
    for schedule in schedules:
        schedule.meeting_link_provider = models.MeetingLinkProviderType.zoom
        db.add(schedule)
    db.commit()
    return True


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
