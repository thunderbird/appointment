import datetime

from starlette_context import request_cycle_context

from appointment.controller.mailer import (
    CancelMail,
    ConfirmationMail,
    RejectionMail,
    ZoomMeetingFailedMail,
    InvitationMail,
    NewBookingMail,
    PendingRequestMail,
    Attachment,
)
from appointment.database import schemas
from appointment.middleware.l10n import L10n


class TestMailer:
    def test_invite(self, with_l10n):
        fake_email = 'to@example.org'

        mailer = InvitationMail(
            to=fake_email,
            name='fake',
            email='fake@example.org',
            date=datetime.datetime.now(),
            duration=30,
            attachments=[Attachment(mime=('text', 'calendar'), filename='test.ics', data=b'')],
        )
        assert mailer.html()
        assert mailer.text()

    def test_confirm(self, faker, with_l10n):
        confirm_url = 'https://example.org/yes'
        deny_url = 'https://example.org/no'
        fake_email = 'to@example.org'
        now = datetime.datetime.now()
        attendee = schemas.AttendeeBase(email=faker.email(), name=faker.name(), timezone='Europe/Berlin')

        mailer = ConfirmationMail(
            confirm_url,
            deny_url,
            attendee.name,
            attendee.email,
            now,
            to=fake_email,
            duration=30,
            schedule_name='test',
            lang='en',
        )
        assert mailer.html()
        assert mailer.text()

        for idx, content in enumerate([mailer.text(), mailer.html()]):
            fault = 'text' if idx == 0 else 'html'
            assert confirm_url in content, fault
            assert deny_url in content, fault
            assert attendee.name in content, fault
            assert attendee.email in content, fault

    def test_new_booking(self, faker, with_l10n):
        fake_email = 'to@example.org'
        now = datetime.datetime.now()
        attendee = schemas.AttendeeBase(email=faker.email(), name=faker.name(), timezone='Europe/Berlin')

        mailer = NewBookingMail(attendee.name, attendee.email, now, 30, 'test schedule', lang='en', to=fake_email)
        assert mailer.html()
        assert mailer.text()

        for idx, content in enumerate([mailer.text(), mailer.html()]):
            fault = 'text' if idx == 0 else 'html'
            assert attendee.name in content, fault
            assert attendee.email in content, fault

    def test_pending(self, faker, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        now = datetime.datetime.now()
        fake_email = 'to@example.org'

        mailer = PendingRequestMail(owner_name=subscriber.name, date=now, duration=30, to=fake_email)
        assert mailer.html()
        assert mailer.text()

        for idx, content in enumerate([mailer.text(), mailer.html()]):
            fault = 'text' if idx == 0 else 'html'
            assert subscriber.name in content, fault

    def test_reject(self, faker, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        now = datetime.datetime.now()
        fake_email = 'to@example.org'

        mailer = RejectionMail(owner_name=subscriber.name, date=now, duration=30, to=fake_email)
        assert mailer.html()
        assert mailer.text()

        for idx, content in enumerate([mailer.text(), mailer.html()]):
            fault = 'text' if idx == 0 else 'html'
            assert subscriber.name in content, fault

    def test_cancel(self, faker, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        now = datetime.datetime.now()
        fake_email = 'to@example.org'

        mailer = CancelMail(owner_name=subscriber.name, date=now, to=fake_email)
        assert mailer.html()
        assert mailer.text()

        for idx, content in enumerate([mailer.text(), mailer.html()]):
            fault = 'text' if idx == 0 else 'html'
            assert subscriber.name in content, fault

    def test_zoom_invite_failed(self, faker, with_l10n):
        fake_title = faker.name()
        fake_email = 'to@example.org'

        mailer = ZoomMeetingFailedMail(appointment_title=fake_title, to=fake_email)
        assert mailer.html()
        assert mailer.text()

        for idx, content in enumerate([mailer.text(), mailer.html()]):
            fault = 'text' if idx == 0 else 'html'
            assert fake_title in content, fault

    def test_booking_emails_use_correct_language(self, faker):
        """Bookee's invite email should be in German (bookee's language from context),
        while the owner's new-booking email should be in English (owner's explicit lang).

        This simulates a German-speaking bookee booking with an English-speaking owner.
        """
        now = datetime.datetime.now()
        attendee = schemas.AttendeeBase(email=faker.email(), name=faker.name(), timezone='Europe/Berlin')

        # Set up a German context (simulating bookee's Accept-Language: de)
        l10n_plugin = L10n()
        l10n_fn = l10n_plugin.get_fluent_with_header('de')

        with request_cycle_context({'l10n': l10n_fn}):
            # InvitationMail goes to the bookee — no explicit lang, uses context (German)
            invite_mail = InvitationMail(
                to='bookee@example.org',
                name='Owner Name',
                email='owner@example.org',
                date=now,
                duration=30,
                attachments=[Attachment(mime=('text', 'calendar'), filename='test.ics', data=b'')],
            )

            # Subject should be in German (bookee's context language)
            assert 'Buchung bestätigt' in invite_mail.subject
            assert 'Booking confirmed' not in invite_mail.subject

            # NewBookingMail goes to the owner — explicit lang='en' (owner's language)
            new_booking_mail = NewBookingMail(
                attendee.name,
                attendee.email,
                now,
                30,
                'Test Schedule',
                to='owner@example.org',
                lang='en',
            )

            # Subject should be in English (owner's language), not German
            assert 'new confirmed booking' in new_booking_mail.subject
            assert 'bestätigte Terminbuchung' not in new_booking_mail.subject

            # Text body should also be in English
            text = new_booking_mail.text()
            assert 'has just booked' in text
            assert 'hat soeben' not in text
