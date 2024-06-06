import logging
import os

from fastapi import Depends

from .auth import get_subscriber
from ..controller.apis.zoom_client import ZoomClient
from ..database.models import Subscriber, ExternalConnectionType


def get_zoom_client(subscriber: Subscriber = Depends(get_subscriber)):
    """Returns a zoom client instance. This is a stateful dependency, and requires a new instance per request"""
    try:
        _zoom_client = ZoomClient(
            os.getenv("ZOOM_AUTH_CLIENT_ID"), os.getenv("ZOOM_AUTH_SECRET"), os.getenv("ZOOM_AUTH_CALLBACK")
        )

        # Grab our zoom connection if it's available, we only support one zoom connection...hopefully
        zoom_connection = subscriber.get_external_connection(ExternalConnectionType.zoom)
        token = zoom_connection.token if zoom_connection is not None else None

        _zoom_client.setup(subscriber.id, token)
    except Exception as e:
        logging.error(f"[routes.zoom] Zoom Client could not be setup, bad credentials?\nError: {str(e)}")
        raise e

    return _zoom_client
