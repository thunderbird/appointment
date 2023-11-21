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

templates = Jinja2Templates("src/appointment/templates/email")


def get_template(template_name) -> "jinja2.Template":
    """Retrieves a template under the templates/email folder. Make sure to include the file extension!"""
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
        message = MIMEMultipart()
        message["Subject"] = self.subject
        message["From"] = self.sender
        message["To"] = self.to

        # add body as html and text parts
        if self.html():
            message.attach(MIMEText(self.html(), "html"))
        if self.text():
            message.attach(MIMEText(self.text(), "plain"))

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
            logging.error("[mailer.send] An error occured on sending email: " + str(e))
        finally:
            if server:
                server.quit()


class InvitationMail(Mailer):
    def __init__(self, *args, **kwargs):
        """init Mailer with invitation specific defaults"""
        defaultKwargs = {
            "subject": "[TBA] Invitation sent from Thunderbird Appointment",
            "plain": "This message is sent from Thunderbird Appointment.",
        }
        super(InvitationMail, self).__init__(*args, **defaultKwargs, **kwargs)

    def html(self):
        return get_template("invite.jinja2").render()


class ZoomMeetingFailedMail(Mailer):
    def __init__(self, appointment_title, *args, **kwargs):
        """init Mailer with invitation specific defaults"""
        defaultKwargs = {
            "subject": "[TBA] Zoom Meeting Link Creation Error",
        }
        super(ZoomMeetingFailedMail, self).__init__(*args, **defaultKwargs, **kwargs)

        self.appointment_title = appointment_title

    def html(self):
        return get_template("errors/zoom_invite_failed.jinja2").render(title=self.appointment_title)

    def text(self):
        return f"Unfortunately there was an error creating your Zoom meeting for your upcoming appointment: {self.appointment_title}"


class ConfirmationMail(Mailer):
    def __init__(self, confirmUrl, denyUrl, attendee, date, *args, **kwargs):
        """init Mailer with confirmation specific defaults"""
        self.attendee = attendee
        self.date = date
        self.confirmUrl = confirmUrl
        self.denyUrl = denyUrl
        defaultKwargs = {
            "subject": "[TBA] Confirm booking request from Thunderbird Appointment",
            "plain": """
{name} ({email}) just requested this time slot from your schedule: {date}

Visit this link to confirm the booking request:
{confirm}

Or this link if you want to deny it:
{deny}

This message is sent from Thunderbird Appointment.
            """.format(
                    name=self.attendee.name,
                    email=self.attendee.email,
                    date=self.date,
                    confirm=self.confirmUrl,
                    deny=self.denyUrl
                ),
        }
        super(ConfirmationMail, self).__init__(*args, **defaultKwargs, **kwargs)

    def html(self):
        return get_template("confirm.jinja2").render(
            attendee=self.attendee,
            date=self.date,
            confirm=self.confirmUrl,
            deny=self.denyUrl,
        )


class RejectionMail(Mailer):
    def __init__(self, owner, date, *args, **kwargs):
        """init Mailer with rejection specific defaults"""
        self.owner = owner
        self.date = date
        defaultKwargs = {
            "subject": "[TBA] Booking request declined",
            "plain": """
{name} denied your booking request for this time slot: {date}.

This message is sent from Thunderbird Appointment.
            """.format(name=self.owner.name, date=self.date),
        }
        super(RejectionMail, self).__init__(*args, **defaultKwargs, **kwargs)

    def html(self):
        return get_template("rejected.jinja2").render(owner=self.owner, date=self.date)
