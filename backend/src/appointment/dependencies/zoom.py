import hashlib
import hmac
import logging
import os

from fastapi import Depends, Request

from .auth import get_subscriber
from ..controller.apis.zoom_client import ZoomClient
from ..database.models import Subscriber, ExternalConnectionType


def get_zoom_client(subscriber: Subscriber = Depends(get_subscriber)):
    """Returns a zoom client instance. This is a stateful dependency, and requires a new instance per request"""
    try:
        _zoom_client = ZoomClient(
            os.getenv('ZOOM_AUTH_CLIENT_ID'), os.getenv('ZOOM_AUTH_SECRET'), os.getenv('ZOOM_AUTH_CALLBACK')
        )

        # Grab our zoom connection if it's available, we only support one zoom connection...hopefully
        zoom_connection = subscriber.get_external_connection(ExternalConnectionType.zoom)
        token = zoom_connection.token if zoom_connection is not None else None

        _zoom_client.setup(subscriber.id, token)
    except Exception as e:
        logging.error(f'[routes.zoom] Zoom Client could not be setup, bad credentials?\nError: {str(e)}')
        raise e

    return _zoom_client


async def get_webhook_auth(request: Request):
    data = await request.json()
    event = data.get('event')

    if not event or event != 'app_deauthorized':
        return None

    signature = request.headers.get('x-zm-signature')
    signature_timestamp = request.headers.get('x-zm-request-timestamp')
    key = os.getenv('ZOOM_API_SECRET')

    if not signature or not signature_timestamp or not key:
        return None

    # Grab the body, and get encoding!
    # Body is encoded in bytes so we'll need to decode it and re-encode it...
    body = await request.body()
    key = bytes(key, 'UTF-8')
    message = bytes(f'v0:{signature_timestamp}:{body.decode("UTF-8")}', 'UTF-8')
    hash = hmac.new(key, message, hashlib.sha256).hexdigest()
    hash = f'v0={hash}'

    if hash != signature:
        return None

    payload = data.get('payload', {})
    user_id = payload.get('user_id')
    deauthorized_at = payload.get('deauthorization_time')

    if not user_id or not deauthorized_at:
        return None

    return payload
