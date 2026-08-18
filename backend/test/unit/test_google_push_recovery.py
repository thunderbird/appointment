"""Recovery behaviour when push delivery is imperfect.

Covers the failure modes that make a push-only pipeline diverge from the real
calendar: an invalidated sync token, dropped notifications, duplicate
notifications, and a channel that goes quiet. In every case the requirement is
the same -- local state either catches up, or stops claiming to be current.
"""

import httplib2
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from googleapiclient.errors import HttpError

from appointment.controller.google_watch import is_push_active
from appointment.database import models, repo

MODULE = 'appointment.tasks.google'


class BoomError(Exception):
    """A distinctive failure, so tests assert on the real error rather than on
    anything the task machinery might raise in its place."""


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
        degraded-but-correct polling instead of silent divergence. Asserted by
        comparing against the watermark captured *before* the call -- assigning a
        stale value here and re-checking is_push_active would only test that
        function's arithmetic, and would pass even if recovery advanced it.
        """
        _, calendar = push_setup()
        client = _mock_client(
            list_events_sync=Mock(return_value=(None, None)),
            get_initial_sync_token=Mock(return_value=None),
        )

        with with_db() as db:
            before = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id).last_synced_at

        _run_sync(with_db, client, FakeRedis())

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel.last_synced_at == before

    def test_resync_scan_failure_does_not_reestablish_the_token(self, with_db, push_setup):
        """A failed recovery scan must abort recovery, not paper over it.

        A fresh sync token starts its delta chain after the blackout, so storing
        one here would make the changes we failed to re-scan unrecoverable by any
        later sync. Keeping the old (invalid) token means the next attempt
        re-enters recovery instead of skipping past the gap.
        """
        _, calendar = push_setup()
        client = _mock_client(
            list_events_sync=Mock(return_value=(None, None)),
            list_events=Mock(side_effect=BoomError('google exploded')),
        )

        with with_db() as db:
            before = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id).last_synced_at

        with pytest.raises(BoomError):
            _run_sync(with_db, client, FakeRedis())

        client.get_initial_sync_token.assert_not_called()
        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            assert channel.sync_token == 'token-v1'
            assert channel.last_synced_at == before

    def test_resync_scans_a_window_starting_before_now(self, with_db, push_setup):
        """Events that began before the blackout may still have changed during it."""
        push_setup()
        client = _mock_client(list_events_sync=Mock(return_value=(None, None)))

        _run_sync(with_db, client, FakeRedis())

        _, time_min, time_max, _ = client.list_events.call_args.args
        now = datetime.now(tz=timezone.utc)
        # Meaningfully in the past, not merely a few microseconds earlier than
        # the timestamp this assertion happens to compute.
        assert datetime.fromisoformat(time_min) < now - timedelta(days=1)
        assert datetime.fromisoformat(time_max) > now + timedelta(days=1)


class TestSyncFailureIsNotSuccess:
    """A failed sync must never look like a quiet one.

    list_events_sync used to swallow non-410 errors and return ([], None), which
    the caller could not distinguish from "nothing changed" -- so it stamped the
    watermark, kept serving the un-busted cache, and hid the channel from the
    reconciliation sweep, which filters on that same watermark. Persistent errors
    therefore produced a channel that self-reported healthy forever.
    """

    def _captured(self, with_db, calendar_id):
        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar_id)
            return channel.last_synced_at, channel.sync_token

    def test_transport_error_propagates_and_advances_nothing(self, with_db, push_setup):
        _, calendar = push_setup()
        client = _mock_client(list_events_sync=Mock(side_effect=BoomError('502 from google')))

        before = self._captured(with_db, calendar.id)

        with pytest.raises(BoomError):
            _run_sync(with_db, client, FakeRedis())

        assert self._captured(with_db, calendar.id) == before

    def test_missing_sync_token_is_an_error_not_an_empty_sync(self, with_db, push_setup):
        """A completed pagination always ends with a nextSyncToken."""
        _, calendar = push_setup()
        client = _mock_client(list_events_sync=Mock(return_value=([], None)))

        before = self._captured(with_db, calendar.id)

        with pytest.raises(RuntimeError):
            _run_sync(with_db, client, FakeRedis())

        assert self._captured(with_db, calendar.id) == before

    def test_partial_page_failure_records_nothing(self, with_db, push_setup):
        """Page 1 succeeded, page 2 returned a non-410 error.

        Drives the real pagination loop rather than mocking its result, because
        mocking that result is precisely what hid this bug: returning the items
        gathered so far alongside a null token is indistinguishable from a clean
        empty delta.
        """
        _, calendar = push_setup()

        pages = [
            {'items': [{'id': 'evt-1', 'status': 'confirmed'}], 'nextPageToken': 'page-2'},
            HttpError(httplib2.Response({'status': 503}), b'{"error": {"message": "unavailable"}}'),
        ]

        def execute():
            page = pages.pop(0)
            if isinstance(page, Exception):
                raise page
            return page

        service = MagicMock()
        service.events.return_value.list.return_value.execute.side_effect = execute
        service.__enter__.return_value = service
        # A MagicMock __exit__ returns a truthy mock, which would suppress the
        # very exception under test.
        service.__exit__.return_value = False

        from appointment.controller.apis.google_client import GoogleClient

        client = _mock_client()
        client.list_events_sync = lambda *a, **kw: GoogleClient.list_events_sync(
            client, 'cal-id', 'token-v1', None
        )

        before = self._captured(with_db, calendar.id)

        with patch('appointment.controller.apis.google_client.build', return_value=service):
            with pytest.raises(HttpError):
                _run_sync(with_db, client, FakeRedis())

        assert self._captured(with_db, calendar.id) == before

    def test_410_on_a_later_page_still_routes_to_recovery(self, with_db, push_setup):
        """The one status that must not propagate: it means "resync", not "failed"."""
        _, calendar = push_setup()

        pages = [
            {'items': [], 'nextPageToken': 'page-2'},
            HttpError(httplib2.Response({'status': 410}), b'{}'),
        ]

        def execute():
            page = pages.pop(0)
            if isinstance(page, Exception):
                raise page
            return page

        service = MagicMock()
        service.events.return_value.list.return_value.execute.side_effect = execute
        service.__enter__.return_value = service
        # A MagicMock __exit__ returns a truthy mock, which would suppress the
        # very exception under test.
        service.__exit__.return_value = False

        from appointment.controller.apis.google_client import GoogleClient

        client = _mock_client()
        client.list_events_sync = lambda *a, **kw: GoogleClient.list_events_sync(
            client, 'cal-id', 'token-v1', None
        )

        with patch('appointment.controller.apis.google_client.build', return_value=service):
            _run_sync(with_db, client, FakeRedis())

        # Recovery ran rather than the error escaping.
        client.list_events.assert_called_once()
        with with_db() as db:
            assert repo.google_calendar_channel.get_by_calendar_id(db, calendar.id).sync_token == 'fresh-token'

    def test_persistently_failing_channel_ages_out_and_is_reconciled(self, with_db, push_setup):
        """The layered defence, end to end.

        Distinct from the assertions above: an untouched-but-recent watermark
        still reads as trusted for up to MAX_SYNC_AGE, so ageing out has to be
        tested from an already-stale starting point rather than inferred from
        "nothing was advanced".
        """
        stale = datetime.now(tz=timezone.utc) - timedelta(hours=7)
        _, calendar = push_setup(last_synced_at=stale)
        client = _mock_client(list_events_sync=Mock(side_effect=BoomError('still broken')))

        with pytest.raises(BoomError):
            _run_sync(with_db, client, FakeRedis())

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, calendar.id)
            # Reads fall back to polling ...
            assert is_push_active(channel) is False
            # ... and the sweep still sees it, rather than being told it is fresh.
            synced_before = (datetime.now(tz=timezone.utc) - timedelta(minutes=15)).replace(tzinfo=None)
            stale_ids = [c.id for c in repo.google_calendar_channel.get_stale(db, synced_before)]
            assert channel.id in stale_ids


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
