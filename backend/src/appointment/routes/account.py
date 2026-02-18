import os
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from posthog import Posthog

from ..controller import data
from ..controller.external_connection import check_status
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber, ExternalConnectionType
from ..database.repo.external_connection import get_by_type
from ..database import schemas

from fastapi.responses import StreamingResponse

from ..dependencies.metrics import get_posthog
from ..exceptions.account_api import AccountDeletionException

router = APIRouter()


def _serialize_external_connections(subscriber: Subscriber) -> dict:
    """Serialize a subscriber's external connections into a grouped dict by type."""
    external_connections = defaultdict(list)

    if os.getenv('ZOOM_API_ENABLED'):
        external_connections['zoom'] = []

    for ec in subscriber.external_connections:
        external_connections[ec.type.name].append(
            schemas.ExternalConnectionOut(
                id=ec.id,
                owner_id=ec.owner_id,
                type=ec.type.name,
                type_id=ec.type_id,
                name=ec.name,
                status=ec.status.value if ec.status else 'ok',
                status_checked_at=ec.status_checked_at.isoformat() if ec.status_checked_at else None,
            )
        )

    return external_connections


@router.get('/external-connections', tags=['no-cache'])
def get_external_connections(subscriber: Subscriber = Depends(get_subscriber)):
    """Return all external connections for the authenticated subscriber."""
    return _serialize_external_connections(subscriber)


@router.post('/external-connections/check-status', tags=['no-cache'])
def check_external_connection_status(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Run health checks on the subscriber's external connections (Zoom, Google, CalDAV).
    Updates connection statuses in the database and returns the updated list."""
    check_status(db, subscriber)
    return _serialize_external_connections(subscriber)


@router.post('/download')
def download_data(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Download your account data in zip format! Returns a streaming response with the zip buffer."""
    zip_buffer = data.download(db, subscriber)
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type='application/x-zip-compressed',
        headers={'Content-Disposition': 'attachment; filename=data.zip'},
    )


@router.delete('/delete')
def delete_account(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
    posthog: Posthog = Depends(get_posthog),
):
    """Delete your account and all the data associated with it forever!"""
    try:
        return data.delete_account(db, subscriber)
    except AccountDeletionException as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get('/available-emails')
def get_available_emails(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Return the list of emails they can use within Thunderbird Appointment"""
    google_connections = get_by_type(db, subscriber_id=subscriber.id, type=ExternalConnectionType.google)

    emails = {subscriber.email, *[connection.name for connection in google_connections]} - {subscriber.preferred_email}

    return [subscriber.preferred_email, *emails]
