import logging
import os
import traceback

import sentry_sdk

from appointment.controller.mailer import (
    PendingRequestMail,
    ConfirmationMail,
    InvitationMail,
    ZoomMeetingFailedMail,
    RejectionMail,
    NewBookingMail,
    CancelMail,
)
from appointment.defines import APP_ENV_DEV


def send_invite_email(owner_name, owner_email, date, duration, to, attachment, lang):
    try:
        mail = InvitationMail(
            name=owner_name, email=owner_email, date=date, duration=duration,
            to=to, attachments=[attachment], lang=lang,
        )
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_confirmation_email(url, attendee_name, attendee_email, date, duration, to, schedule_name, lang):
    # send confirmation mail to owner
    try:
        mail = ConfirmationMail(
            f'{url}/1', f'{url}/0', attendee_name, attendee_email, date, duration, schedule_name, to=to, lang=lang
        )
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_new_booking_email(name, email, date, duration, to, schedule_name, lang):
    # send notice mail to owner
    try:
        mail = NewBookingMail(name, email, date, duration, schedule_name, to=to, lang=lang)
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_pending_email(owner_name, date, duration, to, attachment, lang):
    try:
        mail = PendingRequestMail(
            owner_name=owner_name, date=date, duration=duration, to=to, attachments=[attachment], lang=lang,
        )
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_cancel_email(owner_name, date, duration, to, attachment, lang):
    try:
        mail = CancelMail(
            owner_name=owner_name, date=date, duration=duration, to=to, attachments=[attachment], lang=lang,
        )
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_rejection_email(owner_name, date, duration, to, attachment, lang):
    try:
        mail = RejectionMail(
            owner_name=owner_name, date=date, duration=duration, to=to, attachments=[attachment], lang=lang,
        )
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_zoom_meeting_failed_email(to, appointment_title, lang):
    try:
        mail = ZoomMeetingFailedMail(to=to, appointment_title=appointment_title, lang=lang)
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)
