"""Cache invalidation has to be exhaustive.

`bust_cached_events` is called by the booking write path immediately before it
re-checks availability, so a key that survives the bust becomes a stale answer on
the one path that is supposed to be authoritative.
"""

from appointment.controller.calendar import BaseConnector
from appointment.defines import REDIS_REMOTE_EVENTS_KEY


class BatchedFakeRedis:
    """In-memory Redis that iterates the way the real one does.

    Two properties matter here, and both come straight from the SCAN docs:

    * A single call returns one batch plus a cursor, never the whole key set.
      "the client should not consider the iteration complete as long as the
      returned cursor is not zero."

    * MATCH "is applied after elements are retrieved from the collection", so a
      batch is sliced out of *all* keys first and only then filtered. When the
      pattern matches a small share of the keyspace, "SCAN will likely return no
      elements in most iterations" -- a call can legitimately return nothing
      while plenty of matching keys are still to come.

    A fake that filtered before batching would never produce that second case,
    and an implementation reading a single batch would look correct.
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

    def scan(self, cursor, match=None):
        all_keys = list(self.store)
        batch = all_keys[cursor:cursor + self.BATCH]
        next_cursor = cursor + self.BATCH

        if match is not None:
            prefix = match[:-1] if match.endswith('*') else match
            batch = [k for k in batch if k.startswith(prefix)]

        return (0 if next_cursor >= len(all_keys) else next_cursor), batch

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

    def test_deletes_when_the_first_batch_matches_nothing(self):
        """The realistic shape, and the one that makes the old code delete zero.

        MATCH is applied after a batch is pulled from the keyspace, so when this
        subscriber's keys sit behind a pile of unrelated ones the first SCAN
        returns an empty list with a non-zero cursor. Reading a single batch
        reads that as "nothing cached" and busts nothing at all.
        """
        redis_instance = BatchedFakeRedis()

        for i in range(40):
            redis_instance.set(f'unrelated:key:{i}', 'x')

        con = _connector(redis_instance)
        for i in range(12):
            con.put_cached_events(f'scope-{i}', [])

        # Precondition: the first batch really is empty, with more to come.
        cursor, first_batch = redis_instance.scan(0, match=f'{REDIS_REMOTE_EVENTS_KEY}:*')
        assert first_batch == []
        assert cursor != 0

        deleted = con.bust_cached_events(all_calendars=True)

        assert deleted == 12
        assert len(redis_instance.store) == 40

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
