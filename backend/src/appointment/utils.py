import json
import re

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
    except ValueError as e:
        return False
    return True


@cache
def setup_encryption_engine():
    engine = AesEngine()
    # Yes we need to use protected methods to set this up.
    # We could replace it with our own encryption, 
    # but I wanted it to be similar to the db.
    engine._update_key(secret())
    engine._set_padding_mechanism("pkcs5")
    return engine


def retrieve_user_url_data(url):
    """Retrieves username, signature, and main url from /<username>/<signature>/"""
    pattern = r"[\/]([\w\d\-_\.\@!]+)[\/]?([\w\d]*)[\/]?$"
    match = re.findall(pattern, url)

    if match is None or len(match) == 0:
        return False

    # Flatten
    match = match[0]

    clean_url = url
    username = match[0]
    signature = None
    if len(match) > 1:
        signature = match[1]
        clean_url = clean_url.replace(signature, "")

    return username, signature, clean_url
