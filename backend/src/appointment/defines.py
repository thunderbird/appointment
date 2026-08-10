import os
import sys
from enum import StrEnum
from functools import cache

SUPPORTED_LOCALES = ['en', 'de']
FALLBACK_LOCALE = 'en'

DATEFMT = '%Y-%m-%d'
DATETIMEFMT = '%Y-%m-%dT%H:%M:%SZ'

# list of redis keys
REDIS_REMOTE_EVENTS_KEY = 'rmt_events'
REDIS_USER_SESSION_PROFILE_KEY = ':1:tb_accounts_user_session'  # Used with shared redis cache
REDIS_OIDC_TOKEN_KEY = 'introspect_token'

APP_ENV_DEV = 'dev'
APP_ENV_TEST = 'test'
APP_ENV_STAGE = 'stage'
APP_ENV_PROD = 'prod'

APP_NAME = 'Appointment'
APP_NAME_SHORT = 'apmt'

# Custom pydantic error types
END_TIME_BEFORE_START_TIME_ERR = 'end_time_before_start_time'

# CalDAV doesn't provide colours afaik
DEFAULT_CALENDAR_COLOUR = '#c276c5'

# List of Google CalDAV domains
GOOGLE_CALDAV_DOMAINS = ['googleusercontent.com', 'google.com', 'gmail.com']

# Code Accounts returns when a subscriber's Thundermail mailbox hasn't finished provisioning yet
# (see thunderbird-accounts mail/views.py `appointment_caldav_setup`). It's a transient race, not
# a permanent failure, so Appointment retries a few times with backoff before giving up.
ACCOUNTS_MAIL_NOT_READY_CODE = 'mail_account_not_ready'
ACCOUNTS_CALDAV_SETUP_MAX_ATTEMPTS = 3
ACCOUNTS_CALDAV_SETUP_RETRY_DELAY_SECONDS = 2

# Resolves to absolute appointment package path
BASE_PATH = f'{sys.modules["appointment"].__path__[0]}'

ONE_DAY_IN_SECONDS = 86400
SEVEN_DAYS_IN_SECONDS = 604800

# This has to be lazy loaded because the env vars are not available at import time in main.py
@cache
def get_long_base_sign_url():
    """Get the base URL used to sign/verify subscriber's signature in requests"""
    return f'{os.getenv("FRONTEND_URL")}/user'


class AuthScheme(StrEnum):
    """Enum for authentication scheme"""

    PASSWORD = 'password'
    ACCOUNTS = 'accounts'
    OIDC = 'oidc'

    @staticmethod
    def is_password():
        return os.getenv('AUTH_SCHEME') == AuthScheme.PASSWORD

    @staticmethod
    def is_accounts():
        return os.getenv('AUTH_SCHEME') == AuthScheme.ACCOUNTS

    @staticmethod
    def is_oidc():
        return os.getenv('AUTH_SCHEME') == AuthScheme.OIDC
