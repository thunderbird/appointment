"""Tests for the push-channel trust gate: is_push_active() and the schema/repo
plumbing (last_synced_at/last_notification_at/last_message_number) it reads.

Slice 2 of issue #1607: this code is purely additive. Nothing on `main` calls
is_push_active() for a caching decision yet -- that wiring is a later slice.
"""

from datetime import datetime, timedelta, UTC

from hypothesis import given, strategies as st

from appointment.controller.google_watch import (
    CHANNEL_EXPIRY_MARGIN,
    MAX_SYNC_AGE,
    is_push_active,
    push_backed_calendar_ids,
)
from appointment.database import models, repo


def _channel(**overrides) -> models.GoogleCalendarChannel:
    """A channel that is_push_active() should consider healthy by default."""
    now = overrides.pop('now', datetime.now(tz=UTC))
    defaults = {
        'calendar_id': 1,
        'channel_id': 'chan-1',
        'resource_id': 'res-1',
        'expiration': now + timedelta(days=1),
        'sync_token': 'sync-token-1',
        'state': 'state-1',
        'last_synced_at': now,
    }
    defaults.update(overrides)
    return models.GoogleCalendarChannel(**defaults)


class TestIsPushActive:
    def test_healthy_channel_is_active(self):
        assert is_push_active(_channel()) is True

    def test_none_channel_is_inactive(self):
        assert is_push_active(None) is False

    def test_expired_channel_is_inactive(self):
        now = datetime.now(tz=UTC)
        channel = _channel(now=now, expiration=now - timedelta(hours=1))
        assert is_push_active(channel, now=now) is False

    def test_channel_inside_expiry_margin_is_inactive(self):
        now = datetime.now(tz=UTC)
        channel = _channel(now=now, expiration=now + (CHANNEL_EXPIRY_MARGIN / 2))
        assert is_push_active(channel, now=now) is False

    def test_missing_sync_token_is_inactive(self):
        channel = _channel(sync_token=None)
        assert is_push_active(channel) is False

    def test_never_synced_channel_is_inactive(self):
        channel = _channel(last_synced_at=None)
        assert is_push_active(channel) is False

    def test_stale_beyond_max_sync_age_is_inactive(self):
        now = datetime.now(tz=UTC)
        channel = _channel(now=now, last_synced_at=now - MAX_SYNC_AGE - timedelta(minutes=1))
        assert is_push_active(channel, now=now) is False

    def test_naive_db_datetimes_are_normalized_without_raising(self):
        now = datetime.now(tz=UTC)
        channel = _channel(
            now=now,
            expiration=(now + timedelta(days=1)).replace(tzinfo=None),
            last_synced_at=now.replace(tzinfo=None),
        )
        assert is_push_active(channel, now=now) is True


class TestPushBackedCalendarIds:
    def test_only_calendars_with_a_live_channel_are_returned(self, with_db, make_google_calendar):
        watched = make_google_calendar(connected=True)
        unwatched = make_google_calendar(connected=True)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=watched.id,
                channel_id='chan-watched',
                resource_id='res-watched',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='state',
                sync_token='sync-token',
                last_synced_at=datetime.now(tz=UTC),
            )
            calendars = db.query(models.Calendar).filter(models.Calendar.id.in_([watched.id, unwatched.id])).all()
            backed = push_backed_calendar_ids(db, calendars)

        assert backed == {watched.user}

    def test_expired_channel_is_excluded(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='chan-expired',
                resource_id='res-expired',
                expiration=datetime.now(tz=UTC) - timedelta(hours=1),
                state='state',
                sync_token='sync-token',
                last_synced_at=datetime.now(tz=UTC),
            )
            calendars = db.query(models.Calendar).filter(models.Calendar.id == calendar.id).all()
            backed = push_backed_calendar_ids(db, calendars)

        assert backed == set()


class TestGetStale:
    def test_includes_never_synced_and_old_excludes_fresh(self, with_db, make_google_calendar):
        never_synced = make_google_calendar(connected=True)
        stale = make_google_calendar(connected=True)
        fresh = make_google_calendar(connected=True)

        now = datetime.now(tz=UTC)
        cutoff = now - timedelta(minutes=15)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db, calendar_id=never_synced.id, channel_id='c1', resource_id='r1',
                expiration=now + timedelta(days=1), state='s', sync_token=None, last_synced_at=None,
            )
            repo.google_calendar_channel.create(
                db, calendar_id=stale.id, channel_id='c2', resource_id='r2',
                expiration=now + timedelta(days=1), state='s', sync_token='tok',
                last_synced_at=now - timedelta(minutes=30),
            )
            repo.google_calendar_channel.create(
                db, calendar_id=fresh.id, channel_id='c3', resource_id='r3',
                expiration=now + timedelta(days=1), state='s', sync_token='tok',
                last_synced_at=now - timedelta(minutes=1),
            )

            stale_channels = repo.google_calendar_channel.get_stale(db, synced_before=cutoff)
            stale_calendar_ids = {c.calendar_id for c in stale_channels}

        assert stale_calendar_ids == {never_synced.id, stale.id}


class TestRecordNotification:
    def test_advances_high_water_mark(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db, calendar_id=calendar.id, channel_id='c', resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1), state='s',
            )
            previous = repo.google_calendar_channel.record_notification(db, channel, message_number=5)
            assert previous is None
            assert channel.last_message_number == 5

            previous = repo.google_calendar_channel.record_notification(db, channel, message_number=6)
            assert previous == 5
            assert channel.last_message_number == 6

    def test_duplicate_does_not_move_mark_backward(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db, calendar_id=calendar.id, channel_id='c', resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1), state='s',
            )
            repo.google_calendar_channel.record_notification(db, channel, message_number=10)
            repo.google_calendar_channel.record_notification(db, channel, message_number=3)
            assert channel.last_message_number == 10

    def test_expiration_is_refreshed(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        new_expiration = datetime.now(tz=UTC) + timedelta(days=7)
        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db, calendar_id=calendar.id, channel_id='c', resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1), state='s',
            )
            repo.google_calendar_channel.record_notification(db, channel, expiration=new_expiration)
            assert channel.expiration.replace(tzinfo=UTC) == new_expiration

    def test_notification_alone_does_not_make_push_active(self, with_db, make_google_calendar):
        """A notification tells us something changed, not that we've synced it -- is_push_active
        must not trust a channel just because a notification arrived."""
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db, calendar_id=calendar.id, channel_id='c', resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1), state='s', sync_token='tok',
            )
            repo.google_calendar_channel.record_notification(db, channel, message_number=1)
            assert is_push_active(channel) is False


class _NoopDb:
    """Stub session: record_notification only calls commit()/refresh(), never queries."""

    def commit(self):
        pass

    def refresh(self, _obj):
        pass


class TestRecordNotificationMonotonicity:
    @given(st.lists(st.one_of(st.integers(min_value=1, max_value=1000), st.none()), max_size=30))
    def test_last_message_number_is_monotonic_non_decreasing(self, deliveries):
        channel = _channel()
        db = _NoopDb()

        seen_max = None
        for message_number in deliveries:
            repo.google_calendar_channel.record_notification(db, channel, message_number=message_number)
            if message_number is not None:
                seen_max = message_number if seen_max is None else max(seen_max, message_number)
            assert channel.last_message_number == seen_max
