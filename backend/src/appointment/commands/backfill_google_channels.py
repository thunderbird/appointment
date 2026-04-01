"""One-off command to set up Google Calendar watch channels for existing connected calendars."""

import json
import logging
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials

from ..controller.google_watch import get_webhook_url
from ..database import repo, models
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
        print('BACKEND_URL not set, aborting.')
        db.close()
        return

    # Find connected Google calendars that are the default in a schedule
    # and don't yet have a watch channel
    schedule_calendar_ids = db.query(models.Schedule).filter(models.Schedule.calendar_id is None).all()

    all_calendars = db.query(models.Calendar).filter(
        models.Calendar.provider == models.CalendarProvider.google,
        models.Calendar.connected == True,  # noqa: E712
        models.Calendar.id.in_(schedule_calendar_ids),
    ).all()

    candidates = []
    for cal in all_calendars:
        existing = repo.google_calendar_channel.get_by_calendar_id(db, cal.id)
        if not existing:
            candidates.append(cal)

    print(f'Found {len(candidates)} connected Google calendar(s) without a watch channel.')

    created = 0
    skipped = 0
    failed = 0

    for calendar in candidates:
        ext_conn = calendar.external_connection
        if not ext_conn or not ext_conn.token:
            print(f'  Calendar {calendar.id}: no external connection or token, skipping.')
            skipped += 1
            continue

        try:
            token = Credentials.from_authorized_user_info(
                json.loads(ext_conn.token), google_client.SCOPES
            )
        except Exception as e:
            print(f'  Calendar {calendar.id}: failed to parse token ({e}), skipping.')
            skipped += 1
            continue

        try:
            response = google_client.watch_events(calendar.user, webhook_url, token)
            if not response:
                print(f'  Calendar {calendar.id}: watch_events returned no response.')
                failed += 1
                continue

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
            created += 1
            print(f'  Calendar {calendar.id}: channel created (expires {expiration_dt}).')
        except Exception as e:
            print(f'  Calendar {calendar.id}: failed ({e}).')
            logging.error(f'[backfill_google_channels] Error for calendar {calendar.id}: {e}')
            failed += 1

    db.close()
    print(f'\nBackfill complete: {created} created, {skipped} skipped, {failed} failed.')
