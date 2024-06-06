"""Module: mailer

Handle outgoing emails.
"""
import logging
import os
import smtplib
import ssl

import jinja2
import validators

from html import escape
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi.templating import Jinja2Templates

from ..l10n import l10n


def get_jinja():
    path = "src/appointment/templates/email"

    templates = Jinja2Templates(path)
    # Add our l10n function
    templates.env.globals.update(l10n=l10n)

    return templates


def get_template(template_name) -> "jinja2.Template":
    """Retrieves a template under the templates/email folder. Make sure to include the file extension!"""
    templates = get_jinja()
    return templates.get_template(template_name)


class Attachment:
    def __init__(self, mime: tuple[str], filename: str, data: str):
        self.mime_main = mime[0]
        self.mime_sub = mime[1]
        self.filename = filename
        self.data = data


class Mailer:
    def __init__(
        self,
        to: str,
        sender: str = os.getenv("SERVICE_EMAIL"),
        subject: str = "",
        html: str = "",
        plain: str = "",
        attachments: list[Attachment] = [],
    ):
        self.sender = sender
        self.to = to
        self.subject = subject
        self.body_html = html
        self.body_plain = plain
        self.attachments = attachments

    def html(self):
        """provide email body as html per default"""
        return self.body_html

    def text(self):
        """provide email body as text"""
        # TODO: do some real html tag stripping and sanitizing here
        return self.body_plain if self.body_plain != "" else escape(self.body_html)

    def attachments(self):
        """provide all attachments as list"""
        return self.attachments

    def build(self):
        """build email header, body and attachments"""
        # create mail header
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject
        message["From"] = self.sender
        message["To"] = self.to

        # add body as html and text parts
        if self.text():
            message.attach(MIMEText(self.text(), "plain"))
        if self.html():
            message.attach(MIMEText(self.html(), "html"))

        # add attachment(s) as multimedia parts
        for a in self.attachments:
            part = MIMEBase(a.mime_main, a.mime_sub)
            part.set_payload(a.data)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={a.filename}")
            message.attach(part)

        return message.as_string()

    def send(self):
        """actually send the email"""
        # get smtp configuration
        SMTP_SECURITY = os.getenv("SMTP_SECURITY", "NONE")
        SMTP_URL = os.getenv("SMTP_URL", "localhost")
        SMTP_PORT = os.getenv("SMTP_PORT", 25)
        SMTP_USER = os.getenv("SMTP_USER")
        SMTP_PASS = os.getenv("SMTP_PASS")

        # check config
        url = f"http://{SMTP_URL}:{SMTP_PORT}"
        if not validators.url(url):
            # url is not valid
            logging.error("[mailer.send] No valid SMTP url configured: " + url)

        server = None
        try:
            # if configured, create a secure SSL context
            if SMTP_SECURITY == "SSL":
                server = smtplib.SMTP_SSL(SMTP_URL, SMTP_PORT, context=ssl.create_default_context())
                server.login(SMTP_USER, SMTP_PASS)
            elif SMTP_SECURITY == "STARTTLS":
                server = smtplib.SMTP(SMTP_URL, SMTP_PORT)
                server.starttls(context=ssl.create_default_context())
                server.login(SMTP_USER, SMTP_PASS)
            # fall back to non-secure
            else:
                server = smtplib.SMTP(SMTP_URL, SMTP_PORT)
            # now send email
            server.sendmail(self.sender, self.to, self.build())
        except Exception as e:
            # sending email was not possible
            logging.error("[mailer.send] An error occurred on sending email: " + str(e))
        finally:
            if server:
                server.quit()


class InvitationMail(Mailer):
    def __init__(self, *args, **kwargs):
        """init Mailer with invitation specific defaults"""
        default_kwargs = {
            "subject": l10n("invite-mail-subject"),
            "plain": l10n("invite-mail-plain"),
        }
        super(InvitationMail, self).__init__(*args, **default_kwargs, **kwargs)

    def html(self):
        return get_template("invite.jinja2").render()


class ZoomMeetingFailedMail(Mailer):
    def __init__(self, appointment_title, *args, **kwargs):
        """init Mailer with invitation specific defaults"""
        default_kwargs = {"subject": l10n("zoom-invite-failed-subject")}
        super(ZoomMeetingFailedMail, self).__init__(*args, **default_kwargs, **kwargs)

        self.appointment_title = appointment_title

    def html(self):
        return get_template("errors/zoom_invite_failed.jinja2").render(title=self.appointment_title)

    def text(self):
        return l10n("zoom-invite-failed-plain", {"title": self.appointment_title})


class ConfirmationMail(Mailer):
    def __init__(self, confirm_url, deny_url, attendee_name, attendee_email, date, *args, **kwargs):
        """init Mailer with confirmation specific defaults"""
        self.attendee_name = attendee_name
        self.attendee_email = attendee_email
        self.date = date
        self.confirmUrl = confirm_url
        self.denyUrl = deny_url
        default_kwargs = {"subject": l10n("confirm-mail-subject")}
        super(ConfirmationMail, self).__init__(*args, **default_kwargs, **kwargs)

    def text(self):
        return l10n(
            "confirm-mail-plain",
            {
                "attendee_name": self.attendee_name,
                "attendee_email": self.attendee_email,
                "date": self.date,
                "confirm_url": self.confirmUrl,
                "deny_url": self.denyUrl,
            },
        )

    def html(self):
        return get_template("confirm.jinja2").render(
            attendee_name=self.attendee_name,
            attendee_email=self.attendee_email,
            date=self.date,
            confirm=self.confirmUrl,
            deny=self.denyUrl,
        )


class RejectionMail(Mailer):
    def __init__(self, owner_name, date, *args, **kwargs):
        """init Mailer with rejection specific defaults"""
        self.owner_name = owner_name
        self.date = date
        default_kwargs = {"subject": l10n("reject-mail-subject")}
        super(RejectionMail, self).__init__(*args, **default_kwargs, **kwargs)

    def text(self):
        return l10n("reject-mail-plain", {"owner_name": self.owner_name, "date": self.date})

    def html(self):
        return get_template("rejected.jinja2").render(owner_name=self.owner_name, date=self.date)


class PendingRequestMail(Mailer):
    def __init__(self, owner_name, date, *args, **kwargs):
        """init Mailer with pending specific defaults"""
        self.owner_name = owner_name
        self.date = date
        default_kwargs = {"subject": l10n("pending-mail-subject")}
        super(PendingRequestMail, self).__init__(*args, **default_kwargs, **kwargs)

    def text(self):
        return l10n("pending-mail-plain", {"owner_name": self.owner_name, "date": self.date})

    def html(self):
        return get_template("pending.jinja2").render(owner_name=self.owner_name, date=self.date)


class SupportRequestMail(Mailer):
    def __init__(self, requestee_name, requestee_email, topic, details, *args, **kwargs):
        """init Mailer with support specific defaults"""
        self.requestee_name = requestee_name
        self.requestee_email = requestee_email
        self.topic = topic
        self.details = details
        default_kwargs = {"subject": l10n("support-mail-subject", {"topic": topic})}
        super(SupportRequestMail, self).__init__(os.getenv("SUPPORT_EMAIL"), *args, **default_kwargs, **kwargs)

    def text(self):
        return l10n(
            "support-mail-plain",
            {
                "requestee_name": self.requestee_name,
                "requestee_email": self.requestee_email,
                "topic": self.topic,
                "details": self.details,
            },
        )

    def html(self):
        return get_template("support.jinja2").render(
            requestee_name=self.requestee_name,
            requestee_email=self.requestee_email,
            topic=self.topic,
            details=self.details,
        )


class InviteAccountMail(Mailer):
    def __init__(self, *args, **kwargs):
        default_kwargs = {"subject": l10n("new-account-mail-subject")}
        super(InviteAccountMail, self).__init__(*args, **default_kwargs, **kwargs)

    def text(self):
        return l10n(
            "new-account-mail-plain",
            {
                "homepage_url": os.getenv("FRONTEND_URL"),
            },
        )

    def html(self):
        return get_template("new_account.jinja2").render(homepage_url=os.getenv("FRONTEND_URL"))
