import logging
import os

from posthog import Posthog
from appointment.defines import APP_ENV_TEST, APP_ENV_DEV


def get_posthog() -> Posthog | None:
    if any([not os.getenv('POSTHOG_PROJECT_KEY'), not os.getenv('POSTHOG_HOST')]):
        logging.warning("!! Posthog is not setup correctly")
        return None

    posthog = Posthog(os.getenv('POSTHOG_PROJECT_KEY'), host=os.getenv('POSTHOG_HOST'))

    if os.getenv('APP_ENV') == APP_ENV_TEST:
        posthog.disabled = True
        logging.info("!! Posthog is disabled")
    if os.getenv('APP_ENV') == APP_ENV_DEV:
        posthog.debug = True
        logging.info("!! Posthog is in debug mode")

    return posthog
