"""Module: controller.external_connection

Health check logic for external connections (Zoom, Google, CalDAV).
"""

import json
import logging
import os
from datetime import datetime, UTC

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from ..controller.apis.google_client import GoogleClient
from ..controller.apis.zoom_client import ZoomClient
from ..controller.calendar import CalDavConnector
from ..database.models import (
    ExternalConnectionStatus,
    ExternalConnectionType,
    ExternalConnections,
    Subscriber,
)
from ..exceptions.calendar import TestConnectionFailed


CHECKABLE_TYPES = {
    ExternalConnectionType.zoom,
    ExternalConnectionType.google,
    ExternalConnectionType.caldav,
}


def _check_zoom(ec: ExternalConnections) -> ExternalConnectionStatus:
    """Validate a Zoom connection by attempting to fetch the user profile."""
    try:
        zoom_client = ZoomClient(
            os.getenv('ZOOM_AUTH_CLIENT_ID'),
            os.getenv('ZOOM_AUTH_SECRET'),
            os.getenv('ZOOM_AUTH_CALLBACK'),
        )
        zoom_client.setup(subscriber_id=ec.owner_id, token=ec.token)
        zoom_client.get_me()
        return ExternalConnectionStatus.ok
    except Exception as e:
        logging.warning(f'[health_check] Zoom connection {ec.id} is unhealthy: {e}')
        return ExternalConnectionStatus.error


def _check_google(ec: ExternalConnections) -> ExternalConnectionStatus:
    """Validate a Google connection by checking/refreshing its credentials."""
    try:
        google_client = GoogleClient(
            os.getenv('GOOGLE_AUTH_CLIENT_ID'),
            os.getenv('GOOGLE_AUTH_SECRET'),
            os.getenv('GOOGLE_AUTH_PROJECT_ID'),
            os.getenv('GOOGLE_AUTH_CALLBACK'),
        )

        creds = Credentials.from_authorized_user_info(
            json.loads(ec.token), google_client.SCOPES
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds.valid:
            return ExternalConnectionStatus.error

        return ExternalConnectionStatus.ok
    except (RefreshError, ValueError, Exception) as e:
        logging.warning(f'[health_check] Google connection {ec.id} is unhealthy: {e}')
        return ExternalConnectionStatus.error


def _check_caldav(ec: ExternalConnections, db: Session) -> ExternalConnectionStatus:
    """Validate a CalDAV connection by testing server connectivity."""
    try:
        # type_id stores [url, user] as JSON, token stores the password
        url, user = json.loads(ec.type_id)
        password = ec.token

        con = CalDavConnector(
            db=db,
            redis_instance=None,
            url=url,
            user=user,
            password=password,
            subscriber_id=ec.owner_id,
            calendar_id=None,
        )
        con.test_connection()

        return ExternalConnectionStatus.ok
    except (TestConnectionFailed, Exception) as e:
        logging.warning(f'[health_check] CalDAV connection {ec.id} is unhealthy: {e}')
        return ExternalConnectionStatus.error


def check_status(db: Session, subscriber: Subscriber) -> list[ExternalConnections]:
    """Run health checks on all checkable external connections for a subscriber.

    Checks Zoom, Google, and CalDAV connections. Updates the status column
    in the database and returns the updated connections.
    """
    updated = []

    for ec in subscriber.external_connections:
        if ec.type not in CHECKABLE_TYPES:
            continue

        if ec.type == ExternalConnectionType.zoom:
            new_status = _check_zoom(ec)
        elif ec.type == ExternalConnectionType.google:
            new_status = _check_google(ec)
        elif ec.type == ExternalConnectionType.caldav:
            new_status = _check_caldav(ec, db)
        else:
            continue

        ec.status = new_status
        ec.status_checked_at = datetime.now(UTC)
        db.add(ec)
        updated.append(ec)

    db.commit()

    return updated
