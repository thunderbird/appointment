from appointment.controller.mailer import (
    PendingRequestMail,
    ConfirmationMail,
    InvitationMail,
    ZoomMeetingFailedMail,
    RejectionMail,
    SupportRequestMail,
    InviteAccountMail,
)


def send_invite_email(to, attachment):
    mail = InvitationMail(to=to, attachments=[attachment])
    mail.send()


def send_confirmation_email(url, attendee_name, attendee_email, date, to):
    # send confirmation mail to owner
    mail = ConfirmationMail(f"{url}/1", f"{url}/0", attendee_name, attendee_email, date, to=to)
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
