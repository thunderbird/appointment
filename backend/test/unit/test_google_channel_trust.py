"""Tests for is_push_active() and the schema/repo plumbing it reads
(last_synced_at/last_notification_at/last_message_number).
"""

from datetime import datetime, timedelta, UTC

import pytest

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


def _healthy_channel(now: datetime) -> models.GoogleCalendarChannel:
    return _channel(now=now)


def _no_channel(now: datetime) -> None:
    return None


def _expired_channel(now: datetime) -> models.GoogleCalendarChannel:
    return _channel(now=now, expiration=now - timedelta(hours=1))


def _channel_inside_expiry_margin(now: datetime) -> models.GoogleCalendarChannel:
    return _channel(now=now, expiration=now + (CHANNEL_EXPIRY_MARGIN / 2))


def _channel_missing_sync_token(now: datetime) -> models.GoogleCalendarChannel:
    return _channel(now=now, sync_token=None)


def _never_synced_channel(now: datetime) -> models.GoogleCalendarChannel:
    return _channel(now=now, last_synced_at=None)


def _channel_stale_beyond_max_sync_age(now: datetime) -> models.GoogleCalendarChannel:
    return _channel(now=now, last_synced_at=now - MAX_SYNC_AGE - timedelta(minutes=1))


def _channel_with_naive_db_datetimes(now: datetime) -> models.GoogleCalendarChannel:
    return _channel(
        now=now,
        expiration=(now + timedelta(days=1)).replace(tzinfo=None),
        last_synced_at=now.replace(tzinfo=None),
    )


class TestIsPushActive:
    @pytest.mark.parametrize(
        'channel_factory, expected',
        [
            pytest.param(_healthy_channel, True, id='healthy'),
            pytest.param(_no_channel, False, id='none_channel'),
            pytest.param(_expired_channel, False, id='expired'),
            pytest.param(_channel_inside_expiry_margin, False, id='inside_expiry_margin'),
            pytest.param(_channel_missing_sync_token, False, id='missing_sync_token'),
            pytest.param(_never_synced_channel, False, id='never_synced'),
            pytest.param(_channel_stale_beyond_max_sync_age, False, id='stale_beyond_max_sync_age'),
            pytest.param(_channel_with_naive_db_datetimes, True, id='naive_db_datetimes_normalized'),
        ],
    )
    def test_is_push_active_scenarios(self, channel_factory, expected):
        now = datetime.now(tz=UTC)
        channel = channel_factory(now)
        assert is_push_active(channel, now=now) is expected


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
                db,
                calendar_id=never_synced.id,
                channel_id='c1',
                resource_id='r1',
                expiration=now + timedelta(days=1),
                state='s',
                sync_token=None,
                last_synced_at=None,
            )
            repo.google_calendar_channel.create(
                db,
                calendar_id=stale.id,
                channel_id='c2',
                resource_id='r2',
                expiration=now + timedelta(days=1),
                state='s',
                sync_token='tok',
                last_synced_at=now - timedelta(minutes=30),
            )
            repo.google_calendar_channel.create(
                db,
                calendar_id=fresh.id,
                channel_id='c3',
                resource_id='r3',
                expiration=now + timedelta(days=1),
                state='s',
                sync_token='tok',
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
                db,
                calendar_id=calendar.id,
                channel_id='c',
                resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
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
                db,
                calendar_id=calendar.id,
                channel_id='c',
                resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
            )
            repo.google_calendar_channel.record_notification(db, channel, message_number=10)
            repo.google_calendar_channel.record_notification(db, channel, message_number=3)
            assert channel.last_message_number == 10

    def test_expiration_is_refreshed(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        new_expiration = datetime.now(tz=UTC) + timedelta(days=7)
        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='c',
                resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
            )
            repo.google_calendar_channel.record_notification(db, channel, expiration=new_expiration)
            assert channel.expiration.replace(tzinfo=UTC) == new_expiration

    def test_notification_alone_does_not_make_push_active(self, with_db, make_google_calendar):
        """A notification just means something changed; is_push_active shouldn't trust
        a channel until it's actually been synced."""
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='c',
                resource_id='r',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
                sync_token='tok',
            )
            repo.google_calendar_channel.record_notification(db, channel, message_number=1)
            assert is_push_active(channel) is False
