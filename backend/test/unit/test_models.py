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


class TestWaitingList:
    def test_successful_relationship(self, with_db, make_pro_subscriber, make_invite, make_waiting_list):
        subscriber = make_pro_subscriber()
        invite = make_invite(subscriber_id=subscriber.id)
        waiting_list = make_waiting_list(invite_id=invite.id)

        with with_db() as db:
            db.add(subscriber)
            db.add(invite)
            db.add(waiting_list)

            assert waiting_list.invite == invite
            assert waiting_list.invite.subscriber == subscriber

            assert invite.waiting_list == waiting_list
            assert subscriber.invite.waiting_list == waiting_list

    def test_empty_relationship(self, with_db, make_waiting_list):
        waiting_list = make_waiting_list()

        with with_db() as db:
            db.add(waiting_list)

            assert not waiting_list.invite

    def test_email_is_unique(self, make_waiting_list):
        email = 'greg@example.org'

        waiting_list = make_waiting_list(email=email)
        assert waiting_list

        # Raises integrity error due to unique constraint failure
        with pytest.raises(IntegrityError):
            waiting_list_2 = make_waiting_list(email=email)
            assert not waiting_list_2


class TestInvite:
    def test_owned_invites_are_removed_after_subscriber_is_deleted(self, with_db, make_basic_subscriber, make_invite):
        with with_db() as db:
            subscriber = make_basic_subscriber()
            db.add(subscriber)

            assert len(subscriber.owned_invites) == 0

            invite = make_invite(owner_id=subscriber.id)
            db.add(invite)
            db.refresh(subscriber)

            assert invite
            assert len(subscriber.owned_invites) == 1
            assert subscriber.owned_invites[0].id == invite.id

            # Delete the subscriber
            db.delete(subscriber)
            db.commit()

            # This also deletes the invite
            invite = db.query(models.Invite).filter(models.Invite.id == invite.id).first()
            assert not invite
