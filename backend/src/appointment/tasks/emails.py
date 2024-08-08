import os

from appointment.controller.mailer import (
    PendingRequestMail,
    ConfirmationMail,
    InvitationMail,
    ZoomMeetingFailedMail,
    RejectionMail,
    SupportRequestMail,
    InviteAccountMail,
    ConfirmYourEmailMail, NewBookingMail,
)


def send_invite_email(owner_name, owner_email, date, duration, to, attachment):
    mail = InvitationMail(name=owner_name, email=owner_email, date=date, duration=duration, to=to, attachments=[attachment])
    mail.send()


def send_confirmation_email(url, attendee_name, attendee_email, date, duration, to, schedule_name):
    # send confirmation mail to owner
    mail = ConfirmationMail(f'{url}/1', f'{url}/0', attendee_name, attendee_email, date, duration, schedule_name, to=to)
    mail.send()


def send_new_booking_email(attendee_name, attendee_email, date, to):
    # send notice mail to owner
    mail = NewBookingMail(attendee_name, attendee_email, date, to=to)
    mail.send()


def send_pending_email(owner_name, date, to):
    mail = PendingRequestMail(owner_name=owner_name, date=date, to=to)
    mail.send()


def send_rejection_email(owner_name, date, to):
    mail = RejectionMail(owner_name=owner_name, date=date, to=to)
    mail.send()


def send_zoom_meeting_failed_email(to, appointment_title):
    mail = ZoomMeetingFailedMail(to=to, appointment_title=appointment_title)
    mail.send()


def send_support_email(requestee_name, requestee_email, topic, details):
    mail = SupportRequestMail(
        requestee_name=requestee_name,
        requestee_email=requestee_email,
        topic=topic,
        details=details,
    )
    mail.send()


def send_invite_account_email(to):
    mail = InviteAccountMail(to=to)
    mail.send()


def send_confirm_email(to, confirm_token, decline_token):
    base_url = f"{os.getenv('FRONTEND_URL')}/waiting-list"
    confirm_url = f"{base_url}/{confirm_token}"
    decline_url = f"{base_url}/{decline_token}"

    mail = ConfirmYourEmailMail(to=to, confirm_url=confirm_url, decline_url=decline_url)
    mail.send()
