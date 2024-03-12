from functools import cache

from argon2 import PasswordHasher
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from appointment.database.models import secret

ph = PasswordHasher()


def verify_password(password, hashed_password):
    ph.verify(hashed_password, password)


def get_password_hash(password):
    return ph.hash(password)


@cache
def setup_encryption_engine():
    engine = AesEngine()
    # Yes we need to use protected methods to set this up.
    # We could replace it with our own encryption, 
    # but I wanted it to be similar to the db.
    engine._update_key(secret())
    engine._set_padding_mechanism("pkcs5")
    return engine
