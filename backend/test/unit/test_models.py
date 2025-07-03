import pytest
from sqlalchemy.exc import IntegrityError
from appointment.database import models, repo, schemas
from appointment.database.models import calculate_encrypted_length
from appointment.utils import encrypt


class TestMisc:
    def test_calculate_encrypted_length(self, faker):
        """Ensures an encrypted string is equal to our length calc method.
        We have a list of clear_strs which are random bits of text with variable length.
        We encrypt it (same method used for db fields) and run it through our calculate method,
        and assert they are the same length"""
        clear_strs = [
            'a',
            faker.text(max_nb_chars=7),
            faker.text(max_nb_chars=32),
            faker.text(max_nb_chars=64),
            faker.text(max_nb_chars=82),
            faker.text(max_nb_chars=128),
            faker.text(max_nb_chars=250),
            faker.text(max_nb_chars=256),
            faker.text(max_nb_chars=300),
            faker.text(max_nb_chars=512),
            faker.text(max_nb_chars=1024),
            faker.text(max_nb_chars=2048),
        ]
        for i, clear_str in enumerate(clear_strs):
            assert len(encrypt(clear_str)) == calculate_encrypted_length(len(clear_str))


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

    def test_invited_user_remains_after_owner_is_deleted(self, with_db, make_basic_subscriber, make_invite):
        with with_db() as db:
            subscriber = make_basic_subscriber()
            db.add(subscriber)

            assert len(subscriber.owned_invites) == 0

            invited_subscriber = make_basic_subscriber()
            db.add(invited_subscriber)

            invite = make_invite(subscriber_id=invited_subscriber.id, owner_id=subscriber.id)
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

            # Invited user should remain
            inv_subscriber = db.query(models.Subscriber).filter(models.Subscriber.id == invited_subscriber.id).first()
            assert inv_subscriber

    def test_deleting_invited_user_deletes_invite_and_waiting_list(
        self,
        with_db,
        make_basic_subscriber,
        make_invite,
        make_waiting_list
    ):
        with with_db() as db:
            subscriber = make_basic_subscriber()
            invite = make_invite(subscriber_id=subscriber.id)
            waiting_list = make_waiting_list(invite_id=invite.id)

            db.add(subscriber)
            db.add(invite)
            db.add(waiting_list)

            db.delete(subscriber)
            db.commit()

            subscriber = db.query(models.Subscriber).filter(models.Subscriber.id == subscriber.id).first()
            assert not subscriber
            invite = db.query(models.Invite).filter(models.Invite.id == invite.id).first()
            assert not invite
            waiting_list = db.query(models.WaitingList).filter(models.WaitingList.id == waiting_list.id).first()
            assert not waiting_list


class TestSubscriber:
    def test_get_external_connection_by_type_only(self, with_db, make_basic_subscriber, make_external_connections):
        """Test that get_external_connection returns the first connection of
           the specified type when no type_id is provided"""

        with with_db() as db:
            subscriber = make_basic_subscriber()
            db.add(subscriber)

            # Create multiple external connections of the same type
            make_external_connections(
                subscriber_id=subscriber.id, type=models.ExternalConnectionType.fxa, type_id='fxa_id_1'
            )
            make_external_connections(
                subscriber_id=subscriber.id, type=models.ExternalConnectionType.fxa, type_id='fxa_id_2'
            )
            make_external_connections(
                subscriber_id=subscriber.id, type=models.ExternalConnectionType.google, type_id='google_id_1'
            )

            db.refresh(subscriber)

            # Should return the first FXA connection found
            result = subscriber.get_external_connection(models.ExternalConnectionType.fxa)
            assert result is not None
            assert result.type == models.ExternalConnectionType.fxa
            assert result.type_id == 'fxa_id_1'

            # Should return the Google connection
            result = subscriber.get_external_connection(models.ExternalConnectionType.google)
            assert result is not None
            assert result.type == models.ExternalConnectionType.google
            assert result.type_id == 'google_id_1'

            # Should return None for non-existent type
            result = subscriber.get_external_connection(models.ExternalConnectionType.zoom)
            assert result is None

    def test_get_external_connection_by_type_and_type_id(
        self, with_db, make_basic_subscriber, make_external_connections
    ):
        """Test that get_external_connection returns the specific connection when both type and type_id are provided"""
        with with_db() as db:
            subscriber = make_basic_subscriber()
            db.add(subscriber)

            # Create multiple external connections of the same type with different type_ids
            make_external_connections(
                subscriber_id=subscriber.id, type=models.ExternalConnectionType.fxa, type_id='fxa_id_1'
            )
            make_external_connections(
                subscriber_id=subscriber.id, type=models.ExternalConnectionType.fxa, type_id='fxa_id_2'
            )

            db.refresh(subscriber)

            # Should return the specific connection with matching type_id
            result = subscriber.get_external_connection(models.ExternalConnectionType.fxa, type_id='fxa_id_1')
            assert result is not None
            assert result.type == models.ExternalConnectionType.fxa
            assert result.type_id == 'fxa_id_1'

            result = subscriber.get_external_connection(models.ExternalConnectionType.fxa, type_id='fxa_id_2')
            assert result is not None
            assert result.type == models.ExternalConnectionType.fxa
            assert result.type_id == 'fxa_id_2'

            # Should return None for non-existent type_id
            result = subscriber.get_external_connection(models.ExternalConnectionType.fxa, type_id='non_existent_id')
            assert result is None

    def test_get_external_connection_no_connections(self, with_db, make_basic_subscriber):
        """Test that get_external_connection returns None when subscriber has no external connections"""
        with with_db() as db:
            subscriber = make_basic_subscriber()
            db.add(subscriber)
            db.refresh(subscriber)

            # Should return None when no connections exist
            result = subscriber.get_external_connection(models.ExternalConnectionType.fxa)
            assert result is None

            result = subscriber.get_external_connection(models.ExternalConnectionType.fxa, type_id='any_id')
            assert result is None


class TestExternalConnection:
    def test_update_token_google_with_type_id(self, with_db, make_basic_subscriber, make_external_connections):
        """Test that update_token works for Google connections with type_id"""
        with with_db() as db:
            subscriber = make_basic_subscriber()
            db.add(subscriber)

            # Create a Google external connection
            connection = make_external_connections(
                subscriber_id=subscriber.id,
                type=models.ExternalConnectionType.google,
                type_id='test_google_id',
                token='old_token'
            )

            # Update the token
            new_token = 'new_google_token'
            result = repo.external_connection.update_token(
                db, new_token, subscriber.id, models.ExternalConnectionType.google, 'test_google_id'
            )

            assert result is not None
            assert result.token == new_token
            assert result.id == connection.id

    def test_update_token_google_without_type_id_returns_none(self, with_db, make_basic_subscriber):
        """Test that update_token returns None for Google connections without type_id"""
        with with_db() as db:
            subscriber = make_basic_subscriber()
            db.add(subscriber)

            result = repo.external_connection.update_token(
                db, 'new_token', subscriber.id, models.ExternalConnectionType.google
            )

            assert result is None
