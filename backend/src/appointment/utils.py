import json
import logging
import os
import urllib.parse
from urllib import parse
from datetime import time, datetime, timedelta

from functools import cache

from argon2 import PasswordHasher
from sqlalchemy.engine.url import URL as sqlalchemy_url
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from appointment.database import repo
from appointment.database.models import secret
from appointment.exceptions.misc import UnexpectedBehaviourWarning

ph = PasswordHasher()
log = logging.getLogger(__name__)


def verify_password(password, hashed_password):
    ph.verify(hashed_password, password)


def get_password_hash(password):
    return ph.hash(password)


def list_first(items: list, default=None):
    """Returns the first item of a list or the default value."""
    return next(iter(items), default)


def is_valid_hostname(hostname: str, domain: str) -> bool:
    return hostname == domain or hostname.endswith(f'.{domain}')


def is_json(jsonstring: str):
    """Return true if given string is valid JSON."""
    try:
        json.loads(jsonstring)
    except ValueError:
        return False
    return True


def is_valid_time_range(a: time, b: time, gap: int = 0):
    """Return true if time a is before time b and both have at least the given time gap in minutes."""
    a_datetime = datetime.strptime(a.strftime('%H:%M:%S'), '%H:%M:%S') + timedelta(minutes=gap)
    return a_datetime.time() <= b


@cache
def setup_encryption_engine():
    engine = AesEngine()
    # Yes we need to use protected methods to set this up.
    # We could replace it with our own encryption,
    # but I wanted it to be similar to the db.
    engine._update_key(secret())
    engine._set_padding_mechanism('pkcs5')
    return engine


def encrypt(value):
    return setup_encryption_engine().encrypt(value)


def decrypt(value):
    return setup_encryption_engine().decrypt(value)


def retrieve_user_url_data(url):
    """URL Decodes, and retrieves username, slug/signature, and main url from /<username>/<slug/signature?>/"""
    parsed_url = parse.urlparse(url)
    split_path = [x for x in parsed_url.path.split('/') if x]

    # Check for general validity of the path
    if split_path is None or len(split_path) == 0 or len(split_path) > 3:
        return False

    # Normalize short and long urls to only username and slug/signature (remove the /user/ segment)
    # FIXME: Handle edge case: A user with username='user' might make trouble here
    if len(split_path) > 1 and split_path[0] == 'user':
        split_path.pop(0)

    clean_url = url
    username = urllib.parse.unquote_plus(split_path[0])
    slug = None
    if len(split_path) > 1:
        slug = split_path[1]
        # Strip any tailing slashes
        clean_url = clean_url.replace(slug, '').rstrip('/')
        # Re-add just the last one
        clean_url = f'{clean_url}/'
        # Decode slug/signature
        slug = urllib.parse.unquote_plus(slug)

    # Return the username and slug/signature decoded, but ensure the clean_url is encoded.
    return username, slug, clean_url


def chunk_list(to_chunk: list, chunk_by: int):
    """Chunk a to_chunk list by chunk_by"""
    for i in range(0, len(to_chunk), chunk_by):
        yield to_chunk[i : i + chunk_by]


def determine_database_driver(dialect: str) -> str:
    """Return our preferred ORM driver for the given database dialect.

    :param dialect: A class of database, like "mysql" or "postgresql".
    :type dialect: str

    :return: The string indicator of which driver the ORM should use.
    :rtype: str
    """

    if dialect == 'mysql':
        return 'mysqldb'
    elif dialect == 'postgresql':
        return 'psycopg'
    elif dialect == 'sqlite':
        return 'pysqlite'
    else:
        return None


@cache
def get_database_url() -> str | sqlalchemy_url:
    """Returns a database URL value suitable for passing to SQLAlechemy's ``create_engine`` function. If DATABASE_URL is
    set in the environment, that string will be used, but this is not preferred as there are problems handling some
    special characters. Otherwise (and preferably), uses SQLAlchemy's URL factory to produce working connection URL
    objects in which special character escaping is handled for us.

    :raises ValueError: If a necessary URL component is not configured.

    :return: Either a string or a sqlalchemy.engine.url.URL, depending on configuration.
    :rtype: str | sqlalchemy_url
    """

    # Tests make use of an in-memory SQLite database, and I can't figure out how to make that work with sqlalchemy_url.
    # So we make an exception for that scenario. However, if a url is set directly for other engines, only reluctantly
    # pass that through with a deprecation warning. Preferably pull the URL components from environment variables.
    dialect = os.environ.get('DATABASE_ENGINE', 'mysql')
    if 'DATABASE_URL' in os.environ and dialect != 'sqlite':
        log.info(
            'The use of the DATABASE_URL environment variable is discouraged. Instead, use DATABASE_HOST, '
            'DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_ENGINE, and DATABASE_NAME.'
        )
        return os.environ.get('DATABASE_URL')

    # These are settings we can safely assume defaults about.
    db_name = os.environ.get('DATABASE_NAME', 'appointment')
    driver = determine_database_driver(dialect=dialect)
    port = int(os.environ.get('DATABASE_PORT', '3306'))

    # These settings are secrets and must be set manually.
    host = os.environ.get('DATABASE_HOST')
    username = os.environ.get('DATABASE_USERNAME')
    password = os.environ.get('DATABASE_PASSWORD')

    requirements = {
        'db_name': db_name,
        'dialect': dialect,
        'host': host,
        'password': password,
        'port': port,
        'username': username,
    }
    missing_requirements = [key for key, value in requirements.items() if not value]
    if len(missing_requirements) > 0:
        raise ValueError(f'Missing the following database options: {missing_requirements}')

    # If we've had to compose this from parts, use the SQLAlchemy URL class
    return sqlalchemy_url(
        f'{dialect}+{driver}',
        database=db_name,
        host=host,
        password=password,
        port=port,
        query={},  # "query" as in "query string" for the URI, a key/value map. Ref: https://docs.sqlalchemy.org/en/21/core/engines.html#sqlalchemy.engine.URL.query
        username=username,
    )


def flag_code(reason, debug_obj):
    """Raise and catch the unexpected behaviour warning so we can get proper stacktrace in sentry"""
    import sentry_sdk

    try:
        sentry_sdk.set_extra('debug_object', debug_obj)
        raise UnexpectedBehaviourWarning(message=reason, info=debug_obj)
    except UnexpectedBehaviourWarning as ex:
        sentry_sdk.capture_exception(ex)


def is_in_allow_list(db, email: str):
    """Check this email against our allow list"""

    # Allow existing subscribers to login even if they're not on an allow-list
    subscriber = repo.subscriber.get_by_email(db, email)
    if subscriber:
        return True

    allow_list = os.getenv('FXA_ALLOW_LIST')
    # If we have no allow list, then we allow everyone
    if not allow_list or allow_list == '':
        return True

    return email.endswith(tuple(allow_list.split(',')))


def get_expiry_time_with_grace_period(expiry: int):
    grace_period = max(int(os.getenv('OIDC_EXP_GRACE_PERIOD', 0)), 120)
    expiry += grace_period
    return expiry
