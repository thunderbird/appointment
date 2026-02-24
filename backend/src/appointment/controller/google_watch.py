"""Shared helpers for managing Google Calendar push notification (watch) channels."""

import json
import logging
import os
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from .apis.google_client import GoogleClient
from ..database import repo, models


def get_webhook_url() -> str | None:
    """Build the Google Calendar webhook URL from the backend URL, requires https."""
    backend_url = os.getenv('BACKEND_URL')
    if not backend_url:
        return None
    return f'{backend_url}/webhooks/google-calendar'


def get_google_token(google_client: GoogleClient, external_connection: models.ExternalConnections):
    """Build Google Credentials from an external connection's stored token."""
    return Credentials.from_authorized_user_info(
        json.loads(external_connection.token), google_client.SCOPES
    )


def setup_watch_channel(db: Session, google_client: GoogleClient, calendar: models.Calendar):
    """Register a push notification channel for a single Google calendar.
    No-ops if a channel already exists or prerequisites are missing."""
    if not google_client or calendar.provider != models.CalendarProvider.google:
        return

    webhook_url = get_webhook_url()
    if not webhook_url:
        logging.warning('[google_watch] BACKEND_URL not set, skipping watch channel setup')
        return

    existing = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
    if existing:
        return

    external_connection = calendar.external_connection
    if not external_connection or not external_connection.token:
        return

    try:
        token = get_google_token(google_client, external_connection)
    except (json.JSONDecodeError, Exception) as e:
        logging.warning(f'[google_watch] Could not parse token for calendar {calendar.id}: {e}')
        return

    try:
        response = google_client.watch_events(calendar.user, webhook_url, token)
        if response:
            expiration_ms = int(response.get('expiration', 0))
            expiration_dt = datetime.fromtimestamp(expiration_ms / 1000, tz=timezone.utc)

            sync_token = google_client.get_initial_sync_token(calendar.user, token)

            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id=response['id'],
                resource_id=response['resourceId'],
                expiration=expiration_dt,
                sync_token=sync_token,
            )
    except Exception as e:
        logging.warning(f'[google_watch] Failed to set up watch channel for calendar {calendar.id}: {e}')


def teardown_watch_channel(db: Session, google_client: GoogleClient | None, calendar: models.Calendar):
    """Stop and delete the watch channel for a single Google calendar."""
    channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
    if not channel:
        return

    if google_client and calendar.external_connection and calendar.external_connection.token:
        try:
            token = get_google_token(google_client, calendar.external_connection)
            google_client.stop_channel(channel.channel_id, channel.resource_id, token)
        except Exception as e:
            logging.warning(f'[google_watch] Failed to stop channel {channel.channel_id}: {e}')

    repo.google_calendar_channel.delete(db, channel)


def setup_watch_channels_for_connection(
    db: Session,
    google_client: GoogleClient,
    creds,
    subscriber_id: int,
    external_connection_id: int,
):
    """Register push notification channels for all connected Google calendars under a connection."""
    webhook_url = get_webhook_url()
    if not webhook_url:
        logging.warning('[google_watch] BACKEND_URL not set, skipping watch channel setup')
        return

    calendars = repo.calendar.get_by_subscriber(db, subscriber_id)
    for calendar in calendars:
        if calendar.provider != models.CalendarProvider.google:
            continue
        if calendar.external_connection_id != external_connection_id:
            continue
        if not calendar.connected:
            continue

        existing = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
        if existing:
            continue

        try:
            response = google_client.watch_events(calendar.user, webhook_url, creds)
            if response:
                expiration_ms = int(response.get('expiration', 0))
                expiration_dt = datetime.fromtimestamp(expiration_ms / 1000, tz=timezone.utc)

                sync_token = google_client.get_initial_sync_token(calendar.user, creds)

                repo.google_calendar_channel.create(
                    db,
                    calendar_id=calendar.id,
                    channel_id=response['id'],
                    resource_id=response['resourceId'],
                    expiration=expiration_dt,
                    sync_token=sync_token,
                )
        except Exception as e:
            logging.warning(f'[google_watch] Failed to set up watch channel for calendar {calendar.id}: {e}')


def teardown_watch_channels_for_connection(
    db: Session,
    google_client: GoogleClient | None,
    google_connection: models.ExternalConnections,
):
    """Stop and remove all watch channels for calendars under a Google connection."""
    if not google_connection or not google_connection.token:
        return

    token = None
    if google_client:
        try:
            token = Credentials.from_authorized_user_info(
                json.loads(google_connection.token), google_client.SCOPES
            )
        except (json.JSONDecodeError, Exception) as e:
            logging.warning(f'[google_watch] Could not parse token for channel teardown: {e}')

    calendars = (
        db.query(models.Calendar)
        .filter(models.Calendar.external_connection_id == google_connection.id)
        .all()
    )

    for calendar in calendars:
        channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
        if not channel:
            continue

        if google_client and token:
            try:
                google_client.stop_channel(channel.channel_id, channel.resource_id, token)
            except Exception as e:
                logging.warning(f'[google_watch] Failed to stop channel {channel.channel_id}: {e}')

        repo.google_calendar_channel.delete(db, channel)
