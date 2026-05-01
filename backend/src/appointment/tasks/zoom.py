import logging
import os

import sentry_sdk

from appointment.celery_app import celery
from appointment.dependencies.database import get_redis
from appointment.tasks.locks import (
    DEFAULT_LOCK_TTL_SECONDS,
    acquire_task_lock,
    release_task_lock,
)

log = logging.getLogger(__name__)


@celery.task
def refresh_zoom_tokens():
    from appointment.commands.refresh_zoom_tokens import run

    task_name = refresh_zoom_tokens.__name__
    redis_instance = get_redis(os.getenv('REDIS_CELERY_DB'))
    lock_token = None

    if redis_instance is not None:
        lock_token = acquire_task_lock(redis_instance, task_name, DEFAULT_LOCK_TTL_SECONDS)
        if lock_token is None:
            log.info('Zoom token check is already running, skipping.')
            return
    else:
        log.warning('Redis unavailable; running Zoom token check without distributed lock.')

    log.info('Starting Zoom token check')

    try:
        run()
    except Exception as e:
        log.error(f'Zoom token check failed: {e}')
        sentry_sdk.capture_exception(e)
        raise
    finally:
        if lock_token is not None:
            try:
                release_task_lock(redis_instance, task_name, lock_token)
            except Exception as e:
                log.error(f'Failed to release Zoom token check lock: {e}')
                sentry_sdk.capture_exception(e)

    log.info('Zoom token check complete')
