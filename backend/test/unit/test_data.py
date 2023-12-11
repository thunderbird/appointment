from argon2 import PasswordHasher

from backend.src.appointment.controller.data import model_to_csv_buffer


class TestData:
    def test_model_to_csv_buffer(self, make_pro_subscriber):
        """Make sure our model to csv buffer is working, scrubbers and all!"""
        ph = PasswordHasher()

        password = "cool beans"
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
