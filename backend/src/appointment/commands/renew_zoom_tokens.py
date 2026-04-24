"""Renew expiring Zoom auth tokens.

Run periodically (e.g., weekly) to ensure tokens don't expire.
Zoom tokens typically last ~90 days, so weekly renewal keeps a buffer.
"""

import logging
from datetime import datetime, timedelta, timezone

from ..database import repo
from ..dependencies.database import get_engine_and_session
from ..dependencies.zoom import get_zoom_client
from ..main import _common_setup


def run():
    _common_setup()

    _, SessionLocal = get_engine_and_session()
    db = SessionLocal()

    # Renew tokens that expire within the next 7 days
    threshold = datetime.now(tz=timezone.utc) + timedelta(days=7)
    zoom_connections = repo.external_connection.get_zoom(db)

    checked = 0
    failed = 0

    for connection in zoom_connections:
        if not connection or not connection.token:
            continue

        # Setup a new Zoom client to trigger token renewal if expiry date is in the past
        # or within the given time threshold
        try:
            subscriber = repo.subscriber.get(db, connection.owner_id)
            zoom_client = get_zoom_client(subscriber)
            zoom_client.setup(subscriber.id, connection.token, threshold.timestamp())
            checked += 1
        except Exception as e:
            logging.error(f'[renew_zoom_tokens] Failed to renew Zoom token for subscriber {subscriber.id}: {e}')
            failed += 1

    db.close()
    logging.info(
        f'[renew_zoom_tokens] Zoom token checks complete: '
        f'{checked} checked, {failed} failed, {len(zoom_connections)} total processed'
    )
