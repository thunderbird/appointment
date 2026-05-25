import json
import os
import time
import pytest

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from appointment.database import models, repo
from appointment.routes.commands import cron_lock, refresh_tokens
from appointment.tasks.locks import acquire_task_lock, release_task_lock, task_lock, TaskLockFailed
from appointment.tasks.zoom import refresh_zoom_tokens as refresh_zoom_tokens_task


def test_cron_lock():
    """Test our cron lock function, this does use disk io but should clean itself up after."""
    test_lock_name = 'test_cron_lock_run'
    test_lock_file_name = f'/tmp/{test_lock_name}.lock'

    # Clean up in case the lock file previously exists
    if os.path.isfile(test_lock_file_name):
        os.remove(test_lock_file_name)

    # Test that the lock works
    with cron_lock(test_lock_name):
        assert os.path.isfile(test_lock_file_name)

    # And cleans itself up
    assert not os.path.isfile(test_lock_file_name)

    # Test a lock already exists case with way too many withs.
    with open(test_lock_file_name, 'w'):
        with pytest.raises(FileExistsError):
            with cron_lock(test_lock_name):
                pass

    # Remove the lock file we manually created
    os.remove(test_lock_file_name)


def test_refresh_zoom_tokens_command_queues_celery_task():
    """CLI refresh command should enqueue task instead of running inline."""
    with patch('appointment.tasks.zoom.refresh_zoom_tokens.delay') as mock_delay:
        refresh_tokens()

    mock_delay.assert_called_once()


def test_acquire_task_lock_returns_token_when_acquired():
    """Lock helper should return a lock token when Redis acquires lock."""

    mock_redis = Mock()
    mock_redis.set.return_value = True

    with patch('appointment.tasks.locks.uuid.uuid4', return_value='abc-123'):
        lock_token = acquire_task_lock(mock_redis, 'refresh_zoom_tokens', ttl_seconds=123)

    assert lock_token == 'abc-123'
    mock_redis.set.assert_called_once_with(
        'lock:task:refresh_zoom_tokens',
        'abc-123',
        nx=True,
        ex=123,
    )


def test_acquire_task_lock_returns_none_when_not_acquired():
    """Lock helper should return None when lock is already held."""

    mock_redis = Mock()
    mock_redis.set.return_value = False

    lock_token = acquire_task_lock(mock_redis, 'refresh_zoom_tokens')

    assert lock_token is None


def test_release_task_lock_deletes_when_token_matches():
    """Lock helper should delete the key when the stored token matches."""
    mock_pipe = Mock()
    mock_pipe.get.return_value = 'abc-123'
    mock_pipe.__enter__ = Mock(return_value=mock_pipe)
    mock_pipe.__exit__ = Mock(return_value=False)

    mock_redis = Mock()
    mock_redis.pipeline.return_value = mock_pipe

    release_task_lock(mock_redis, 'refresh_zoom_tokens', 'abc-123')

    mock_pipe.watch.assert_called_once_with('lock:task:refresh_zoom_tokens')
    mock_pipe.multi.assert_called_once()
    mock_pipe.delete.assert_called_once_with('lock:task:refresh_zoom_tokens')
    mock_pipe.execute.assert_called_once()


def test_release_task_lock_skips_when_token_differs():
    """Lock helper should not delete the key when a different token owns it."""
    mock_pipe = Mock()
    mock_pipe.get.return_value = 'other-token'
    mock_pipe.__enter__ = Mock(return_value=mock_pipe)
    mock_pipe.__exit__ = Mock(return_value=False)

    mock_redis = Mock()
    mock_redis.pipeline.return_value = mock_pipe

    release_task_lock(mock_redis, 'refresh_zoom_tokens', 'abc-123')

    mock_pipe.watch.assert_called_once_with('lock:task:refresh_zoom_tokens')
    mock_pipe.multi.assert_not_called()
    mock_pipe.delete.assert_not_called()
    mock_pipe.unwatch.assert_called_once()


def test_task_lock_context_manager_acquires_and_releases():
    """Context manager should acquire lock on entry and release on exit."""

    mock_redis = Mock()
    mock_redis.set.return_value = True

    with patch('appointment.tasks.locks.get_redis', return_value=mock_redis):
        with patch('appointment.tasks.locks.uuid.uuid4', return_value='ctx-token'):
            with patch('appointment.tasks.locks.release_task_lock') as mock_release:
                with task_lock('my_task'):
                    mock_redis.set.assert_called_once()

    mock_release.assert_called_once_with(mock_redis, 'my_task', 'ctx-token')


def test_task_lock_context_manager_raises_when_lock_held():
    """Context manager should raise TaskLockFailed when lock is already held."""

    mock_redis = Mock()
    mock_redis.set.return_value = False

    with patch('appointment.tasks.locks.get_redis', return_value=mock_redis):
        with pytest.raises(TaskLockFailed):
            with task_lock('my_task'):
                pass


def test_task_lock_context_manager_releases_on_exception():
    """Context manager should still release the lock when the body raises."""

    mock_redis = Mock()
    mock_redis.set.return_value = True

    with patch('appointment.tasks.locks.get_redis', return_value=mock_redis):
        with patch('appointment.tasks.locks.uuid.uuid4', return_value='err-token'):
            with patch('appointment.tasks.locks.release_task_lock') as mock_release:
                with pytest.raises(RuntimeError):
                    with task_lock('my_task'):
                        raise RuntimeError('boom')

    mock_release.assert_called_once_with(mock_redis, 'my_task', 'err-token')


def test_task_lock_context_manager_proceeds_without_redis():
    """Context manager should proceed without locking when Redis is unavailable."""

    ran = False
    with patch('appointment.tasks.locks.get_redis', return_value=None):
        with task_lock('my_task'):
            ran = True

    assert ran


def test_refresh_zoom_tokens_task_skips_when_lock_is_held():
    """Celery task should skip execution when lock cannot be acquired."""

    @contextmanager
    def _failing_lock(task_name, ttl_seconds=None):
        raise TaskLockFailed('already locked')

    with patch('appointment.tasks.zoom.task_lock', side_effect=_failing_lock):
        with patch('appointment.commands.refresh_zoom_tokens.run') as mock_run:
            refresh_zoom_tokens_task()

    mock_run.assert_not_called()


def test_refresh_zoom_tokens_task_acquires_lock_for_run():
    """Celery task should run inside the task_lock context manager."""

    lock_entered = False

    @contextmanager
    def _tracking_lock(task_name, ttl_seconds=None):
        nonlocal lock_entered
        lock_entered = True
        yield

    with patch('appointment.tasks.zoom.task_lock', side_effect=_tracking_lock):
        with patch('appointment.commands.refresh_zoom_tokens.run') as mock_run:
            refresh_zoom_tokens_task()

    assert lock_entered
    mock_run.assert_called_once()


def test_refresh_zoom_tokens_task_uses_function_name_for_lock():
    """Task should use its own function name as lock key scope."""

    captured_name = None

    @contextmanager
    def _capture_lock(task_name, ttl_seconds=None):
        nonlocal captured_name
        captured_name = task_name
        raise TaskLockFailed('test')

    with patch('appointment.tasks.zoom.task_lock', side_effect=_capture_lock):
        refresh_zoom_tokens_task()

    assert captured_name == 'refresh_zoom_tokens'


def _make_google_token():
    return json.dumps(
        {
            'token': 'fake-access-token',
            'refresh_token': 'fake-refresh-token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'fake-client-id',
            'client_secret': 'fake-client-secret',
        }
    )


class TestBackfillGoogleChannels:
    """Tests that the backfill command only creates watch channels
    for connected Google calendars that are the default in a schedule."""

    def test_skips_google_calendar_without_schedule(self, with_db, make_google_calendar, make_external_connections):
        """A connected Google calendar not used by any schedule should be skipped."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        make_google_calendar(connected=True, external_connection_id=ext.id)

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']

        with patch('appointment.commands.backfill_google_channels._common_setup'):
            with patch(
                'appointment.commands.backfill_google_channels.get_google_client', return_value=mock_google_client
            ):
                with patch(
                    'appointment.commands.backfill_google_channels.get_webhook_url',
                    return_value='https://example.com/webhook',
                ):
                    with patch(
                        'appointment.commands.backfill_google_channels.get_engine_and_session',
                        return_value=(None, with_db),
                    ):
                        from appointment.commands.backfill_google_channels import run

                        run()

        mock_google_client.watch_events.assert_not_called()

    def test_creates_channel_for_schedule_calendar(
        self, with_db, make_google_calendar, make_schedule, make_external_connections
    ):
        """A connected Google calendar used by a schedule should get a watch channel."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=True, external_connection_id=ext.id)
        make_schedule(calendar_id=cal.id, active=True)

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        mock_google_client.watch_events.return_value = {
            'id': 'channel-123',
            'resourceId': 'resource-456',
            'expiration': str(int(datetime(2030, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)),
        }
        mock_google_client.get_initial_sync_token.return_value = 'sync-token-abc'

        with patch('appointment.commands.backfill_google_channels._common_setup'):
            with patch(
                'appointment.commands.backfill_google_channels.get_google_client', return_value=mock_google_client
            ):
                with patch(
                    'appointment.commands.backfill_google_channels.get_webhook_url',
                    return_value='https://example.com/webhook',
                ):
                    with patch(
                        'appointment.commands.backfill_google_channels.get_engine_and_session',
                        return_value=(None, with_db),
                    ):
                        from appointment.commands.backfill_google_channels import run

                        run()

        mock_google_client.watch_events.assert_called_once()

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, cal.id)
            assert channel is not None
            assert channel.channel_id == 'channel-123'
            assert channel.resource_id == 'resource-456'
            assert channel.sync_token == 'sync-token-abc'
            assert channel.state is not None

    def test_skips_calendar_with_existing_channel(
        self, with_db, make_google_calendar, make_schedule, make_external_connections
    ):
        """A schedule calendar that already has a watch channel should be skipped."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=True, external_connection_id=ext.id)
        make_schedule(calendar_id=cal.id, active=True)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=cal.id,
                channel_id='existing-channel',
                resource_id='existing-resource',
                expiration=datetime(2030, 1, 1, tzinfo=timezone.utc),
                state='existing-state',
                sync_token='existing-sync',
            )

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']

        with patch('appointment.commands.backfill_google_channels._common_setup'):
            with patch(
                'appointment.commands.backfill_google_channels.get_google_client', return_value=mock_google_client
            ):
                with patch(
                    'appointment.commands.backfill_google_channels.get_webhook_url',
                    return_value='https://example.com/webhook',
                ):
                    with patch(
                        'appointment.commands.backfill_google_channels.get_engine_and_session',
                        return_value=(None, with_db),
                    ):
                        from appointment.commands.backfill_google_channels import run

                        run()

        mock_google_client.watch_events.assert_not_called()

    def test_skips_disconnected_google_calendar(
        self, with_db, make_google_calendar, make_schedule, make_external_connections
    ):
        """A disconnected Google calendar should be skipped even if it's in a schedule.
        It shouldn't be possible to disconnect a default calendar from a schedule but just in case."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=False, external_connection_id=ext.id)
        make_schedule(calendar_id=cal.id, active=True)

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']

        with patch('appointment.commands.backfill_google_channels._common_setup'):
            with patch(
                'appointment.commands.backfill_google_channels.get_google_client', return_value=mock_google_client
            ):
                with patch(
                    'appointment.commands.backfill_google_channels.get_webhook_url',
                    return_value='https://example.com/webhook',
                ):
                    with patch(
                        'appointment.commands.backfill_google_channels.get_engine_and_session',
                        return_value=(None, with_db),
                    ):
                        from appointment.commands.backfill_google_channels import run

                        run()

        mock_google_client.watch_events.assert_not_called()


class TestRenewGoogleChannels:
    """Tests that the renew command correctly refreshes expiring channels."""

    MODULE = 'appointment.commands.renew_google_channels'

    def _run_renew(self, with_db, mock_google_client, mock_stop_task=None):
        with patch(f'{self.MODULE}._common_setup'):
            with patch(f'{self.MODULE}.get_google_client', return_value=mock_google_client):
                with patch(f'{self.MODULE}.get_webhook_url', return_value='https://example.com/webhook'):
                    with patch(f'{self.MODULE}.get_engine_and_session', return_value=(None, with_db)):
                        with patch('appointment.tasks.google.stop_google_channel', mock_stop_task or Mock()):
                            from appointment.commands.renew_google_channels import run

                            run()

    def _create_expiring_channel(self, with_db, calendar_id, hours_until_expiry=12):
        """Create a channel that expires within the renewal threshold (24h)."""
        with with_db() as db:
            return repo.google_calendar_channel.create(
                db,
                calendar_id=calendar_id,
                channel_id='old-channel-id',
                resource_id='old-resource-id',
                expiration=datetime.now(tz=timezone.utc) + timedelta(hours=hours_until_expiry),
                state='old-state',
                sync_token='old-sync-token',
            )

    def test_renews_expiring_channel(self, with_db, make_google_calendar, make_external_connections):
        """An expiring channel gets renewed with new ids and expiration."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=True, external_connection_id=ext.id)
        self._create_expiring_channel(with_db, cal.id)

        new_expiration_ms = int(datetime(2030, 6, 1, tzinfo=timezone.utc).timestamp() * 1000)
        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        mock_google_client.watch_events.return_value = {
            'id': 'new-channel-id',
            'resourceId': 'new-resource-id',
            'expiration': str(new_expiration_ms),
        }

        mock_stop_task = Mock()
        self._run_renew(with_db, mock_google_client, mock_stop_task)

        mock_stop_task.delay.assert_called_once()
        mock_google_client.watch_events.assert_called_once()

        with with_db() as db:
            updated = repo.google_calendar_channel.get_by_calendar_id(db, cal.id)
            assert updated is not None
            assert updated.channel_id == 'new-channel-id'
            assert updated.resource_id == 'new-resource-id'
            expected = datetime.fromtimestamp(new_expiration_ms / 1000, tz=timezone.utc)
            assert updated.expiration.replace(tzinfo=None) == expected.replace(tzinfo=None)
            assert updated.state is not None
            assert updated.state != 'old-state'

    def test_skips_channel_not_yet_expiring(self, with_db, make_google_calendar, make_external_connections):
        """A channel that expires beyond the 24-hour threshold is left alone."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=True, external_connection_id=ext.id)

        with with_db() as db:
            repo.google_calendar_channel.create(
                db,
                calendar_id=cal.id,
                channel_id='healthy-channel',
                resource_id='healthy-resource',
                expiration=datetime.now(tz=timezone.utc) + timedelta(days=5),
                state='healthy-state',
                sync_token='healthy-sync',
            )

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']

        self._run_renew(with_db, mock_google_client)

        mock_google_client.watch_events.assert_not_called()

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, cal.id)
            assert channel is not None
            assert channel.channel_id == 'healthy-channel'

    def test_deletes_channel_for_disconnected_calendar(self, with_db, make_google_calendar, make_external_connections):
        """If the calendar is disconnected, the channel record should be removed."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=False, external_connection_id=ext.id)
        self._create_expiring_channel(with_db, cal.id)

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']

        self._run_renew(with_db, mock_google_client)

        mock_google_client.watch_events.assert_not_called()

        with with_db() as db:
            assert repo.google_calendar_channel.get_by_calendar_id(db, cal.id) is None

    def test_deletes_channel_when_no_external_connection(self, with_db, make_google_calendar):
        """If the calendar has no external connection, the channel record should be removed."""
        cal = make_google_calendar(connected=True)
        self._create_expiring_channel(with_db, cal.id)

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']

        self._run_renew(with_db, mock_google_client)

        mock_google_client.watch_events.assert_not_called()

        with with_db() as db:
            assert repo.google_calendar_channel.get_by_calendar_id(db, cal.id) is None

    def test_deletes_channel_when_watch_returns_none(self, with_db, make_google_calendar, make_external_connections):
        """If watch_events returns None, the channel record should be cleaned up."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=True, external_connection_id=ext.id)
        self._create_expiring_channel(with_db, cal.id)

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        mock_google_client.watch_events.return_value = None

        self._run_renew(with_db, mock_google_client)

        with with_db() as db:
            assert repo.google_calendar_channel.get_by_calendar_id(db, cal.id) is None

    def test_stop_channel_is_async_and_does_not_block_renewal(
        self, with_db, make_google_calendar, make_external_connections
    ):
        """Stopping the old channel is fire-and-forget via Celery; renewal always proceeds."""
        ext = make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.google,
            token=_make_google_token(),
        )
        cal = make_google_calendar(connected=True, external_connection_id=ext.id)
        self._create_expiring_channel(with_db, cal.id)

        new_expiration_ms = int(datetime(2030, 6, 1, tzinfo=timezone.utc).timestamp() * 1000)
        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']
        mock_google_client.watch_events.return_value = {
            'id': 'new-channel-id',
            'resourceId': 'new-resource-id',
            'expiration': str(new_expiration_ms),
        }

        mock_stop_task = Mock()
        self._run_renew(with_db, mock_google_client, mock_stop_task)

        mock_stop_task.delay.assert_called_once()
        mock_google_client.watch_events.assert_called_once()

        with with_db() as db:
            updated = repo.google_calendar_channel.get_by_calendar_id(db, cal.id)
            assert updated is not None
            assert updated.channel_id == 'new-channel-id'
            assert updated.state is not None
            assert updated.state != 'old-state'

class TestRefreshZoomTokens:
    """Tests that the refresh command correctly renews Zoom OAuth tokens."""

    MODULE = 'appointment.commands.refresh_zoom_tokens'

    @staticmethod
    def _make_zoom_token(**overrides):
        token = {
            'access_token': 'old-access-token',
            'refresh_token': 'old-refresh-token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'scope': 'meeting:read meeting:write user:read',
        }
        token.update(overrides)
        return json.dumps(token)

    def _run_refresh(self, with_db, mock_zoom_client):
        with patch(f'{self.MODULE}._common_setup'):
            with patch(f'{self.MODULE}.get_zoom_client', return_value=mock_zoom_client):
                with patch(f'{self.MODULE}.get_engine_and_session', return_value=(None, with_db)):
                    from appointment.commands.refresh_zoom_tokens import run

                    run()

    def test_token_is_refreshed(self, with_db, make_external_connections):
        """Running the command should trigger a token refresh and persist the new token in the DB."""
        old_token = self._make_zoom_token()
        make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.zoom,
            token=old_token,
        )

        refreshed_token = {
            'access_token': 'new-access-token',
            'refresh_token': 'new-refresh-token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'expires_at': time.time() + 3600,
            'scope': 'meeting:read meeting:write user:read',
        }

        mock_zoom_client = Mock()

        def fake_setup(subscriber_id, token, threshold=0.0):
            mock_zoom_client.client = Mock()
            mock_zoom_client.client.token = refreshed_token

        mock_zoom_client.setup.side_effect = fake_setup
        mock_zoom_client.get_me.return_value = {'id': 'user123'}

        self._run_refresh(with_db, mock_zoom_client)

        mock_zoom_client.get_me.assert_called_once()
        setup_subscriber_id, setup_token = mock_zoom_client.setup.call_args.args
        assert setup_subscriber_id == 1
        assert setup_token['expires_in'] == -100
        assert setup_token['expires_at'] == 0

        with with_db() as db:
            connections = repo.external_connection.get_by_type(
                db, 1, models.ExternalConnectionType.zoom
            )
            assert len(connections) == 1
            stored_token = json.loads(connections[0].token)
            assert stored_token['access_token'] == 'new-access-token'
            assert stored_token['refresh_token'] == 'new-refresh-token'
            assert 'expires_at' in stored_token

    def test_skips_connection_without_token(self, with_db, make_external_connections):
        """Connections with no token should be skipped."""
        make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.zoom,
            token='',
        )

        mock_zoom_client = Mock()
        self._run_refresh(with_db, mock_zoom_client)

        mock_zoom_client.setup.assert_not_called()

    def test_failed_refresh_does_not_stop_others(self, with_db, make_external_connections, make_pro_subscriber):
        """If one token fails to refresh, the command should continue with the rest."""
        make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.zoom,
            token=self._make_zoom_token(),
        )

        subscriber_2 = make_pro_subscriber()
        make_external_connections(
            subscriber_id=subscriber_2.id,
            type=models.ExternalConnectionType.zoom,
            token=self._make_zoom_token(),
        )

        call_count = 0

        def fail_first_setup(subscriber_id, token, threshold=0.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception('Zoom API error')

        mock_zoom_client = Mock()
        mock_zoom_client.setup.side_effect = fail_first_setup

        self._run_refresh(with_db, mock_zoom_client)

        assert mock_zoom_client.setup.call_count == 2

    def test_failed_refresh_marks_external_connection_error(self, with_db, make_external_connections):
        """If token refresh fails, external connection status should be marked as error."""
        make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.zoom,
            token=self._make_zoom_token(),
        )

        mock_zoom_client = Mock()
        mock_zoom_client.setup.side_effect = Exception('Zoom API error')

        self._run_refresh(with_db, mock_zoom_client)

        with with_db() as db:
            connection = repo.external_connection.get_by_type(db, 1, models.ExternalConnectionType.zoom)[0]
            assert connection.status == models.ExternalConnectionStatus.error
            assert connection.status_checked_at is not None

    def test_successful_refresh_resets_external_connection_status(self, with_db, make_external_connections):
        """A successful refresh should mark previously-failed connections back to ok."""
        make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.zoom,
            token=self._make_zoom_token(),
        )

        with with_db() as db:
            connection = repo.external_connection.get_by_type(db, 1, models.ExternalConnectionType.zoom)[0]
            repo.external_connection.update_status(
                db,
                connection,
                models.ExternalConnectionStatus.error,
            )

        refreshed_token = {
            'access_token': 'new-access-token',
            'refresh_token': 'new-refresh-token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'expires_at': time.time() + 3600,
            'scope': 'meeting:read meeting:write user:read',
        }

        mock_zoom_client = Mock()

        def fake_setup(subscriber_id, token, threshold=0.0):
            mock_zoom_client.client = Mock()
            mock_zoom_client.client.token = refreshed_token

        mock_zoom_client.setup.side_effect = fake_setup
        mock_zoom_client.get_me.return_value = {'id': 'user123'}

        self._run_refresh(with_db, mock_zoom_client)

        with with_db() as db:
            connection = repo.external_connection.get_by_type(db, 1, models.ExternalConnectionType.zoom)[0]
            assert connection.status == models.ExternalConnectionStatus.ok
            assert connection.status_checked_at is not None

    def test_orphaned_zoom_connection_is_cleaned_up(self, with_db, make_external_connections):
        """If an external connection has no subscriber, it should be deleted as orphaned."""
        make_external_connections(
            subscriber_id=99999,
            type=models.ExternalConnectionType.zoom,
            token=self._make_zoom_token(),
        )

        mock_zoom_client = Mock()
        self._run_refresh(with_db, mock_zoom_client)

        mock_zoom_client.setup.assert_not_called()

        with with_db() as db:
            assert repo.external_connection.get_zoom(db) == []

    def test_invalid_token_payload_does_not_stop_others(
        self, with_db, make_external_connections, make_pro_subscriber
    ):
        """If one stored token is invalid JSON, the command should still refresh other users."""
        make_external_connections(
            subscriber_id=1,
            type=models.ExternalConnectionType.zoom,
            token='not-json',
        )

        subscriber_2 = make_pro_subscriber()
        make_external_connections(
            subscriber_id=subscriber_2.id,
            type=models.ExternalConnectionType.zoom,
            token=self._make_zoom_token(),
        )

        refreshed_token = {
            'access_token': 'new-access-token',
            'refresh_token': 'new-refresh-token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'expires_at': time.time() + 3600,
            'scope': 'meeting:read meeting:write user:read',
        }

        mock_zoom_client = Mock()

        def fake_setup(subscriber_id, token, threshold=0.0):
            assert subscriber_id == subscriber_2.id
            mock_zoom_client.client = Mock()
            mock_zoom_client.client.token = refreshed_token

        mock_zoom_client.setup.side_effect = fake_setup
        mock_zoom_client.get_me.return_value = {'id': 'user456'}

        self._run_refresh(with_db, mock_zoom_client)

        mock_zoom_client.setup.assert_called_once()
        mock_zoom_client.get_me.assert_called_once()

        with with_db() as db:
            valid_connection = repo.external_connection.get_by_type(
                db, subscriber_2.id, models.ExternalConnectionType.zoom
            )[0]
            assert json.loads(valid_connection.token)['refresh_token'] == 'new-refresh-token'

