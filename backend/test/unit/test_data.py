from argon2 import PasswordHasher

from appointment.controller.data import model_to_csv_buffer, delete_account
from appointment.database import models


class TestData:
    def test_model_to_csv_buffer(self, make_pro_subscriber):
        """Make sure our model to csv buffer is working, scrubbers and all!"""
        ph = PasswordHasher()

        password = 'cool beans'
        subscriber = make_pro_subscriber(password=password)

        buffer = model_to_csv_buffer([subscriber])
        csv_data = buffer.getvalue()

        assert csv_data
        # Check if our scrubber is working as intended
        assert 'subscriber.password' not in csv_data
        assert password not in csv_data
        assert ph.hash(password) not in csv_data
        # Ensure that some of our subscriber data is there
        assert subscriber.email in csv_data
        assert subscriber.username in csv_data

    def test_delete_account(
        self,
        with_db,
        make_pro_subscriber,
        make_appointment,
        make_schedule,
        make_caldav_calendar,
        make_external_connections,
        make_invite,
        make_invite_bucket,
    ):
        """Test that our delete account functionality actually deletes everything"""
        subscriber = make_pro_subscriber()
        calendar = make_caldav_calendar(subscriber_id=subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)
        schedule = make_schedule(calendar_id=calendar.id)
        external_connections = [
            make_external_connections(subscriber_id=subscriber.id, type=models.ExternalConnectionType.fxa),
            make_external_connections(subscriber_id=subscriber.id, type=models.ExternalConnectionType.google),
            make_external_connections(subscriber_id=subscriber.id, type=models.ExternalConnectionType.zoom),
        ]
        invite = make_invite(subscriber_id=subscriber.id)
        invite_bucket = make_invite_bucket(email=subscriber.email, invite_id=invite.id)

        # Get some relationships
        slots = appointment.slots

        # Bunch them together into a list. They must have an id field, otherwise assert them manually.
        models_to_check = [
            subscriber,
            calendar,
            appointment,
            schedule,
            invite,
            invite_bucket,
            *external_connections,
            *slots,
        ]

        with with_db() as db:
            ret = delete_account(db, subscriber)
            assert ret is True

        for model in models_to_check:
            check = db.get(model.__class__, model.id)
            assert check is None, f'Ensuring {model.__class__} is None'
