import logging
import os

from fastapi import Depends
from posthog import Posthog

from appointment.database import models
from appointment.defines import APP_ENV_TEST, APP_ENV_DEV
from appointment.dependencies.auth import get_subscriber


def get_posthog(subscriber:  models.Subscriber = Depends(get_subscriber)) -> Posthog | None:
    if any([not subscriber, not os.getenv('POSTHOG_PROJECT_KEY'), not os.getenv('POSTHOG_HOST')]):
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
