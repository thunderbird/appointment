import logging

import requests
import sentry_sdk
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..controller import auth, data, zoom
from ..controller.apis.fxa_client import FxaClient
from ..database import repo, models, schemas
from ..database.models import ExternalConnectionType
from ..dependencies.database import get_db
from ..dependencies.fxa import get_webhook_auth as get_webhook_auth_fxa, get_fxa_client
from ..dependencies.zoom import get_webhook_auth as get_webhook_auth_zoom
from ..exceptions.account_api import AccountDeletionSubscriberFail
from ..exceptions.fxa_api import MissingRefreshTokenException

router = APIRouter()


@router.post('/fxa-process')
def fxa_process(
    db: Session = Depends(get_db),
    decoded_token: dict = Depends(get_webhook_auth_fxa),
    fxa_client: FxaClient = Depends(get_fxa_client),
):
    """Main for webhooks regarding fxa"""

    subscriber: models.Subscriber = repo.external_connection.get_subscriber_by_fxa_uid(db, decoded_token.get('sub'))
    if not subscriber:
        logging.warning('FXA webhook event received for non-existent user.')
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
                    logging.info('Ignoring out of date logout request.')
                    break

                try:
                    auth.logout(db, subscriber, fxa_client)
                except MissingRefreshTokenException:
                    logging.warning("Subscriber doesn't have refresh token.")
                except requests.exceptions.HTTPError as ex:
                    sentry_sdk.capture_exception(ex)
                    logging.error(f'Error logging out user: {ex.response}')
            case 'https://schemas.accounts.firefox.com/event/profile-change':
                if event_data.get('email') is not None:
                    # Update the subscriber's email, we do this first in case there's a problem with get_profile()
                    subscriber.email = event_data.get('email')
                    db.add(subscriber)
                    db.commit()

                try:
                    profile = fxa_client.get_profile()
                    # Update profile with fxa info
                    repo.subscriber.update(
                        db,
                        schemas.SubscriberIn(
                            avatar_url=profile['avatar'], name=subscriber.name, username=subscriber.username
                        ),
                        subscriber.id,
                    )
                except Exception as ex:
                    logging.error(f'Error updating user: {ex}')

                # Finally log the subscriber out
                try:
                    auth.logout(db, subscriber, fxa_client)
                except MissingRefreshTokenException:
                    logging.warning("Subscriber doesn't have refresh token.")
                except requests.exceptions.HTTPError as ex:
                    sentry_sdk.capture_exception(ex)
                    logging.error(f'Error logging out user: {ex.response}')
            case 'https://schemas.accounts.firefox.com/event/delete-user':
                try:
                    data.delete_account(db, subscriber)
                except AccountDeletionSubscriberFail as ex:
                    sentry_sdk.capture_exception(ex)
                    logging.error(f'Account deletion webhook failed: {ex.message}')

            case _:
                logging.warning(f'Ignoring event {event}')


@router.post('/zoom-deauthorization')
def zoom_deauthorization(
    request: Request,
    db: Session = Depends(get_db),
    webhook_payload: dict | None = Depends(get_webhook_auth_zoom)
):
    if not webhook_payload:
        logging.warning('Invalid zoom webhook event received.')
        return

    user_id = webhook_payload.get('user_id')

    subscriber = repo.external_connection.get_subscriber_by_zoom_user_id(
        db,
        user_id
    )

    if not subscriber:
        logging.warning('Zoom webhook event received for non-existent user.')
        return

    try:
        zoom.disconnect(db, subscriber.id, user_id)
    except Exception as ex:
        sentry_sdk.capture_exception(ex)
        logging.error(f'Error disconnecting zoom connection: {ex}')
