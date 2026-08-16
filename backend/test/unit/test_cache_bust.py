"""Tests for BaseConnector.bust_cached_events(): a single SCAN batch is not guaranteed to be
complete, so busting a subscriber's cache could silently leave stale entries behind. scan_iter
walks the whole matching keyspace instead.
"""

from appointment.controller.calendar import BaseConnector
from appointment.defines import REDIS_REMOTE_EVENTS_KEY


class FakeRedis:
    """Minimal in-memory redis stub covering get/set/delete/scan_iter."""

    def __init__(self):
        self.store = {}

    def scan_iter(self, match=None, count=None):
        prefix = match[:-1] if match and match.endswith('*') else match
        for key in list(self.store.keys()):
            if prefix is None or key.startswith(prefix):
                yield key

    def delete(self, *keys):
        removed = 0
        for key in keys:
            if key in self.store:
                del self.store[key]
                removed += 1
        return removed


class TestBustAllCachedEvents:
    def test_deletes_all_matching_keys_across_batches(self):
        redis_instance = FakeRedis()
        connector = BaseConnector(subscriber_id=1, calendar_id=None, redis_instance=redis_instance)
        prefix = f'{REDIS_REMOTE_EVENTS_KEY}:{connector.get_key_body(only_subscriber=True)}'
        for i in range(1200):
            redis_instance.store[f'{prefix}:{i}'] = 'x'
        redis_instance.store['unrelated-key'] = 'keep'

        deleted = connector.bust_cached_events(all_calendars=True)

        assert deleted == 1200
        assert redis_instance.store == {'unrelated-key': 'keep'}

    def test_no_op_without_redis_returns_zero(self):
        connector = BaseConnector(subscriber_id=1, calendar_id=None, redis_instance=None)
        assert connector.bust_cached_events(all_calendars=True) == 0
