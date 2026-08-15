"""Tests for GoogleConnector.get_busy_time()'s push-backed caching -- the actual fix for
issue #1607 (stop polling Google's freebusy.query on every booking-page load when a push
channel is already live). Slices 2 and 3 built the trust gate and kept it honest; this wires
the one real call site.
"""

from datetime import datetime, timedelta, UTC
from unittest.mock import Mock

from appointment.controller.calendar import GoogleConnector, push_cache_expiry
from appointment.database import repo


class FakeRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value
        return True

    def delete(self, *keys):
        deleted = 0
        for key in keys:
            if key in self.store:
                del self.store[key]
                deleted += 1
        return deleted

    def scan_iter(self, match=None, count=None):
        import fnmatch

        pattern = match or '*'
        return iter([k for k in list(self.store.keys()) if fnmatch.fnmatch(k, pattern)])


def _mock_google_client():
    client = Mock()
    client.SCOPES = ['https://www.googleapis.com/auth/calendar']
    client.get_free_busy.return_value = [
        {'start': datetime(2026, 1, 1, 9), 'end': datetime(2026, 1, 1, 10)}
    ]
    return client


def _channel_for(db, calendar, **overrides):
    now = datetime.now(tz=UTC)
    defaults = {
        'channel_id': f'chan-{calendar.id}',
        'resource_id': f'res-{calendar.id}',
        'expiration': now + timedelta(days=1),
        'state': 's',
        'sync_token': 'tok',
        'last_synced_at': now,
    }
    defaults.update(overrides)
    return repo.google_calendar_channel.create(db, calendar_id=calendar.id, **defaults)


def _connector(db, subscriber_id, remote_calendar_id, redis_instance, google_client):
    return GoogleConnector(
        subscriber_id=subscriber_id,
        calendar_id=None,
        redis_instance=redis_instance,
        db=db,
        remote_calendar_id=remote_calendar_id,
        google_client=google_client,
    )


class TestGetBusyTimeCaching:
    def test_push_backed_calendar_served_from_cache_on_second_call(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            _channel_for(db, calendar)

            google_client = _mock_google_client()
            connector = _connector(db, calendar.owner_id, calendar.user, FakeRedis(), google_client)

            connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')
            connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')

        assert google_client.get_free_busy.call_count == 1

    def test_calendar_without_channel_still_polls_every_request(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            google_client = _mock_google_client()
            connector = _connector(db, calendar.owner_id, calendar.user, FakeRedis(), google_client)

            connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')
            connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')

        assert google_client.get_free_busy.call_count == 2

    def test_expired_channel_falls_back_to_polling(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            _channel_for(db, calendar, expiration=datetime.now(tz=UTC) - timedelta(hours=1))

            google_client = _mock_google_client()
            connector = _connector(db, calendar.owner_id, calendar.user, FakeRedis(), google_client)

            connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')
            connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')

        assert google_client.get_free_busy.call_count == 2

    def test_mixed_batch_polls_only_the_unbacked_calendar(self, with_db, make_google_calendar):
        watched = make_google_calendar(connected=True)
        unwatched = make_google_calendar(connected=True)
        with with_db() as db:
            _channel_for(db, watched)

            google_client = _mock_google_client()
            connector = _connector(db, watched.owner_id, watched.user, FakeRedis(), google_client)

            connector.get_busy_time([watched.user, unwatched.user], '2026-01-01', '2026-01-02')
            connector.get_busy_time([watched.user, unwatched.user], '2026-01-01', '2026-01-02')

        # 1st call: two chunks (cacheable + uncacheable) = 2 get_free_busy calls.
        # 2nd call: cacheable served from cache, only uncacheable polls again = 1 more call.
        assert google_client.get_free_busy.call_count == 3

    def test_cache_key_distinguishes_different_calendar_id_sets(self, with_db, make_google_calendar):
        cal_a = make_google_calendar(connected=True)
        cal_b = make_google_calendar(connected=True)
        with with_db() as db:
            _channel_for(db, cal_a)
            _channel_for(db, cal_b)

            google_client = _mock_google_client()
            connector = _connector(db, cal_a.owner_id, cal_a.user, FakeRedis(), google_client)

            connector.get_busy_time([cal_a.user], '2026-01-01', '2026-01-02')
            connector.get_busy_time([cal_a.user, cal_b.user], '2026-01-01', '2026-01-02')

        # Different calendar-id sets must not share a cache entry.
        assert google_client.get_free_busy.call_count == 2

    def test_push_cache_expiry_is_bounded(self, monkeypatch):
        monkeypatch.delenv('REDIS_EVENT_EXPIRE_SECONDS_PUSH', raising=False)
        assert 0 < push_cache_expiry() <= 24 * 60 * 60


class TestBusyTimeCacheRoundTrip:
    def test_cache_hit_indistinguishable_from_fresh(self, with_db, make_google_calendar):
        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            _channel_for(db, calendar)

            google_client = _mock_google_client()
            connector = _connector(db, calendar.owner_id, calendar.user, FakeRedis(), google_client)

            first = connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')
            second = connector.get_busy_time([calendar.user], '2026-01-01', '2026-01-02')

        assert first == second

    def test_malformed_cache_entry_is_treated_as_a_miss(self, with_db, make_google_calendar):
        """A corrupted or unexpectedly-shaped cache entry (e.g. from a prior schema version)
        must degrade to a cache miss, not raise and take down the whole availability lookup."""
        import json

        calendar = make_google_calendar(connected=True)
        with with_db() as db:
            _channel_for(db, calendar)
            redis_instance = FakeRedis()
            connector = _connector(db, calendar.owner_id, calendar.user, redis_instance, _mock_google_client())

            key_scope = 'freebusy_dummy_2026-01-01_2026-01-02'
            obscured = connector.obscure_key(key_scope)
            redis_key = f'rmt_events:{connector.get_key_body()}:{obscured}'
            redis_instance.store[redis_key] = json.dumps([{'not': 'a valid entry'}])

            assert connector.get_cached_busy_times(key_scope) is None
