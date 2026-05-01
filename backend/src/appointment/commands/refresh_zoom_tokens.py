"""Renew expiring Zoom auth tokens.

Run periodically (e.g., weekly) to ensure tokens don't expire.
Zoom tokens typically last ~90 days, so weekly renewal keeps a buffer.
"""

import json
import logging

from ..database import repo, models
from ..dependencies.database import get_engine_and_session
from ..dependencies.zoom import get_zoom_client
from ..main import _common_setup


def run():
    _common_setup()

    _, SessionLocal = get_engine_and_session()
    db = SessionLocal()
    zoom_connections = []
    refreshed = 0
    failed = 0

    try:
        zoom_connections = repo.external_connection.get_zoom(db)

        for connection in zoom_connections:
            if not connection or not connection.token:
                continue

            owner_id = connection.owner_id
            try:
                subscriber = repo.subscriber.get(db, owner_id)
                if not subscriber:
                    raise ValueError('No subscriber found for external connection')

                zoom_client = get_zoom_client(subscriber)
                token = json.loads(connection.token)

                # Force the OAuth session to attempt a refresh by marking the token as expired.
                token['expires_in'] = -100
                token['expires_at'] = 0
                zoom_client.setup(subscriber.id, token)
                zoom_client.get_me()

                new_token = zoom_client.client.token
                repo.external_connection.update_token_by_connection(
                    db,
                    json.dumps(new_token),
                    connection,
                )
                repo.external_connection.update_status(
                    db,
                    connection,
                    models.ExternalConnectionStatus.ok,
                )
                refreshed += 1
            except Exception:
                # Mark the external connection as error so the user can see
                # it in the Settings UI and fix it manually when they log in
                repo.external_connection.update_status(
                    db,
                    connection,
                    models.ExternalConnectionStatus.error,
                )

                # TODO: Send an email to the Subscriber
                # https://github.com/thunderbird/appointment/issues/1662
                failed += 1
    finally:
        db.close()

    logging.info(
        f'[refresh_zoom_tokens] Zoom token refresh complete: '
        f'{refreshed} refreshed, {failed} failed, {len(zoom_connections)} total processed'
    )
