SUPPORTED_LOCALES = ['en', 'de']
FALLBACK_LOCALE = 'en'

DATEFMT = '%Y-%m-%d'
DATETIMEFMT = '%Y-%m-%dT%H:%M:%SZ'

# list of redis keys
REDIS_REMOTE_EVENTS_KEY = 'rmt_events'

APP_ENV_DEV = 'dev'
APP_ENV_TEST = 'test'
APP_ENV_STAGE = 'stage'
APP_ENV_PROD = 'prod'

APP_NAME = 'Appointment'
APP_NAME_SHORT = 'apmt'

INVITES_TO_GIVE_OUT = 10

# Custom pydantic error types
END_TIME_BEFORE_START_TIME_ERR = 'end_time_before_start_time'

# CalDAV doesn't provide colours afaik
DEFAULT_CALENDAR_COLOUR = '#c276c5'

# List of Google CalDAV domains
GOOGLE_CALDAV_DOMAINS = ['googleusercontent.com', 'google.com', 'gmail.com']
