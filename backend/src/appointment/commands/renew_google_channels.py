"""Renew expiring Google Calendar push notification channels.

Run periodically (e.g., daily) to ensure channels don't expire.
Google channels typically last ~7 days, so daily renewal keeps a buffer.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials

from ..controller.google_watch import get_webhook_url
from ..database import repo
from ..dependencies.database import get_engine_and_session
from ..dependencies.google import get_google_client
from ..main import _common_setup


def run():
    _common_setup()
    google_client = get_google_client()

    _, SessionLocal = get_engine_and_session()
    db = SessionLocal()

    webhook_url = get_webhook_url()
    if not webhook_url:
        logging.error('[renew_google_channels] BACKEND_URL not set, aborting')
        db.close()
        return

    # Renew channels that expire within the next 24 hours
    threshold = datetime.now(tz=timezone.utc) + timedelta(hours=24)
    channels = repo.google_calendar_channel.get_expiring(db, before=threshold)

    renewed = 0
    failed = 0

    for channel in channels:
        calendar = channel.calendar
        if not calendar or not calendar.connected:
            repo.google_calendar_channel.delete(db, channel)
            continue

        external_connection = calendar.external_connection
        if not external_connection or not external_connection.token:
            repo.google_calendar_channel.delete(db, channel)
            continue

        token = Credentials.from_authorized_user_info(
            json.loads(external_connection.token), google_client.SCOPES
        )

        # Stop the old channel (fire-and-forget via Celery with retries)
        from ..tasks.google import stop_google_channel
        stop_google_channel.delay(channel.channel_id, channel.resource_id, external_connection.token)

        # Create a new channel
        try:
            new_state = str(uuid.uuid4())
            response = google_client.watch_events(calendar.user, webhook_url, token, state=new_state)
            if response:
                expiration_ms = int(response.get('expiration', 0))
                expiration_dt = datetime.fromtimestamp(expiration_ms / 1000, tz=timezone.utc)

                repo.google_calendar_channel.update_expiration(
                    db,
                    channel,
                    new_channel_id=response['id'],
                    new_resource_id=response['resourceId'],
                    new_expiration=expiration_dt,
                    new_state=new_state,
                )
                renewed += 1
            else:
                repo.google_calendar_channel.delete(db, channel)
                failed += 1
        except Exception as e:
            logging.error(f'[renew_google_channels] Failed to renew channel for calendar {calendar.id}: {e}')
            failed += 1

    db.close()
    print(f'Channel renewal complete: {renewed} renewed, {failed} failed, {len(channels)} total processed')
