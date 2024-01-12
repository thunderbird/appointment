"""Module: auth

Handle authentification with Auth0 and get subscription data.
"""
import logging
import os
import hashlib
import hmac
import datetime

from sqlalchemy.orm import Session

from .apis.fxa_client import FxaClient
from ..database import repo, schemas, models


def logout(db: Session, subscriber: models.Subscriber, fxa_client: FxaClient | None, deny_previous_tokens=True):
    """Sets a minimum valid issued at time (time). This prevents access tokens issued earlier from working."""
    if deny_previous_tokens:
        subscriber.minimum_valid_iat_time = datetime.datetime.now(datetime.UTC)
        db.add(subscriber)
        db.commit()

    if os.getenv('AUTH_SCHEME') == 'fxa':
        fxa_client.logout()


def sign_url(url: str):
    """helper to sign a given url"""
    secret = os.getenv("SIGNED_SECRET")

    if not secret:
        raise RuntimeError("Missing signed secret environment variable")

    key = bytes(secret, "UTF-8")
    message = f"{url}".encode()
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature


def signed_url_by_subscriber(subscriber: schemas.Subscriber):
    """helper to generated signed url for given subscriber"""
    short_url = os.getenv("SHORT_BASE_URL")
    base_url = f"{os.getenv('FRONTEND_URL')}/user"

    # If we don't have a short url, then use the default url with /user added to it
    if not short_url:
        short_url = base_url

    # We sign with a different hash that the end-user doesn't have access to
    # We also need to use the default url, as short urls are currently setup as a redirect
    url = f"{base_url}/{subscriber.username}/{subscriber.short_link_hash}"

    signature = sign_url(url)

    # We return with the signed url signature
    return f"{short_url}/{subscriber.username}/{signature}"
