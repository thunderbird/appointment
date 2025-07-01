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
    SupportRequestMail,
    InviteAccountMail,
    ConfirmYourEmailMail,
    NewBookingMail,
    CancelMail,
)
from appointment.defines import APP_ENV_DEV


def send_invite_email(owner_name, owner_email, date, duration, to, attachment):
    try:
        mail = InvitationMail(
            name=owner_name, email=owner_email, date=date, duration=duration, to=to, attachments=[attachment]
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


def send_pending_email(owner_name, date, to, attachment):
    try:
        mail = PendingRequestMail(owner_name=owner_name, date=date, to=to, attachments=[attachment])
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_cancel_email(owner_name, date, to, reason, attachment):
    try:
        mail = CancelMail(owner_name=owner_name, date=date, reason=reason, to=to, attachments=[attachment])
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_rejection_email(owner_name, date, to, attachment):
    try:
        mail = RejectionMail(owner_name=owner_name, date=date, to=to, attachments=[attachment])
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_zoom_meeting_failed_email(to, appointment_title):
    try:
        mail = ZoomMeetingFailedMail(to=to, appointment_title=appointment_title)
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_support_email(requestee_name, requestee_email, topic, details):
    try:
        mail = SupportRequestMail(
            requestee_name=requestee_name,
            requestee_email=requestee_email,
            topic=topic,
            details=details,
        )
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_invite_account_email(date, to, lang):
    try:
        mail = InviteAccountMail(date=date, to=to, lang=lang)
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)


def send_confirm_email(to, confirm_token, decline_token):
    try:
        base_url = f"{os.getenv('FRONTEND_URL')}/waiting-list"
        confirm_url = f'{base_url}/{confirm_token}'
        decline_url = f'{base_url}/{decline_token}'

        mail = ConfirmYourEmailMail(to=to, confirm_url=confirm_url, decline_url=decline_url)
        mail.send()
    except Exception as e:
        if os.getenv('APP_ENV') == APP_ENV_DEV:
            logging.error('[tasks.emails] An exception has occurred: ', e)
            traceback.print_exc()
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)
