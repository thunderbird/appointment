import json
import os
import pytest

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from appointment.database import models, repo
from appointment.routes.commands import cron_lock


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

    def _run_renew(self, with_db, mock_google_client):
        with patch(f'{self.MODULE}._common_setup'):
            with patch(f'{self.MODULE}.get_google_client', return_value=mock_google_client):
                with patch(f'{self.MODULE}.get_webhook_url', return_value='https://example.com/webhook'):
                    with patch(f'{self.MODULE}.get_engine_and_session', return_value=(None, with_db)):
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

    def test_renews_expiring_channel(
        self, with_db, make_google_calendar, make_external_connections
    ):
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

        self._run_renew(with_db, mock_google_client)

        mock_google_client.stop_channel.assert_called_once()
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

    def test_skips_channel_not_yet_expiring(
        self, with_db, make_google_calendar, make_external_connections
    ):
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
        mock_google_client.stop_channel.assert_not_called()

        with with_db() as db:
            channel = repo.google_calendar_channel.get_by_calendar_id(db, cal.id)
            assert channel is not None
            assert channel.channel_id == 'healthy-channel'

    def test_deletes_channel_for_disconnected_calendar(
        self, with_db, make_google_calendar, make_external_connections
    ):
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

    def test_deletes_channel_when_no_external_connection(
        self, with_db, make_google_calendar
    ):
        """If the calendar has no external connection, the channel record should be removed."""
        cal = make_google_calendar(connected=True)
        self._create_expiring_channel(with_db, cal.id)

        mock_google_client = Mock()
        mock_google_client.SCOPES = ['https://www.googleapis.com/auth/calendar']

        self._run_renew(with_db, mock_google_client)

        mock_google_client.watch_events.assert_not_called()

        with with_db() as db:
            assert repo.google_calendar_channel.get_by_calendar_id(db, cal.id) is None

    def test_deletes_channel_when_watch_returns_none(
        self, with_db, make_google_calendar, make_external_connections
    ):
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

    def test_still_renews_if_stop_channel_fails(
        self, with_db, make_google_calendar, make_external_connections
    ):
        """Failure to stop the old channel should not prevent renewal."""
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
        mock_google_client.stop_channel.side_effect = Exception('Google API error')
        mock_google_client.watch_events.return_value = {
            'id': 'new-channel-id',
            'resourceId': 'new-resource-id',
            'expiration': str(new_expiration_ms),
        }

        self._run_renew(with_db, mock_google_client)

        mock_google_client.watch_events.assert_called_once()

        with with_db() as db:
            updated = repo.google_calendar_channel.get_by_calendar_id(db, cal.id)
            assert updated is not None
            assert updated.channel_id == 'new-channel-id'
            assert updated.state is not None
            assert updated.state != 'old-state'
