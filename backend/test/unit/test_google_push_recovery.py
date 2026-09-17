"""Tests for Google push sync, fallback/recovery, and channel reconciliation."""

import json
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, patch

from defines import FakeRedis

from appointment.controller.calendar import BaseConnector
from appointment.controller.google_watch import is_push_active
from appointment.database import models, repo
from appointment.defines import REDIS_REMOTE_EVENTS_KEY
from appointment.tasks.google import sync_google_calendar_changes

MODULE = 'appointment.tasks.google'


def _google_token() -> str:
    return json.dumps(
        {
            'token': 'access-token',
            'refresh_token': 'refresh-token',
            'client_id': 'client-id',
            'client_secret': 'client-secret',
            'scopes': ['https://www.googleapis.com/auth/calendar'],
        }
    )


def _mock_client(**overrides):
    client = Mock()
    client.SCOPES = ['https://www.googleapis.com/auth/calendar']
    client.list_events_sync.return_value = ([], 'new-sync-token')
    client.get_initial_sync_token.return_value = 'reestablished-sync-token'
    client.list_events.return_value = []
    for key, value in overrides.items():
        setattr(client, key, value)
    return client


def _run_sync(channel_id, with_db, google_client, redis_instance=None):
    with (
        patch(f'{MODULE}.get_engine_and_session', return_value=(None, with_db)),
        patch(f'{MODULE}.get_google_client', return_value=google_client),
        patch(f'{MODULE}.get_redis', return_value=redis_instance or FakeRedis()),
    ):
        sync_google_calendar_changes(channel_id)


class TestNormalSync:
    def test_successful_sync_advances_watermark_and_token(
        self, with_db, make_google_calendar, make_external_connections
    ):
        ext = make_external_connections(
            subscriber_id=1, type=models.ExternalConnectionType.google, token=_google_token()
        )
        calendar = make_google_calendar(connected=True, external_connection_id=ext.id)

        with with_db() as db:
            channel = repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='chan-1',
                resource_id='res-1',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
                sync_token='old-token',
                last_synced_at=datetime.now(tz=UTC) - timedelta(hours=1),
            )

        _run_sync('chan-1', with_db, _mock_client())

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_channel_id(db, 'chan-1')
            assert channel.sync_token == 'new-sync-token'
            assert channel.last_synced_at is not None
            assert is_push_active(channel) is True

    def test_sync_with_changes_busts_cache(self, with_db, make_google_calendar, make_external_connections):
        ext = make_external_connections(
            subscriber_id=1, type=models.ExternalConnectionType.google, token=_google_token()
        )
        calendar = make_google_calendar(connected=True, external_connection_id=ext.id)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='chan-2',
                resource_id='res-2',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
                sync_token='old-token',
                last_synced_at=datetime.now(tz=UTC) - timedelta(hours=1),
            )

        redis_instance = FakeRedis()
        connector = BaseConnector(calendar.owner_id, calendar.id, redis_instance)
        key = f'{connector.get_key_body()}:cached'
        redis_instance.store[f'{REDIS_REMOTE_EVENTS_KEY}:{key}'] = 'stale-cached-value'

        client = _mock_client(list_events_sync=Mock(return_value=([{'id': 'evt-1'}], 'new-sync-token')))
        _run_sync('chan-2', with_db, client, redis_instance=redis_instance)

        assert redis_instance.store == {}

    def test_quiet_sync_leaves_cache_intact(self, with_db, make_google_calendar, make_external_connections):
        ext = make_external_connections(
            subscriber_id=1, type=models.ExternalConnectionType.google, token=_google_token()
        )
        calendar = make_google_calendar(connected=True, external_connection_id=ext.id)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='chan-3',
                resource_id='res-3',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
                sync_token='old-token',
                last_synced_at=datetime.now(tz=UTC) - timedelta(hours=1),
            )

        redis_instance = FakeRedis()
        redis_instance.store['some-other-key'] = 'untouched'

        _run_sync('chan-3', with_db, _mock_client(), redis_instance=redis_instance)

        assert redis_instance.store == {'some-other-key': 'untouched'}


class TestDuplicateNotifications:
    def test_replayed_sync_is_idempotent(self, with_db, make_google_calendar, make_external_connections):
        ext = make_external_connections(
            subscriber_id=1, type=models.ExternalConnectionType.google, token=_google_token()
        )
        calendar = make_google_calendar(connected=True, external_connection_id=ext.id)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='chan-4',
                resource_id='res-4',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
                sync_token='old-token',
                last_synced_at=datetime.now(tz=UTC) - timedelta(hours=1),
            )

        client = _mock_client()
        _run_sync('chan-4', with_db, client)
        _run_sync('chan-4', with_db, client)

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_channel_id(db, 'chan-4')
            assert channel.sync_token == 'new-sync-token'


class TestInvalidSyncToken:
    def test_410_triggers_bounded_full_resync_and_reestablishes_token(
        self, with_db, make_google_calendar, make_external_connections
    ):
        ext = make_external_connections(
            subscriber_id=1, type=models.ExternalConnectionType.google, token=_google_token()
        )
        calendar = make_google_calendar(connected=True, external_connection_id=ext.id)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='chan-5',
                resource_id='res-5',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
                sync_token='dead-token',
                last_synced_at=datetime.now(tz=UTC) - timedelta(hours=1),
            )

        client = _mock_client(list_events_sync=Mock(return_value=(None, None)))
        _run_sync('chan-5', with_db, client)

        client.get_initial_sync_token.assert_called_once()

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_channel_id(db, 'chan-5')
            assert channel.sync_token == 'reestablished-sync-token'
            assert is_push_active(channel) is True

    def test_failure_to_reestablish_token_leaves_watermark_stale(
        self, with_db, make_google_calendar, make_external_connections
    ):
        """If we can't get a new token, don't touch last_synced_at either, or
        is_push_active() will trust a channel that still has a dead token."""
        ext = make_external_connections(
            subscriber_id=1, type=models.ExternalConnectionType.google, token=_google_token()
        )
        calendar = make_google_calendar(connected=True, external_connection_id=ext.id)

        # 7h > MAX_SYNC_AGE (6h), so this channel should already read as inactive.
        stale_since = datetime.now(tz=UTC) - timedelta(hours=7)
        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=calendar.id,
                channel_id='chan-7',
                resource_id='res-7',
                expiration=datetime.now(tz=UTC) + timedelta(days=1),
                state='s',
                sync_token='dead-token',
                last_synced_at=stale_since,
            )

        client = _mock_client(
            list_events_sync=Mock(return_value=(None, None)),
            get_initial_sync_token=Mock(return_value=None),
        )
        _run_sync('chan-7', with_db, client)

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_channel_id(db, 'chan-7')
            # neither field should have moved
            assert channel.sync_token == 'dead-token'
            assert channel.last_synced_at == stale_since.replace(tzinfo=None)
            assert is_push_active(channel) is False
