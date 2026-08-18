"""Tests for skipping Google polling while a push channel is live (issue #1607).

The property under test throughout is one-directional: when push is trustworthy
we may serve cached data, and when anything about push is uncertain we must fall
back to polling Google. Being wrong in the "poll anyway" direction costs an API
call; being wrong the other way shows users stale availability, so most of these
tests pin down the cases that must *not* be trusted.
"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from appointment.controller.calendar import BaseConnector, GoogleConnector, push_cache_expiry
from appointment.controller.google_watch import (
    CHANNEL_EXPIRY_MARGIN,
    MAX_SYNC_AGE,
    is_push_active,
    push_backed_calendar_ids,
)
from appointment.database import models, repo


class FakeRedis:
    """Minimal in-memory stand-in covering the calls the cache layer makes."""

    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value
        return True

    def delete(self, *keys):
        removed = 0
        for key in keys:
            if key in self.store:
                del self.store[key]
                removed += 1
        return removed

    def scan_iter(self, match=None, count=None):
        # Only the trailing-'*' form is used by the cache layer.
        prefix = match[:-1] if match and match.endswith('*') else match
        for key in list(self.store.keys()):
            if prefix is None or key.startswith(prefix):
                yield key

    def scan(self, cursor, match=None):
        return 0, list(self.scan_iter(match=match))


def _channel(**overrides):
    """A channel that is healthy unless a test makes it otherwise."""
    now = datetime.now(tz=timezone.utc)
    defaults = {
        'expiration': now + timedelta(days=6),
        'sync_token': 'sync-token',
        'last_synced_at': now,
    }
    defaults.update(overrides)
    return models.GoogleCalendarChannel(**defaults)


GOOGLE_CREDS = json.dumps({
    'token': 'fake-token',
    'refresh_token': 'fake-refresh',
    'client_id': 'fake-client-id',
    'client_secret': 'fake-secret',
})


class TestIsPushActive:
    """The gate that decides whether polling can be skipped."""

    def test_healthy_channel_is_active(self):
        assert is_push_active(_channel()) is True

    def test_missing_channel_is_not_active(self):
        # A calendar with no channel at all must keep polling.
        assert is_push_active(None) is False

    def test_expired_channel_is_not_active(self):
        assert is_push_active(_channel(expiration=datetime.now(tz=timezone.utc) - timedelta(minutes=1))) is False

    def test_channel_inside_expiry_margin_is_not_active(self):
        # Google stops delivering the moment the channel lapses, so we have to
        # stop trusting it slightly early rather than exactly at expiry.
        expiring = datetime.now(tz=timezone.utc) + (CHANNEL_EXPIRY_MARGIN / 2)
        assert is_push_active(_channel(expiration=expiring)) is False

    def test_channel_without_sync_token_is_not_active(self):
        # Without a delta chain a notification cannot tell us what changed.
        assert is_push_active(_channel(sync_token=None)) is False

    def test_never_synced_channel_is_not_active(self):
        assert is_push_active(_channel(last_synced_at=None)) is False

    def test_channel_stale_beyond_max_sync_age_is_not_active(self):
        """Push and reconciliation both silently dead -> stop trusting push.

        This is the backstop that turns an undetectable failure (notifications
        simply never arriving) into a detectable one.
        """
        stale = datetime.now(tz=timezone.utc) - (MAX_SYNC_AGE + timedelta(minutes=1))
        assert is_push_active(_channel(last_synced_at=stale)) is False

    def test_naive_datetimes_are_treated_as_utc(self):
        """Columns come back naive; comparing them to aware values must not raise."""
        naive_future = (datetime.now(tz=timezone.utc) + timedelta(days=6)).replace(tzinfo=None)
        naive_now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        assert is_push_active(_channel(expiration=naive_future, last_synced_at=naive_now)) is True


class TestPushBackedCalendarIds:
    def test_only_returns_calendars_with_live_channels(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=GOOGLE_CREDS
        )
        watched = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )
        unwatched = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=watched.id,
                channel_id='channel-a',
                resource_id='resource-a',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=6),
                state='state-a',
                sync_token='token-a',
                last_synced_at=datetime.now(tz=timezone.utc),
            )

            calendars = [repo.calendar.get(db, watched.id), repo.calendar.get(db, unwatched.id)]
            backed = push_backed_calendar_ids(db, calendars)

        assert watched.user in backed
        assert unwatched.user not in backed

    def test_expired_channel_is_excluded(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=GOOGLE_CREDS
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='channel-expired',
                resource_id='resource-expired',
                expiration=datetime.now(tz=timezone.utc) - timedelta(hours=1),
                state='state-expired',
                sync_token='token-expired',
                last_synced_at=datetime.now(tz=timezone.utc),
            )

            backed = push_backed_calendar_ids(db, [repo.calendar.get(db, calendar.id)])

        assert backed == set()


class TestGetBusyTimeCaching:
    """The hot path: freebusy was called on *every* availability request."""

    @pytest.fixture(autouse=True)
    def push_enabled(self, monkeypatch):
        """Watch channels only exist under this flag, so the cache path needs it on."""
        monkeypatch.setenv('GOOGLE_INVITE_ENABLED', 'True')

    @staticmethod
    def _connector(db, subscriber_id, calendar, redis_instance, google_client):
        return GoogleConnector(
            db=db,
            redis_instance=redis_instance,
            google_client=google_client,
            remote_calendar_id=calendar.user,
            calendar_id=calendar.id,
            subscriber_id=subscriber_id,
            google_tkn=GOOGLE_CREDS,
        )

    @staticmethod
    def _make_channel(db, calendar_id, **overrides):
        kwargs = {
            'calendar_id': calendar_id,
            'channel_id': f'channel-{calendar_id}',
            'resource_id': f'resource-{calendar_id}',
            'expiration': datetime.now(tz=timezone.utc) + timedelta(days=6),
            'state': 'state',
            'sync_token': 'token',
            'last_synced_at': datetime.now(tz=timezone.utc),
        }
        kwargs.update(overrides)
        return repo.google_calendar_channel.create(db, **kwargs)

    def test_push_backed_calendar_is_served_from_cache_on_repeat(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        """The actual issue #1607 win: second request makes no Google call."""
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=GOOGLE_CREDS
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        google_client = Mock()
        google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        # get_free_busy returns naive-UTC datetimes, matching the CalDAV connector.
        google_client.get_free_busy.return_value = [
            {'start': datetime(2026, 8, 20, 10, 0), 'end': datetime(2026, 8, 20, 11, 0)}
        ]

        redis_instance = FakeRedis()

        with with_db() as db:
            self._make_channel(db, calendar.id)
            db_cal = repo.calendar.get(db, calendar.id)
            con = self._connector(db, subscriber.id, db_cal, redis_instance, google_client)

            first = con.get_busy_time([db_cal.user], '2026-08-01', '2026-08-31')
            second = con.get_busy_time([db_cal.user], '2026-08-01', '2026-08-31')

        assert first == second
        assert google_client.get_free_busy.call_count == 1

    def test_calendar_without_channel_still_polls_every_request(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        """No channel -> unchanged behaviour, no new staleness introduced."""
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=GOOGLE_CREDS
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        google_client = Mock()
        google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        google_client.get_free_busy.return_value = []

        redis_instance = FakeRedis()

        with with_db() as db:
            db_cal = repo.calendar.get(db, calendar.id)
            con = self._connector(db, subscriber.id, db_cal, redis_instance, google_client)

            con.get_busy_time([db_cal.user], '2026-08-01', '2026-08-31')
            con.get_busy_time([db_cal.user], '2026-08-01', '2026-08-31')

        assert google_client.get_free_busy.call_count == 2

    def test_expired_channel_falls_back_to_polling(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=GOOGLE_CREDS
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        google_client = Mock()
        google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        google_client.get_free_busy.return_value = []

        redis_instance = FakeRedis()

        with with_db() as db:
            self._make_channel(
                db, calendar.id, expiration=datetime.now(tz=timezone.utc) - timedelta(minutes=1)
            )
            db_cal = repo.calendar.get(db, calendar.id)
            con = self._connector(db, subscriber.id, db_cal, redis_instance, google_client)

            con.get_busy_time([db_cal.user], '2026-08-01', '2026-08-31')
            con.get_busy_time([db_cal.user], '2026-08-01', '2026-08-31')

        assert google_client.get_free_busy.call_count == 2

    def test_mixed_batch_polls_only_the_unbacked_calendar(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        """A watched and an unwatched calendar in one request.

        The unwatched one must still be fetched fresh every time; the watched one
        must not re-hit Google.
        """
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=GOOGLE_CREDS
        )
        watched = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )
        unwatched = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        google_client = Mock()
        google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        google_client.get_free_busy.return_value = []

        redis_instance = FakeRedis()

        with with_db() as db:
            self._make_channel(db, watched.id)
            db_watched = repo.calendar.get(db, watched.id)
            db_unwatched = repo.calendar.get(db, unwatched.id)
            con = self._connector(db, subscriber.id, db_watched, redis_instance, google_client)

            ids = [db_watched.user, db_unwatched.user]
            con.get_busy_time(ids, '2026-08-01', '2026-08-31')
            first_round = google_client.get_free_busy.call_count
            con.get_busy_time(ids, '2026-08-01', '2026-08-31')
            second_round = google_client.get_free_busy.call_count - first_round

        # Round 1: one call for each partition. Round 2: only the unbacked one.
        assert first_round == 2
        assert second_round == 1

    def test_cache_key_distinguishes_calendar_sets(
        self, with_db, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        """A request for one calendar must not be answered from a two-calendar entry."""
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=GOOGLE_CREDS
        )
        cal_a = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )
        cal_b = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        google_client = Mock()
        google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        google_client.get_free_busy.return_value = []

        redis_instance = FakeRedis()

        with with_db() as db:
            self._make_channel(db, cal_a.id)
            self._make_channel(db, cal_b.id)
            db_a = repo.calendar.get(db, cal_a.id)
            db_b = repo.calendar.get(db, cal_b.id)
            con = self._connector(db, subscriber.id, db_a, redis_instance, google_client)

            con.get_busy_time([db_a.user, db_b.user], '2026-08-01', '2026-08-31')
            con.get_busy_time([db_a.user], '2026-08-01', '2026-08-31')

        assert google_client.get_free_busy.call_count == 2

    def test_cache_is_bounded_by_push_expiry(self):
        """Even a perfectly healthy channel must not cache forever."""
        expiry = push_cache_expiry()
        assert 0 < expiry <= 24 * 3600


class TestBusyTimeCacheRoundTrip:
    def test_cached_entries_are_indistinguishable_from_fresh_ones(self):
        """Callers must not be able to tell a cache hit from a Google call."""
        redis_instance = FakeRedis()
        con = BaseConnector(subscriber_id=1, calendar_id=2, redis_instance=redis_instance)

        original = [{'start': datetime(2026, 8, 20, 10), 'end': datetime(2026, 8, 20, 11)}]
        assert con.put_cached_busy_times('scope', original) is True

        assert con.get_cached_busy_times('scope') == original

    def test_malformed_entry_is_treated_as_a_miss(self):
        """A poisoned cache entry must fall back to polling, not raise."""
        redis_instance = FakeRedis()
        con = BaseConnector(subscriber_id=1, calendar_id=2, redis_instance=redis_instance)
        key_scope = con.obscure_key('scope')
        from appointment.defines import REDIS_REMOTE_EVENTS_KEY

        redis_instance.set(
            f'{REDIS_REMOTE_EVENTS_KEY}:{con.get_key_body()}:{key_scope}', 'not json'
        )

        assert con.get_cached_busy_times('scope') is None


class TestBustAllCachedEvents:
    def test_deletes_every_matching_key(self):
        """Push invalidation must be complete; a survivor is silent divergence.

        The pre-existing bust_cached_events reads a single SCAN batch, which is
        not guaranteed to return everything.
        """
        redis_instance = FakeRedis()
        con = BaseConnector(subscriber_id=1, calendar_id=2, redis_instance=redis_instance)

        for i in range(1200):
            con.put_cached_busy_times(f'scope-{i}', [])

        assert len(redis_instance.store) == 1200
        deleted = con.bust_cached_events(all_calendars=True)

        assert deleted == 1200
        assert redis_instance.store == {}

    def test_is_a_noop_without_redis(self):
        con = BaseConnector(subscriber_id=1, calendar_id=2, redis_instance=None)
        assert con.bust_cached_events() == 0


class TestRecordNotification:
    """What an inbound notification is allowed to change."""

    def _stored_channel(self, db, calendar_id):
        return repo.google_calendar_channel.create(
            db,
            calendar_id=calendar_id,
            channel_id='channel-x',
            resource_id='resource-x',
            expiration=datetime.now(tz=timezone.utc) + timedelta(days=6),
            state='state-x',
            sync_token='token-x',
        )

    def test_expiration_is_left_alone(
        self, with_db, make_google_calendar, make_pro_subscriber
    ):
        """A channel's expiration is fixed when it is created and never moves.

        Google has no renewal mechanism -- a channel is replaced, not extended --
        so a notification carries no expiry news, and re-deriving it from the
        header would only be a second chance to get it wrong.
        """
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id, connected=True)

        with with_db() as db:
            channel = self._stored_channel(db, calendar.id)
            before = channel.expiration

            repo.google_calendar_channel.record_notification(db, channel)

            assert channel.expiration == before
            assert channel.last_notification_at is not None

    def test_notification_does_not_by_itself_make_push_trusted(
        self, with_db, make_google_calendar, make_pro_subscriber
    ):
        """Receiving a notification is not evidence the *sync* succeeded."""
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id, connected=True)

        with with_db() as db:
            channel = self._stored_channel(db, calendar.id)  # never synced
            repo.google_calendar_channel.record_notification(db, channel)

            assert is_push_active(channel) is False


class TestPushDisabledSkipsLookups:
    """Channels are only ever created under GOOGLE_INVITE_ENABLED.

    With the flag off the lookups can only come back empty, and this runs on the
    public availability path, so they must not be issued at all.
    """

    def test_no_db_work_when_the_flag_is_off(self, monkeypatch):
        monkeypatch.setenv('GOOGLE_INVITE_ENABLED', 'False')

        db = Mock()
        con = GoogleConnector(
            db=db,
            redis_instance=None,
            google_client=Mock(),
            remote_calendar_id='remote-id',
            calendar_id=1,
            subscriber_id=1,
            google_tkn=GOOGLE_CREDS,
        )

        assert con._push_backed_remote_ids(['remote-id']) == set()
        assert con._push_backed_for_this_calendar() is False
        db.query.assert_not_called()


class TestGetStale:
    def test_includes_never_synced_and_old_channels_only(
        self, with_db, make_google_calendar, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        fresh_cal = make_google_calendar(subscriber_id=subscriber.id, connected=True)
        stale_cal = make_google_calendar(subscriber_id=subscriber.id, connected=True)
        never_cal = make_google_calendar(subscriber_id=subscriber.id, connected=True)

        now = datetime.now(tz=timezone.utc)

        with with_db() as db:
            for cal, synced in (
                (fresh_cal, now),
                (stale_cal, now - timedelta(hours=2)),
                (never_cal, None),
            ):
                repo.google_calendar_channel.create(
                    db,
                    calendar_id=cal.id,
                    channel_id=f'channel-{cal.id}',
                    resource_id=f'resource-{cal.id}',
                    expiration=now + timedelta(days=6),
                    state='state',
                    sync_token='token',
                    last_synced_at=synced.replace(tzinfo=None) if synced else None,
                )

            stale = repo.google_calendar_channel.get_stale(
                db, synced_before=(now - timedelta(minutes=15)).replace(tzinfo=None)
            )

        stale_calendar_ids = {c.calendar_id for c in stale}
        assert stale_cal.id in stale_calendar_ids
        assert never_cal.id in stale_calendar_ids
        assert fresh_cal.id not in stale_calendar_ids
