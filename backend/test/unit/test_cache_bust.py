"""Tests for ``BaseConnector.bust_cached_events``."""

from appointment.controller.calendar import BaseConnector
from appointment.defines import REDIS_REMOTE_EVENTS_KEY


class EmptyFirstPageRedis:
    """Return no matches on the first SCAN page while its cursor remains nonzero."""

    def __init__(self, target_keys, unrelated_keys):
        self.store = dict.fromkeys([*unrelated_keys, *target_keys], 'value')
        self.target_keys = target_keys
        self.delete_batch_sizes = []

    def scan(self, cursor, match=None, count=None):
        if cursor == 0:
            return 1, []
        prefix = match.removesuffix('*') if match else ''
        return 0, [key for key in self.target_keys if key.startswith(prefix)]

    def scan_iter(self, match=None, count=None):
        cursor = 0
        while True:
            cursor, keys = self.scan(cursor, match=match, count=count)
            yield from keys
            if cursor == 0:
                return

    def delete(self, *keys):
        self.delete_batch_sizes.append(len(keys))
        removed = 0
        for key in keys:
            if self.store.pop(key, None) is not None:
                removed += 1
        return removed


class TestBustAllCachedEvents:
    def test_scans_until_cursor_is_zero_and_deletes_in_batches(self):
        connector = BaseConnector(subscriber_id=1, calendar_id=None)
        prefix = f'{REDIS_REMOTE_EVENTS_KEY}:{connector.get_key_body(only_subscriber=True)}'
        target_keys = [f'{prefix}:{i}' for i in range(501)]
        redis_instance = EmptyFirstPageRedis(target_keys, ['unrelated-key'])
        connector.redis_instance = redis_instance

        deleted = connector.bust_cached_events(all_calendars=True)

        assert deleted is True
        assert redis_instance.store == {'unrelated-key': 'value'}
        assert redis_instance.delete_batch_sizes == [500, 1]
