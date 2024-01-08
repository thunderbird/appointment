import json
import logging

import requests
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..controller.apis.fxa_client import FxaClient
from ..database import repo, models
from ..dependencies.database import get_db
from ..dependencies.fxa import get_webhook_auth, get_fxa_client
from ..exceptions.fxa_api import MissingRefreshTokenException

router = APIRouter()


@router.post("/fxa-process")
def fxa_process(
    request: Request,
    db: Session = Depends(get_db),
    decoded_token: dict = Depends(get_webhook_auth),
    fxa_client: FxaClient = Depends(get_fxa_client)
):
    """Main for webhooks regarding fxa"""

    subscriber: models.Subscriber = repo.get_subscriber_by_fxa_uid(db, decoded_token.get('sub'))
    if not subscriber:
        logging.warning("Webhook event received for non-existent user.")
        return

    subscriber_external_connection = subscriber.get_external_connection(models.ExternalConnectionType.fxa)
    fxa_client.setup(subscriber.id, token=subscriber_external_connection.token)

    for event, event_data in decoded_token.get('events', {}).items():
        match event:
            case 'https://schemas.accounts.firefox.com/event/password-change':
                # Ensure we ignore out of date requests, also .timestamp() returns seconds, but we get the time in ms.
                # TODO: We may need a last update timestamp JUST for token field changes.
                token_last_updated = subscriber_external_connection.time_updated.timestamp() * 1000
                if token_last_updated > event_data.get('changeTime'):
                    logging.info("Ignoring out of date logout request.")
                    break

                try:
                    fxa_client.logout()
                except MissingRefreshTokenException:
                    logging.warning("Subscriber doesn't have refresh token.")
                except requests.exceptions.HTTPError as ex:
                    logging.error(f"Error logging out user: {ex.response}")
                    logging.error(json.dumps(ex.request))
                    logging.error(json.dumps(ex.response))
            case 'https://schemas.accounts.firefox.com/event/profile-change':
                if event_data.get('email') is not None:
                    # Update the subscriber's email (and username for now)
                    subscriber.email = event_data.get('email')
                    subscriber.username = subscriber.email
                    db.add(subscriber)
                    db.commit()
            case 'https://schemas.accounts.firefox.com/event/delete-user':
                # TODO: We have a delete function, but it's not up-to-date
                logging.warning(f"Deletion request came in for {subscriber.id}")
            case _:
                logging.warning(f"Ignoring event {event}")
