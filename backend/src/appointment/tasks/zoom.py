import logging
import sentry_sdk

from appointment.celery_app import celery
from appointment.tasks.locks import TaskLockFailed, task_lock


@celery.task
def refresh_zoom_tokens():
    from appointment.commands.refresh_zoom_tokens import run

    try:
        with task_lock(refresh_zoom_tokens.__name__):
            logging.info('Starting Zoom token check')
            run()
            logging.info('Zoom token check complete')
    except TaskLockFailed:
        logging.info('Zoom token check is already running, skipping.')
    except Exception as e:
        logging.error(f'Zoom token check failed: {e}')
        sentry_sdk.capture_exception(e)
        raise
