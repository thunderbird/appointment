import json
from typing import Optional
from urllib.parse import urlparse

import requests

from fastapi import APIRouter, Depends, Request
from redis import Redis
from sqlalchemy.orm import Session

from appointment import utils
from appointment.controller.apis.google_client import GoogleClient
from appointment.controller.calendar import CalDavConnector, Tools, GoogleConnector
from appointment.database import models, schemas, repo
from appointment.dependencies.auth import get_subscriber
from appointment.dependencies.database import get_db, get_redis
from appointment.dependencies.google import get_google_client
from appointment.exceptions.validation import RemoteCalendarConnectionError

router = APIRouter()


@router.post('/auth')
def caldav_autodiscover_auth(
    connection: schemas.CalendarConnectionIn,
    db: Session = Depends(get_db),
    subscriber: models.Subscriber = Depends(get_subscriber),
    redis_client: Redis = Depends(get_redis)
):
    """Connects a principal caldav server"""

    # Does url need a protocol?
    if '://' not in connection.url:
        connection.url = f'https://{connection.url}'

    secure_protocol = 'https://' in connection.url

    dns_lookup_cache_key = f'dns:{utils.encrypt(connection.url)}'

    lookup_url = None
    if redis_client:
        lookup_url = redis_client.get(dns_lookup_cache_key)

    # Do a dns lookup first
    if lookup_url is None:
        parsed_url = urlparse(connection.url)
        lookup_url, ttl = Tools.dns_caldav_lookup(parsed_url.hostname, secure=secure_protocol)
        # set the cached lookup for the remainder of the dns ttl
        if redis_client and lookup_url:
            redis_client.set(dns_lookup_cache_key, utils.encrypt(lookup_url), ex=ttl)
    else:
        # Extract the cached value
        lookup_url = utils.decrypt(lookup_url)

    # Check for well-known
    if lookup_url is None:
        lookup_url = Tools.well_known_caldav_lookup(connection.url)

    # If we have a lookup_url then apply it
    if lookup_url:
        connection.url = lookup_url

    # Finally perform any final fixups needed
    connection.url = Tools.fix_caldav_urls(connection.url)

    con = CalDavConnector(
        db=db,
        redis_instance=None,
        url=connection.url,
        user=connection.user,
        password=connection.password,
        subscriber_id=subscriber.id,
        calendar_id=None,
    )

    if not con.test_connection():
        raise RemoteCalendarConnectionError()

    caldav_id = json.dumps([connection.url, connection.user])
    external_connection = repo.external_connection.get_by_type(
        db, subscriber.id, models.ExternalConnectionType.caldav, caldav_id
    )

    # Create or update the external connection
    if not external_connection:
        external_connection_schema = schemas.ExternalConnection(
            name=connection.user,
            type=models.ExternalConnectionType.caldav,
            type_id=caldav_id,
            owner_id=subscriber.id,
            token=connection.password,
        )

        repo.external_connection.create(db, external_connection_schema)
    else:
        repo.external_connection.update_token(
            db, connection.password, subscriber.id, models.ExternalConnectionType.caldav, caldav_id
        )

    con.sync_calendars()
    return True


@router.post('/disconnect')
def disconnect_account(
    type_id: Optional[str] = None,
    db: Session = Depends(get_db),
    subscriber: models.Subscriber = Depends(get_subscriber),
):
    """Disconnects a google account. Removes associated data from our services and deletes the connection details."""
    ec = utils.list_first(
        repo.external_connection.get_by_type(db, subscriber_id=subscriber.id, type=models.ExternalConnectionType.caldav, type_id=type_id)
    )

    if ec is None:
        return RemoteCalendarConnectionError()

    # Deserialize the url/user
    _, user = json.loads(ec.type_id)

    # Remove all the caldav calendars associated with this user
    repo.calendar.delete_by_subscriber_and_provider(db, subscriber.id, provider=models.CalendarProvider.caldav, user=user)

    # Remove their account details
    repo.external_connection.delete_by_type(db, subscriber.id, ec.type, ec.type_id)

    return True
