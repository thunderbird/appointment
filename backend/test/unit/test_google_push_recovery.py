"""Recovery behaviour when push delivery is imperfect.

Covers the failure modes that make a push-only pipeline diverge from the real
calendar: an invalidated sync token, dropped notifications, duplicate
notifications, and a channel that goes quiet. In every case the requirement is
the same -- local state either catches up, or stops claiming to be current.
"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from appointment.controller.google_watch import is_push_active
from appointment.database import models, repo

MODULE = 'appointment.tasks.google'


def _google_token():
    return json.dumps({
        'token': 'fake-token',
        'refresh_token': 'fake-refresh',
        'client_id': 'fake-client-id',
        'client_secret': 'fake-secret',
        'scopes': ['https://www.googleapis.com/auth/calendar'],
    })


class FakeRedis:
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
        prefix = match[:-1] if match and match.endswith('*') else match
        for key in list(self.store.keys()):
            if prefix is None or key.startswith(prefix):
                yield key


@pytest.fixture
def push_setup(with_db, make_google_calendar, make_external_connections, make_pro_subscriber):
    """A connected Google calendar with a healthy, already-synced channel."""

    def _setup(last_synced_at=None, sync_token='token-v1'):
        subscriber = make_pro_subscriber()
        ext_conn = make_external_connections(
            subscriber.id, type=models.ExternalConnectionType.google, token=_google_token()
        )
        calendar = make_google_calendar(
            subscriber_id=subscriber.id, connected=True, external_connection_id=ext_conn.id
        )

        synced = last_synced_at if last_synced_at is not None else datetime.now(tz=timezone.utc)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='channel-1',
                resource_id='resource-1',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=6),
                state='state-1',
                sync_token=sync_token,
                last_synced_at=synced.replace(tzinfo=None) if synced else None,
            )

        return subscriber, calendar

    return _setup


def _run_sync(with_db, google_client, redis_instance, channel_id='channel-1'):
    with patch(f'{MODULE}.get_google_client', return_value=google_client):
        with patch(f'{MODULE}.get_engine_and_session', return_value=(None, with_db)):
            with patch(f'{MODULE}.get_redis', return_value=redis_instance):
                from appointment.tasks.google import sync_google_calendar_changes

                sync_google_calendar_changes(channel_id)


def _mock_client(**overrides):
    client = Mock()
    client.SCOPES = ['https://www.googleapis.com/auth/calendar']
    client.list_events_sync.return_value = ([], 'token-v2')
    client.get_initial_sync_token.return_value = 'fresh-token'
    client.list_events.return_value = []
    for key, value in overrides.items():
        setattr(client, key, value)
    return client


class TestNormalSync:
    def test_successful_sync_advances_watermark_and_token(self, with_db, push_setup):
        _, calendar = push_setup()
        client = _mock_client()

        _run_sync(with_db, client, FakeRedis())

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel.sync_token == 'token-v2'
            assert channel.last_synced_at is not None
            assert is_push_active(channel) is True

    def test_sync_with_changes_busts_the_cache(self, with_db, push_setup):
        """Otherwise a cached availability answer would outlive the change."""
        subscriber, calendar = push_setup()
        client = _mock_client(
            list_events_sync=Mock(return_value=([{'id': 'evt-1', 'status': 'confirmed'}], 'token-v2'))
        )

        redis_instance = FakeRedis()
        from appointment.controller.calendar import BaseConnector

        con = BaseConnector(
            subscriber_id=subscriber.id, calendar_id=calendar.id, redis_instance=redis_instance
        )
        con.put_cached_busy_times(
            'freebusy_scope', [{'start': datetime(2026, 8, 20, 10), 'end': datetime(2026, 8, 20, 11)}]
        )
        assert len(redis_instance.store) == 1

        _run_sync(with_db, client, redis_instance)

        assert redis_instance.store == {}

    def test_quiet_sync_leaves_cache_intact(self, with_db, push_setup):
        """No changes means the cached answer is still correct -- keep it."""
        subscriber, calendar = push_setup()
        client = _mock_client()  # returns no changed events

        redis_instance = FakeRedis()
        from appointment.controller.calendar import BaseConnector

        con = BaseConnector(
            subscriber_id=subscriber.id, calendar_id=calendar.id, redis_instance=redis_instance
        )
        con.put_cached_busy_times(
            'freebusy_scope', [{'start': datetime(2026, 8, 20, 10), 'end': datetime(2026, 8, 20, 11)}]
        )

        _run_sync(with_db, client, redis_instance)

        assert len(redis_instance.store) == 1


class TestDuplicateNotifications:
    def test_replayed_notification_is_idempotent(self, with_db, push_setup):
        """Google may deliver the same notification twice; syncing twice must be safe."""
        _, calendar = push_setup()
        client = _mock_client(
            list_events_sync=Mock(return_value=([{'id': 'evt-1', 'status': 'confirmed'}], 'token-v2'))
        )
        redis_instance = FakeRedis()

        _run_sync(with_db, client, redis_instance)
        with with_db() as db:
            after_first = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id).sync_token

        _run_sync(with_db, client, redis_instance)
        with with_db() as db:
            after_second = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id).sync_token

        assert after_first == after_second == 'token-v2'


class TestInvalidSyncToken:
    """410 fullSyncRequired -- the delta we would have received is unrecoverable."""

    def test_full_resync_runs_and_token_is_reestablished(self, with_db, push_setup):
        _, calendar = push_setup()
        client = _mock_client(list_events_sync=Mock(return_value=(None, None)))

        _run_sync(with_db, client, FakeRedis())

        # A bounded forward window is re-scanned rather than silently skipped.
        client.list_events.assert_called_once()
        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel.sync_token == 'fresh-token'
            assert is_push_active(channel) is True

    def test_cache_is_dropped_on_invalidation(self, with_db, push_setup):
        """We cannot know what changed, so nothing derived from the lost delta may survive."""
        subscriber, calendar = push_setup()
        client = _mock_client(list_events_sync=Mock(return_value=(None, None)))

        redis_instance = FakeRedis()
        from appointment.controller.calendar import BaseConnector

        con = BaseConnector(
            subscriber_id=subscriber.id, calendar_id=calendar.id, redis_instance=redis_instance
        )
        con.put_cached_busy_times(
            'freebusy_scope', [{'start': datetime(2026, 8, 20, 10), 'end': datetime(2026, 8, 20, 11)}]
        )

        _run_sync(with_db, client, redis_instance)

        assert redis_instance.store == {}

    def test_failure_to_reestablish_leaves_push_untrusted(self, with_db, push_setup):
        """If we cannot get a new token we must stop claiming to be current.

        This is the property that turns an unrecoverable push failure into
        degraded-but-correct polling instead of silent divergence.
        """
        _, calendar = push_setup()
        client = _mock_client(
            list_events_sync=Mock(return_value=(None, None)),
            get_initial_sync_token=Mock(return_value=None),
        )

        _run_sync(with_db, client, FakeRedis())

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            # Watermark not advanced -> ages out -> reads fall back to polling.
            stale = datetime.now(tz=timezone.utc) - timedelta(hours=7)
            channel.last_synced_at = stale.replace(tzinfo=None)
            assert is_push_active(channel) is False

    def test_resync_scan_failure_still_reestablishes_the_token(self, with_db, push_setup):
        """A failing re-scan must not leave the channel without a delta chain."""
        _, calendar = push_setup()
        client = _mock_client(
            list_events_sync=Mock(return_value=(None, None)),
            list_events=Mock(side_effect=Exception('google exploded')),
        )

        _run_sync(with_db, client, FakeRedis())

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel.sync_token == 'fresh-token'


class TestReconciliation:
    """The sweep that bounds how long a dropped notification goes unnoticed."""

    def _run_reconcile(self, with_db, google_client, redis_instance):
        with patch(f'{MODULE}.get_google_client', return_value=google_client):
            with patch(f'{MODULE}.get_engine_and_session', return_value=(None, with_db)):
                with patch(f'{MODULE}.get_redis', return_value=redis_instance):
                    from appointment.tasks.google import reconcile_google_channels

                    reconcile_google_channels()

    def test_stale_channel_is_synced(self, with_db, push_setup):
        """No notification arrived, but the sweep catches the change anyway."""
        _, calendar = push_setup(last_synced_at=datetime.now(tz=timezone.utc) - timedelta(hours=2))
        client = _mock_client()

        self._run_reconcile(with_db, client, FakeRedis())

        client.list_events_sync.assert_called_once()
        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel.sync_token == 'token-v2'

    def test_recently_synced_channel_is_left_alone(self, with_db, push_setup):
        """Reconciliation must not undo the point of the feature by re-polling everything."""
        push_setup(last_synced_at=datetime.now(tz=timezone.utc))
        client = _mock_client()

        self._run_reconcile(with_db, client, FakeRedis())

        client.list_events_sync.assert_not_called()

    def test_one_broken_channel_does_not_stop_the_sweep(
        self, with_db, push_setup, make_google_calendar, make_external_connections, make_pro_subscriber
    ):
        stale = datetime.now(tz=timezone.utc) - timedelta(hours=2)
        push_setup(last_synced_at=stale)

        # A second stale channel whose calendar has no usable connection.
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id, connected=True)
        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='channel-broken',
                resource_id='resource-broken',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=6),
                state='state-broken',
                sync_token='token-broken',
                last_synced_at=stale.replace(tzinfo=None),
            )

        client = _mock_client()
        self._run_reconcile(with_db, client, FakeRedis())

        # The healthy one still got synced despite the broken sibling.
        client.list_events_sync.assert_called_once()
