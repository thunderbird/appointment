import logging
import os
import threading
from typing import Optional

from posthog import Posthog
from appointment.defines import APP_ENV_TEST, APP_ENV_DEV

_posthog: Optional[Posthog] = None
_posthog_lock = threading.Lock()


def get_posthog() -> Posthog | None:
    """Returns the process-wide Posthog client, or None if Posthog isn't configured.

    Each Posthog client starts a background consumer thread that lives until the process exits, so we must only
    ever create one and reuse it. Creating one per request leaks a thread per request."""
    global _posthog

    if _posthog is not None:
        return _posthog

    if any([not os.getenv('POSTHOG_PROJECT_KEY'), not os.getenv('POSTHOG_HOST')]):
        logging.warning('!! Posthog is not setup correctly')
        return None

    # Routes run in a threadpool, so guard against two requests creating a client at the same time.
    with _posthog_lock:
        if _posthog is None:
            posthog = Posthog(os.getenv('POSTHOG_PROJECT_KEY'), host=os.getenv('POSTHOG_HOST'))

            if os.getenv('APP_ENV') == APP_ENV_TEST:
                posthog.disabled = True
                logging.info('!! Posthog is disabled')
            if os.getenv('APP_ENV') == APP_ENV_DEV:
                posthog.debug = True
                logging.info('!! Posthog is in debug mode')

            _posthog = posthog

    return _posthog
