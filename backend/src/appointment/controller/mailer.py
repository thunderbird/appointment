"""Module: mailer

Handle outgoing emails.
"""
import datetime
import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

import jinja2
import sentry_sdk
import validators

from html import escape
from fastapi.templating import Jinja2Templates

from ..l10n import l10n


def get_jinja():
    path = 'src/appointment/templates/email'

    templates = Jinja2Templates(path)
    # Add our l10n function
    templates.env.trim_blocks = True
    templates.env.lstrip_blocks = True
    templates.env.globals.update(l10n=l10n)
    templates.env.globals.update(homepage_url=os.getenv('FRONTEND_URL'))

    return templates


def get_template(template_name) -> 'jinja2.Template':
    """Retrieves a template under the templates/email folder. Make sure to include the file extension!"""
    templates = get_jinja()
    return templates.get_template(template_name)


class Attachment:
    def __init__(self, mime: tuple[str,str], filename: str, data: str|bytes):
        self.mime_main = mime[0]
        self.mime_sub = mime[1]
        self.filename = filename
        self.data = data


class Mailer:
    def __init__(
        self,
        to: str,
        sender: str = os.getenv('SERVICE_EMAIL'),
        reply_to: str = os.getenv('SUPPORT_EMAIL'),
        subject: str = '',
        html: str = '',
        plain: str = '',
        attachments: list[Attachment] = [],
        method: str = 'REQUEST'
    ):
        self.sender = sender
        self.to = to
        self.reply_to = reply_to
        self.subject = subject
        self.body_html = html
        self.body_plain = plain
        self.attachments = attachments
        self.method = method

    def html(self):
        """provide email body as html per default"""
        return self.body_html

    def text(self):
        """provide email body as text"""
        # TODO: do some real html tag stripping and sanitizing here
        return self.body_plain if self.body_plain != '' else escape(self.body_html)

    def _attachments(self):
        """provide all attachments as list"""
        return self.attachments

    def build(self):
        """build email header, body and attachments"""
        # create mail header

        message = EmailMessage()
        message['Subject'] = self.subject
        message['From'] = self.sender
        message['To'] = self.to
        message['Reply-To'] = self.reply_to

        # add body as html and text parts
        message.set_content(self.text())
        message.add_alternative(self.html(), subtype='html')

        # add attachment(s) as multimedia parts
        for a in self._attachments():
            # Handle ics files differently than inline images
            if a.mime_main == 'text' and a.mime_sub == 'calendar':
                message.add_attachment(
                    a.data,
                    maintype=a.mime_main,
                    subtype=a.mime_sub,
                    filename=a.filename
                )
                # Fix the header of the attachment
                message.get_payload()[-1].replace_header(
                    'Content-Type',
                    f'{a.mime_main}/{a.mime_sub}; charset="UTF-8"; method={self.method}'
                )
            else:
                # Attach it to the html payload
                message.get_payload()[1].add_related(
                    a.data,
                    a.mime_main,
                    a.mime_sub,
                    cid=f'<{a.filename}>',
                    filename=a.filename,
                )

        return message

    def send(self):
        """actually send the email"""
        # get smtp configuration
        SMTP_SECURITY = os.getenv('SMTP_SECURITY', 'NONE')
        SMTP_URL = os.getenv('SMTP_URL', 'localhost')
        SMTP_PORT = os.getenv('SMTP_PORT', 25)
        SMTP_USER = os.getenv('SMTP_USER')
        SMTP_PASS = os.getenv('SMTP_PASS')

        # check config
        url = f'http://{SMTP_URL}:{SMTP_PORT}'
        if not validators.url(url):
            # url is not valid
            logging.error('[mailer.send] No valid SMTP url configured: ' + url)

        server = None
        try:
            # if configured, create a secure SSL context
            if SMTP_SECURITY == 'SSL':
                server = smtplib.SMTP_SSL(SMTP_URL, SMTP_PORT, context=ssl.create_default_context())
                server.login(SMTP_USER, SMTP_PASS)
            elif SMTP_SECURITY == 'STARTTLS':
                server = smtplib.SMTP(SMTP_URL, SMTP_PORT)
                server.starttls(context=ssl.create_default_context())
                server.login(SMTP_USER, SMTP_PASS)
            # fall back to non-secure
            else:
                server = smtplib.SMTP(SMTP_URL, SMTP_PORT)
            # now send email
            server.send_message(self.build(), to_addrs=self.to)
        except Exception as e:
            # sending email was not possible
            logging.error('[mailer.send] An error occurred on sending email: ' + str(e))
            if os.getenv('SENTRY_DSN'):
                sentry_sdk.capture_exception(e)
            raise e
        finally:
            if server:
                server.quit()


class BaseBookingMail(Mailer):
    def __init__(self, name, email, date, duration, *args, **kwargs):
        """Base class for emails with name, email, and event information"""
        self.name = name
        self.email = email
        self.date = date
        self.duration = duration

        # Pass to super now!
        super().__init__(*args, **kwargs)

        # Localize date and time range format
        self.time_format = l10n('time-format')
        self.date_format = l10n('date-format')

        # If value is key then there's no localization available, set a default.
        if self.time_format == 'time-format':
            self.time_format = '%I:%M%p'
        if self.date_format == 'date-format':
            self.date_format = '%A, %B %d, %Y'

        date_end = self.date + datetime.timedelta(minutes=self.duration)

        self.time_range = ' - '.join([date.strftime(self.time_format), date_end.strftime(self.time_format)])
        self.timezone = ''
        if self.date.tzinfo:
            self.timezone += f'({date.strftime("%Z")})'
        self.day = date.strftime(self.date_format)

    def _attachments(self):
        """We need these little icons for the message body"""
        path = 'src/appointment/templates/assets/img/icons'

        with open(f'{path}/calendar.png', 'rb') as fh:
            calendar_icon = fh.read()
        with open(f'{path}/clock.png', 'rb') as fh:
            clock_icon = fh.read()

        return [
            Attachment(
                mime=('image', 'png'),
                filename='calendar.png',
                data=calendar_icon,
            ),
            Attachment(
                mime=('image', 'png'),
                filename='clock.png',
                data=clock_icon,
            ),
            *self.attachments,
        ]


class InvitationMail(BaseBookingMail):
    def __init__(self, *args, **kwargs):
        """init Mailer with invitation specific defaults"""
        default_kwargs = {
            'subject': l10n('invite-mail-subject'),
            'plain': l10n('invite-mail-plain'),
        }
        super().__init__(*args, **default_kwargs, **kwargs)
        self.reply_to = self.email

    def html(self):
        return get_template('invite.jinja2').render(
            name=self.name,
            email=self.email,
            time_range=self.time_range,
            timezone=self.timezone,
            day=self.day,
            duration=self.duration,
            # Icon cids
            calendar_icon_cid=self._attachments()[0].filename,
            clock_icon_cid=self._attachments()[1].filename,
            # Calendar ics cid
            #invite_cid=self._attachments()[2].filename,
        )


class ZoomMeetingFailedMail(Mailer):
    def __init__(self, appointment_title, *args, **kwargs):
        """init Mailer with invitation specific defaults"""
        default_kwargs = {'subject': l10n('zoom-invite-failed-subject')}
        super(ZoomMeetingFailedMail, self).__init__(*args, **default_kwargs, **kwargs)

        self.appointment_title = appointment_title

    def html(self):
        return get_template('errors/zoom_invite_failed.jinja2').render(title=self.appointment_title)

    def text(self):
        return l10n('zoom-invite-failed-plain', {'title': self.appointment_title})


class ConfirmationMail(BaseBookingMail):
    def __init__(self, confirm_url, deny_url, name, email, date, duration, schedule_name, *args, **kwargs):
        """init Mailer with confirmation specific defaults"""
        self.confirmUrl = confirm_url
        self.denyUrl = deny_url
        self.schedule_name = schedule_name
        default_kwargs = {'subject': l10n('confirm-mail-subject', {'name': name})}
        super().__init__(name=name, email=email, date=date, duration=duration, *args, **default_kwargs, **kwargs)


    def text(self):
        return l10n(
            'confirm-mail-plain',
            {
                'name': self.name,
                'email': self.email,
                'day': self.day,
                'duration': self.duration,
                'time_range': self.time_range,
                'timezone': self.timezone,
                'confirm_url': self.confirmUrl,
                'deny_url': self.denyUrl,
            },
        )

    def html(self):
        return get_template('confirm.jinja2').render(
            name=self.name,
            email=self.email,
            time_range=self.time_range,
            timezone=self.timezone,
            day=self.day,
            duration=self.duration,
            confirm=self.confirmUrl,
            deny=self.denyUrl,
            schedule_name=self.schedule_name,
            # Icon cids
            calendar_icon_cid=self._attachments()[0].filename,
            clock_icon_cid=self._attachments()[1].filename,
        )


class RejectionMail(Mailer):
    def __init__(self, owner_name, date, *args, **kwargs):
        """init Mailer with rejection specific defaults"""
        self.owner_name = owner_name
        self.date = date
        default_kwargs = {'subject': l10n('reject-mail-subject')}
        super(RejectionMail, self).__init__(*args, **default_kwargs, **kwargs)
        self.method = 'CANCEL'

    def text(self):
        return l10n('reject-mail-plain', {'owner_name': self.owner_name, 'date': self.date})

    def html(self):
        return get_template('rejected.jinja2').render(owner_name=self.owner_name, date=self.date)


class PendingRequestMail(Mailer):
    def __init__(self, owner_name, date, *args, **kwargs):
        """init Mailer with pending specific defaults"""
        self.owner_name = owner_name
        self.date = date
        default_kwargs = {'subject': l10n('pending-mail-subject')}
        super(PendingRequestMail, self).__init__(*args, **default_kwargs, **kwargs)

    def text(self):
        return l10n('pending-mail-plain', {'owner_name': self.owner_name, 'date': self.date})

    def html(self):
        return get_template('pending.jinja2').render(owner_name=self.owner_name, date=self.date)


class NewBookingMail(BaseBookingMail):
    def __init__(self, name, email, date, duration, schedule_name, *args, **kwargs):
        """init Mailer with confirmation specific defaults"""
        self.schedule_name = schedule_name
        default_kwargs = {'subject': l10n('new-booking-subject', {'name': name})}
        super().__init__(name=name, email=email, date=date, duration=duration, *args, **default_kwargs, **kwargs)
        self.reply_to = email

    def text(self):
        return l10n(
            'new-booking-plain',
            {
                'name': self.name,
                'email': self.email,
                'date': self.date,
            },
        )

    def html(self):
        return get_template('new_booking.jinja2').render(
            name=self.name,
            email=self.email,
            time_range=self.time_range,
            timezone=self.timezone,
            day=self.day,
            duration=self.duration,
            schedule_name=self.schedule_name,
            # Icon cids
            calendar_icon_cid=self._attachments()[0].filename,
            clock_icon_cid=self._attachments()[1].filename,
        )


class SupportRequestMail(Mailer):
    def __init__(self, requestee_name, requestee_email, topic, details, *args, **kwargs):
        """init Mailer with support specific defaults"""
        self.requestee_name = requestee_name
        self.requestee_email = requestee_email
        self.topic = topic
        self.details = details
        default_kwargs = {'subject': l10n('support-mail-subject', {'topic': topic})}
        super(SupportRequestMail, self).__init__(os.getenv('SUPPORT_EMAIL', 'help@tb.net'), *args, **default_kwargs, **kwargs)

    def text(self):
        return l10n(
            'support-mail-plain',
            {
                'requestee_name': self.requestee_name,
                'requestee_email': self.requestee_email,
                'topic': self.topic,
                'details': self.details,
            },
        )

    def html(self):
        return get_template('support.jinja2').render(
            requestee_name=self.requestee_name,
            requestee_email=self.requestee_email,
            topic=self.topic,
            details=self.details,
        )


class InviteAccountMail(Mailer):
    def __init__(self, *args, **kwargs):
        default_kwargs = {'subject': l10n('new-account-mail-subject')}
        super(InviteAccountMail, self).__init__(*args, **default_kwargs, **kwargs)

    def text(self):
        return l10n(
            'new-account-mail-plain',
            {
                'homepage_url': os.getenv('FRONTEND_URL'),
            },
        )

    def html(self):
        return get_template('new_account.jinja2').render(homepage_url=os.getenv('FRONTEND_URL'))


class ConfirmYourEmailMail(Mailer):
    def __init__(self, confirm_url, decline_url, *args, **kwargs):
        default_kwargs = {'subject': l10n('confirm-email-mail-subject')}
        self.confirm_url = confirm_url
        self.decline_url = decline_url
        super(ConfirmYourEmailMail, self).__init__(*args, **default_kwargs, **kwargs)

    def text(self):
        return l10n(
            'confirm-email-mail-plain',
            {
                'confirm_email_url': self.confirm_url,
                'decline_email_url': self.decline_url,
            },
        )

    def html(self):
        return get_template('confirm_email.jinja2').render(
            confirm_email_url=self.confirm_url,
            decline_email_url=self.decline_url
        )
