import json
import re
import urllib.parse
from urllib import parse

from functools import cache

from argon2 import PasswordHasher
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from appointment.database.models import secret

ph = PasswordHasher()


def verify_password(password, hashed_password):
    ph.verify(hashed_password, password)


def get_password_hash(password):
    return ph.hash(password)


def list_first(items: list, default=None):
    """Returns the first item of a list or the default value."""
    return next(iter(items), default)


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


def retrieve_user_url_data(url):
    """URL Decodes, and retrieves username, signature, and main url from /<username>/<signature>/"""
    # Decode the url so it can be parsed correctly
    url = urllib.parse.unquote(url)

    parsed_url = parse.urlparse(url)
    split_path = [x for x in parsed_url.path.split('/') if x]

    if split_path is None or len(split_path) == 0:
        return False
    # If we have more than two entries, grab the last two
    elif len(split_path) > 2:
        split_path = split_path[-2:]

    clean_url = url
    username = split_path[0]
    signature = None
    if len(split_path) > 1:
        signature = split_path[1]
        # Strip any tailing slashes
        clean_url = clean_url.replace(signature, "").rstrip('/')
        # Re-add just the last one
        clean_url = f'{clean_url}/'

    return username, signature, clean_url
