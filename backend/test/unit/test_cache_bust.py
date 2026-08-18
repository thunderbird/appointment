"""Cache invalidation has to be exhaustive.

`bust_cached_events` is called by the booking write path immediately before it
re-checks availability, so a key that survives the bust becomes a stale answer on
the one path that is supposed to be authoritative.
"""

from appointment.controller.calendar import BaseConnector


class BatchedFakeRedis:
    """In-memory Redis whose SCAN returns one batch at a time, like the real one.

    This is the whole point of the test: `scan()` is documented to return a
    cursor plus *a* batch, not the complete key set. A fake that returns
    everything in one call would let an implementation that reads a single batch
    look correct.
    """

    BATCH = 10

    def __init__(self):
        self.store = {}

    def set(self, key, value, ex=None):
        self.store[key] = value
        return True

    def get(self, key):
        return self.store.get(key)

    def delete(self, *keys):
        removed = 0
        for key in keys:
            if key in self.store:
                del self.store[key]
                removed += 1
        return removed

    def _matching(self, match):
        prefix = match[:-1] if match and match.endswith('*') else match
        return [k for k in self.store if prefix is None or k.startswith(prefix)]

    def scan(self, cursor, match=None):
        """One batch plus a cursor, exactly as redis-py returns it."""
        keys = self._matching(match)
        batch = keys[cursor:cursor + self.BATCH]
        next_cursor = cursor + self.BATCH
        return (0 if next_cursor >= len(keys) else next_cursor), batch

    def scan_iter(self, match=None, count=None):
        cursor = 0
        while True:
            cursor, batch = self.scan(cursor, match=match)
            yield from batch
            if cursor == 0:
                return


def _connector(redis_instance):
    return BaseConnector(subscriber_id=1, calendar_id=2, redis_instance=redis_instance)


class TestBustCachedEvents:
    def test_deletes_every_key_not_just_the_first_batch(self):
        redis_instance = BatchedFakeRedis()
        con = _connector(redis_instance)

        for i in range(95):
            con.put_cached_events(f'scope-{i}', [])

        assert len(redis_instance.store) == 95

        deleted = con.bust_cached_events(all_calendars=True)

        assert deleted == 95
        assert redis_instance.store == {}

    def test_leaves_other_subscribers_alone(self):
        redis_instance = BatchedFakeRedis()
        mine = _connector(redis_instance)
        theirs = BaseConnector(subscriber_id=99, calendar_id=3, redis_instance=redis_instance)

        for i in range(30):
            mine.put_cached_events(f'scope-{i}', [])
        for i in range(30):
            theirs.put_cached_events(f'scope-{i}', [])

        mine.bust_cached_events(all_calendars=True)

        assert len(redis_instance.store) == 30
        assert theirs.get_cached_events('scope-0') == []

    def test_returns_zero_when_there_is_nothing_to_delete(self):
        con = _connector(BatchedFakeRedis())
        assert con.bust_cached_events() == 0

    def test_is_a_noop_without_redis(self):
        assert _connector(None).bust_cached_events() == 0
