import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..controller.apis.fxa_client import FxaClient
from ..database import repo, models
from ..dependencies.database import get_db
from ..dependencies.fxa import get_webhook_auth, get_fxa_client

router = APIRouter()


@router.post("/fxa-process")
def fxa_process(
    request: Request,
    db: Session = Depends(get_db),
    decoded_token = Depends(get_webhook_auth),
    fxa_client: FxaClient = Depends(get_fxa_client)
):
    """Main for webhooks regarding fxa"""

    subscriber: models.Subscriber = repo.get_subscriber_by_fxa_uid(db, decoded_token.get('sub'))
    if not subscriber:
        logging.warning("Webhook event received for non-existent user.")
        return

    fxa_client.setup(subscriber.id, subscriber.get_external_connection(models.ExternalConnectionType.fxa).token)

    for event, event_data in decoded_token.get('events', default={}).items():
        match event:
            case 'https://schemas.accounts.firefox.com/event/password-change':
                # We also get `changeTime` in event_data, but let's just log them out.
                fxa_client.logout()
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
