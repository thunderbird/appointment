"""Module: auth

Handle authentication with Thunderbird Accounts or FxA and get subscription data.
"""

import os
import hashlib
import hmac
import datetime
import urllib.parse

from sqlalchemy.orm import Session

from .apis.accounts_client import AccountsClient
from .apis.fxa_client import FxaClient
from ..database import schemas, models, repo


def logout(
    db: Session,
    subscriber: models.Subscriber,
    auth_client: FxaClient | AccountsClient | None,
    deny_previous_tokens=True,
):
    """Sets a minimum valid issued at time (time). This prevents access tokens issued earlier from working."""
    if deny_previous_tokens:
        subscriber.minimum_valid_iat_time = datetime.datetime.now(datetime.UTC)
        db.add(subscriber)
        db.commit()

    if auth_client:
        auth_client.logout()


def sign_url(url: str):
    """helper to sign a given url"""
    secret = os.getenv('SIGNED_SECRET')

    if not secret:
        raise RuntimeError('Missing signed secret environment variable')

    key = bytes(secret, 'UTF-8')
    message = f'{url}'.encode()
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature


def signed_url_by_subscriber(subscriber: schemas.Subscriber):
    """helper to generated signed url for given subscriber"""
    short_url = os.getenv('SHORT_BASE_URL')
    base_url = f"{os.getenv('FRONTEND_URL')}/user"

    # If we don't have a short url, then use the default url with /user added to it
    if not short_url:
        short_url = base_url

    url_safe_username = urllib.parse.quote_plus(subscriber.username)

    # We sign with a different hash that the end-user doesn't have access to
    # We also need to use the default url, as short urls are currently setup as a redirect
    url = f'{base_url}/{url_safe_username}/{subscriber.short_link_hash}'

    signature = sign_url(url)

    # We return with the signed url signature
    return f'{short_url}/{url_safe_username}/{signature}'


def schedule_links_by_subscriber(db, subscriber: models.Subscriber):
    # Generate some schedule links
    schedules = repo.schedule.get_by_subscriber(db, subscriber_id=subscriber.id)
    short_url = os.getenv('SHORT_BASE_URL')
    base_url = f"{os.getenv('FRONTEND_URL')}/user"

    # If we don't have a short url, then use the default url with /user added to it
    if not short_url:
        short_url = base_url

    url_safe_username = urllib.parse.quote_plus(subscriber.username)

    # Empty space at join is for trailing slash!
    return list(
        map(lambda sch: '/'.join([short_url, url_safe_username, urllib.parse.quote_plus(sch.slug), '']), schedules)
    )
