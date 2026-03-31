import logging

from appointment.celery_app import celery

log = logging.getLogger(__name__)


@celery.task
def heartbeat():
    log.info('Celery heartbeat — worker is alive')
    return 'ok'
