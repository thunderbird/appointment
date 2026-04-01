import logging

from appointment.celery_app import celery

log = logging.getLogger(__name__)


@celery.task
def renew_google_channels():
    from appointment.commands.renew_google_channels import run

    log.info('Starting Google Calendar channel renewal')
    run()
    log.info('Google Calendar channel renewal complete')
