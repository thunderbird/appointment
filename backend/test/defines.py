import fnmatch
from datetime import datetime, timedelta

DATEFMT = '%Y-%m-%d'

REDIS_OIDC_TOKEN_INTROSPECT_EXPIRE_FALLBACK = 300

now = datetime.today()
DAY1 = now.strftime(DATEFMT)
DAY2 = (now + timedelta(days=1)).strftime(DATEFMT)
DAY3 = (now + timedelta(days=2)).strftime(DATEFMT)
DAY5 = (now + timedelta(days=4)).strftime(DATEFMT)
DAY14 = (now + timedelta(days=13)).strftime(DATEFMT)

# Standard headers to used for authentication requests
auth_headers = {'authorization': 'Bearer testtokenplsignore'}

TEST_USER_ID = 1
TEST_CALDAV_URL = 'https://caldav.example.org/'
TEST_CALDAV_USER = 'Test'

# Default value for factories to use a random value
FAKER_RANDOM_VALUE = '___faker_random_value___'


def factory_has_value(val) -> bool:
    """For factories"""
    return val != FAKER_RANDOM_VALUE


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
        pattern = match or '*'
        return iter([k for k in list(self.store.keys()) if fnmatch.fnmatch(k, pattern)])
