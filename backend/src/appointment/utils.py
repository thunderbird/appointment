import json
import os
import urllib.parse
from urllib import parse

from functools import cache

from argon2 import PasswordHasher
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from appointment.database.models import secret
from appointment.exceptions.misc import UnexpectedBehaviourWarning

ph = PasswordHasher()


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
    if split_path is None or len(split_path) == 0:
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
        clean_url = clean_url.replace(slug, "").rstrip('/')
        # Re-add just the last one
        clean_url = f'{clean_url}/'
        # Decode slug/signature
        slug = urllib.parse.unquote_plus(slug)

    # Return the username and slug/signature decoded, but ensure the clean_url is encoded.
    return username, slug, clean_url


def chunk_list(to_chunk: list, chunk_by: int):
    """Chunk a to_chunk list by chunk_by"""
    for i in range(0, len(to_chunk), chunk_by):
        yield to_chunk[i:i+chunk_by]


def normalize_secrets():
    """Normalizes AWS secrets for Appointment"""
    database_secrets = os.getenv('DATABASE_SECRETS')

    if database_secrets:
        secrets = json.loads(database_secrets)

        host = secrets['host']
        port = secrets['port']

        # If port is not already in the host var, then append it to hostname
        hostname = host
        if f':{port}' not in host:
            hostname = f'{hostname}:{port}'

        os.environ['DATABASE_URL'] = (
            f"mysql+mysqldb://{secrets['username']}:{secrets['password']}@{hostname}/appointment"
        )

    database_enc_secret = os.getenv('DB_ENC_SECRET')

    if database_enc_secret:
        secrets = json.loads(database_enc_secret)

        os.environ['DB_SECRET'] = secrets.get('secret')
        # Technically not db related...might rename this item later.
        os.environ['SIGNED_SECRET'] = secrets.get('signed_secret')
        os.environ['SESSION_SECRET'] = secrets.get('session_secret')
        os.environ['JWT_SECRET'] = secrets.get('jwt_secret')

    smtp_secrets = os.getenv('SMTP_SECRETS')

    if smtp_secrets:
        secrets = json.loads(smtp_secrets)

        os.environ['SMTP_SECURITY'] = 'STARTTLS'
        os.environ['SMTP_URL'] = secrets.get('url')
        os.environ['SMTP_PORT'] = secrets.get('port')
        os.environ['SMTP_USER'] = secrets.get('username')
        os.environ['SMTP_PASS'] = secrets.get('password')
        os.environ['SUPPORT_EMAIL'] = secrets.get('support')

    google_oauth_secrets = os.getenv('GOOGLE_OAUTH_SECRETS')

    if google_oauth_secrets:
        secrets = json.loads(google_oauth_secrets)

        os.environ['GOOGLE_AUTH_CLIENT_ID'] = secrets.get('client_id')
        os.environ['GOOGLE_AUTH_SECRET'] = secrets.get('secret')
        os.environ['GOOGLE_AUTH_PROJECT_ID'] = secrets.get('project_id')
        os.environ['GOOGLE_AUTH_CALLBACK'] = secrets.get('callback_url')

    zoom_secrets = os.getenv('ZOOM_SECRETS')

    if zoom_secrets:
        secrets = json.loads(zoom_secrets)

        os.environ['ZOOM_AUTH_CLIENT_ID'] = secrets.get('client_id')
        os.environ['ZOOM_AUTH_SECRET'] = secrets.get('secret')
        os.environ['ZOOM_API_SECRET'] = secrets.get('api_secret')
        os.environ['ZOOM_API_NEW_APP'] = secrets.get('api_new_app', 'False')

    fxa_secrets = os.getenv('FXA_SECRETS')

    if fxa_secrets:
        secrets = json.loads(fxa_secrets)

        os.environ['FXA_OPEN_ID_CONFIG'] = secrets.get('open_id_config')
        os.environ['FXA_CLIENT_ID'] = secrets.get('client_id')
        os.environ['FXA_SECRET'] = secrets.get('secret')
        os.environ['FXA_CALLBACK'] = secrets.get('callback_url')
        os.environ['FXA_ALLOW_LIST'] = secrets.get('allow_list')
        os.environ['APP_ADMIN_ALLOW_LIST'] = secrets.get('admin_list')
        # Need to stuff these somewhere
        os.environ['POSTHOG_PROJECT_KEY'] = secrets.get('posthog_project_key')
        os.environ['POSTHOG_HOST'] = secrets.get('posthog_host')


def flag_code(reason, debug_obj):
    """Raise and catch the unexpected behaviour warning so we can get proper stacktrace in sentry"""
    import sentry_sdk

    try:
        sentry_sdk.set_extra('debug_object', debug_obj)
        raise UnexpectedBehaviourWarning(message=reason, info=debug_obj)
    except UnexpectedBehaviourWarning as ex:
        sentry_sdk.capture_exception(ex)
