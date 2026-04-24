import logging

import sentry_sdk

from appointment.celery_app import celery

log = logging.getLogger(__name__)


@celery.task
def refresh_zoom_tokens():
    from appointment.commands.refresh_zoom_tokens import run

    log.info('Starting Zoom token check')
    try:
        run()
    except Exception as e:
        log.error(f'Zoom token check failed: {e}')
        sentry_sdk.capture_exception(e)
        raise
    log.info('Zoom token check complete')
