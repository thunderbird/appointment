import datetime

from appointment.controller.mailer import ConfirmationMail, RejectionMail, ZoomMeetingFailedMail, InvitationMail
from appointment.database import schemas


class TestMailer:
    def test_invite(self, with_l10n):
        fake_email = 'to@example.org'

        mailer = InvitationMail(to=fake_email)
        assert mailer.html()
        assert mailer.text()

    def test_confirm(self, faker, with_l10n):
        confirm_url = 'https://example.org/yes'
        deny_url = 'https://example.org/no'
        fake_email = 'to@example.org'
        now = datetime.datetime.now()
        attendee = schemas.AttendeeBase(email=faker.email(), name=faker.name())

        mailer = ConfirmationMail(confirm_url, deny_url, attendee, now, to=fake_email)
        assert mailer.html()
        assert mailer.text()

        for idx, content in enumerate([mailer.text(), mailer.html()]):
            fault = 'text' if idx == 0 else 'html'
            assert confirm_url in content, fault
            assert deny_url in content, fault
            assert attendee.name in content, fault
            assert attendee.email in content, fault

    def test_reject(self, faker, with_l10n, make_pro_subscriber):
        subscriber = make_pro_subscriber()
        now = datetime.datetime.now()
        fake_email = 'to@example.org'

        mailer = RejectionMail(owner=subscriber, date=now, to=fake_email)
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
