import pytest
from sqlalchemy.exc import IntegrityError
from appointment.database import models, repo, schemas


class TestAppointment:
    def test_appointment_uuids_are_unique(self, with_db, make_caldav_calendar):
        calendar = make_caldav_calendar()
        with with_db() as db:

            def get_data():
                return schemas.AppointmentFull(
                    title='test',
                    details='my appointment!',
                    calendar_id=calendar.id,
                )

            assert len(db.query(models.Appointment).all()) == 0

            appointments = [
                repo.appointment.create(db, get_data()),
                repo.appointment.create(db, get_data()),
                repo.appointment.create(db, get_data()),
                repo.appointment.create(db, get_data()),
            ]

            assert len(db.query(models.Appointment).all()) == len(appointments)

            for appointment in appointments:
                assert len(db.query(models.Appointment).filter(models.Appointment.uuid == appointment.uuid).all()) == 1


class TestInviteBucket:
    def test_successful_relationship(self, with_db, make_pro_subscriber, make_invite, make_invite_bucket):
        subscriber = make_pro_subscriber()
        invite = make_invite(subscriber_id=subscriber.id)
        invite_bucket = make_invite_bucket(invite_id=invite.id)

        with with_db() as db:
            db.add(subscriber)
            db.add(invite)
            db.add(invite_bucket)

            assert invite_bucket.invite == invite
            assert invite_bucket.invite.subscriber == subscriber

            assert invite.invite_bucket == invite_bucket
            assert subscriber.invite.invite_bucket == invite_bucket

    def test_empty_relationship(self, with_db, make_invite_bucket):
        invite_bucket = make_invite_bucket()

        with with_db() as db:
            db.add(invite_bucket)

            assert not invite_bucket.invite

    def test_email_is_unique(self, make_invite_bucket):
        email = 'greg@example.org'

        invite_bucket = make_invite_bucket(email=email)
        assert invite_bucket

        # Raises integrity error due to unique constraint failure
        with pytest.raises(IntegrityError):
            invite_bucket_2 = make_invite_bucket(email=email)
            assert not invite_bucket_2

