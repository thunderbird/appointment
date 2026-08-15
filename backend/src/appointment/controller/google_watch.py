"""Shared helpers for managing Google Calendar push notification (watch) channels."""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from .apis.google_client import GoogleClient
from ..database import repo, models
from ..tasks.google import stop_google_channel


# How close to its expiration a channel may get before we stop trusting push delivery. Google
# stops sending as soon as the channel lapses, so we need to stop trusting it slightly *before*
# the recorded expiry rather than at it.
CHANNEL_EXPIRY_MARGIN = timedelta(minutes=5)

# The longest a channel may go without a successful sync before we stop trusting it.
# Reconciliation (tasks.google.reconcile_google_channels) runs well inside this window, so
# hitting it means push *and* reconciliation are both failing -- at which point we fall back to
# polling rather than serve unbounded staleness.
MAX_SYNC_AGE = timedelta(hours=6)


def _as_utc(value: datetime | None) -> datetime | None:
    """Normalise a possibly naive DB datetime to an aware UTC one.

    Columns are stored naive-UTC, but values that have just come off the wire are aware.
    Comparing the two raises, so everything funnels through here.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_push_active(channel: models.GoogleCalendarChannel | None, now: datetime | None = None) -> bool:
    """Whether push delivery on this channel can be trusted in place of polling.

    This is deliberately conservative: every uncertain case answers False, which only costs a
    Google API call. Answering True when push is in fact dead is the failure that shows users
    stale availability, so it has to be earned:

      * the channel must exist and still be registered with Google,
      * it must not be at or near its expiration,
      * it must have completed an initial sync (so we hold a sync token), and
      * that sync must be recent enough that a silently dead channel is caught.
    """
    if channel is None:
        return False

    now = now or datetime.now(tz=timezone.utc)

    expiration = _as_utc(channel.expiration)
    if expiration is None or expiration - CHANNEL_EXPIRY_MARGIN <= now:
        return False

    # No sync token means we have never established a delta chain for this calendar, so a
    # notification could not tell us what changed.
    if not channel.sync_token:
        return False

    last_synced_at = _as_utc(channel.last_synced_at)
    if last_synced_at is None or now - last_synced_at > MAX_SYNC_AGE:
        return False

    return True


def push_backed_calendar_ids(db: Session, calendars: list[models.Calendar]) -> set[str]:
    """The remote (Google) calendar ids among `calendars` that have live push.

    Returns remote ids -- i.e. `Calendar.user` -- because the freebusy call sites work in
    Google's ids rather than ours.
    """
    now = datetime.now(tz=timezone.utc)
    backed = set()

    for calendar in calendars:
        if calendar.provider != models.CalendarProvider.google:
            continue
        channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
        if is_push_active(channel, now):
            backed.add(calendar.user)

    return backed


def get_webhook_url() -> str | None:
    """Build the Google Calendar webhook URL from the backend URL, requires https."""
    backend_url = os.getenv('BACKEND_URL')
    if not backend_url:
        return None
    return f'{backend_url}/webhooks/google-calendar'


def get_google_token(google_client: GoogleClient, external_connection: models.ExternalConnections):
    """Build Google Credentials from an external connection's stored token."""
    if not external_connection.token:
        return None

    return Credentials.from_authorized_user_info(
        json.loads(external_connection.token), google_client.SCOPES
    )


def setup_watch_channel(db: Session, google_client: GoogleClient, calendar: models.Calendar) -> bool:
    """Register a push notification channel for a single Google calendar.
    Returns True if a channel exists (or was created), False on failure."""
    if not google_client or calendar.provider != models.CalendarProvider.google:
        return False

    webhook_url = get_webhook_url()
    if not webhook_url:
        logging.warning('[google_watch] BACKEND_URL not set, skipping watch channel setup')
        return False

    existing = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
    if existing:
        return True

    external_connection = calendar.external_connection
    if not external_connection or not external_connection.token:
        return False

    try:
        token = get_google_token(google_client, external_connection)
    except (json.JSONDecodeError, Exception) as e:
        logging.error(f'[google_watch] Could not parse token for calendar {calendar.id}: {e}')
        return False

    if not token:
        logging.error(f'[google_watch] Missing token for calendar {calendar.id}')
        return False

    try:
        state = str(uuid.uuid4())
        response = google_client.watch_events(calendar.user, webhook_url, token, state=state)
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
                state=state,
                sync_token=sync_token,
                last_synced_at=datetime.now(tz=timezone.utc) if sync_token else None,
            )
    except Exception as e:
        logging.warning(f'[google_watch] Failed to set up watch channel for calendar {calendar.id}: {e}')
        return False

    return True


def teardown_watch_channel(db: Session, calendar: models.Calendar) -> bool:
    """Stop and delete the watch channel for a single Google calendar.
    Returns True if the channel was deleted, False if there was nothing to remove."""
    channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
    if not channel:
        return False

    if calendar.external_connection and calendar.external_connection.token:
        stop_google_channel.delay(
            channel.channel_id, channel.resource_id, calendar.external_connection.token,
        )

    repo.google_calendar_channel.delete(db, channel)
    return True


def teardown_watch_channels_for_connection(
    db: Session,
    google_connection: models.ExternalConnections,
):
    """Stop and remove all watch channels for calendars under a Google connection."""
    if not google_connection or not google_connection.token:
        return

    calendars = (
        db.query(models.Calendar)
        .filter(models.Calendar.external_connection_id == google_connection.id)
        .all()
    )

    for calendar in calendars:
        channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
        if not channel:
            continue

        stop_google_channel.delay(
            channel.channel_id, channel.resource_id, google_connection.token,
        )

        repo.google_calendar_channel.delete(db, channel)
