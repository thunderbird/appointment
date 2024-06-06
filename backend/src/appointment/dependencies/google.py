import logging
import os

from ..controller.apis.google_client import GoogleClient


_google_client = GoogleClient(
    os.getenv("GOOGLE_AUTH_CLIENT_ID"),
    os.getenv("GOOGLE_AUTH_SECRET"),
    os.getenv("GOOGLE_AUTH_PROJECT_ID"),
    os.getenv("GOOGLE_AUTH_CALLBACK"),
)


def get_google_client() -> "GoogleClient":
    """Returns the google client instance"""
    try:
        _google_client.setup()
    except Exception as e:
        # google client setup was not possible
        logging.error(f"[routes.google] Google Client could not be setup, bad credentials?\nError: {str(e)}")

    return _google_client
