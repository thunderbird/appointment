import datetime

from appointment.database.schemas import Event


class TestEncrypt:
    def test_cached_events(self):
        """Test our model_(dump/load)_redis functions to ensure they don't leak data and work correctly."""
        now = datetime.datetime.now()
        title = 'Private event!'
        description = 'This is a super secret event!'

        cached_event = Event(title=title, start=now, end=now + datetime.timedelta(hours=2), description=description)

        # Ensure individual accessors are not encrypted
        assert cached_event.title == title
        assert cached_event.description == description

        encrypted_blob = cached_event.model_dump_redis()

        # Ensure model_dump_redis values are encrypted
        assert title not in encrypted_blob
        assert description not in encrypted_blob

        new_event_cached = Event.model_load_redis(encrypted_blob)

        # Ensure individual accessors are not encrypted
        assert new_event_cached.title == title
        assert new_event_cached.description == description
