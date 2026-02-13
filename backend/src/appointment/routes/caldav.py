import json
import urllib
from typing import Optional
from urllib.parse import urlparse

import sentry_sdk
from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy.orm import Session

from appointment import utils
from appointment.controller.calendar import CalDavConnector, Tools
from appointment.database import models, schemas, repo
from appointment.dependencies.auth import get_subscriber
from appointment.dependencies.database import get_db, get_redis
from appointment.exceptions.calendar import TestConnectionFailed, RemoteCalendarAuthenticationError
from appointment.exceptions.misc import UnexpectedBehaviourWarning
from appointment.exceptions.validation import (
    RemoteCalendarConnectionError,
    GoogleCaldavNotSupported,
    ConnectionContainsDefaultCalendarException,
    RemoteCalendarAuthenticationException,
)
from appointment.l10n import l10n
from appointment.defines import GOOGLE_CALDAV_DOMAINS

router = APIRouter()


@router.post('/auth')
def caldav_autodiscover_auth(
    connection: schemas.CalendarConnectionIn,
    db: Session = Depends(get_db),
    subscriber: models.Subscriber = Depends(get_subscriber),
    redis_client: Redis = Depends(get_redis),
):
    """Connects a principal caldav server"""

    # Does url need a protocol?
    if '://' not in connection.url:
        connection.url = f'https://{connection.url}'

    secure_protocol = 'https://' in connection.url

    dns_lookup_cache_key = f'dns:{utils.encrypt(connection.url)}'

    # Check for an attempt to use Google CalDAV API
    # which we don't support because we use their API directly
    basename = urlparse(connection.url).netloc
    if any([(g in basename) for g in GOOGLE_CALDAV_DOMAINS]):
        raise GoogleCaldavNotSupported()

    lookup_url = None
    if redis_client:
        lookup_url = redis_client.get(dns_lookup_cache_key)

    if lookup_url and 'http' not in lookup_url:
        debug_obj = {'url': lookup_url, 'branch': 'CACHE'}
        # Raise and catch the unexpected behaviour warning so we can get proper stacktrace in sentry...
        try:
            sentry_sdk.set_extra('debug_object', debug_obj)
            raise UnexpectedBehaviourWarning(message='Cache incorrect', info=debug_obj)
        except UnexpectedBehaviourWarning as ex:
            sentry_sdk.capture_exception(ex)

        # Clear cache for that key
        redis_client.delete(dns_lookup_cache_key)

        # Ignore cached result and look it up again
        lookup_url = None

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
    if lookup_url and 'http' not in lookup_url:
        connection.url = urllib.parse.urljoin(connection.url, lookup_url)
    elif lookup_url:
        connection.url = lookup_url

    con = CalDavConnector(
        db=db,
        redis_instance=None,
        url=connection.url,
        user=connection.user,
        password=connection.password,
        subscriber_id=subscriber.id,
        calendar_id=None,
    )

    # If it returns False it doesn't support VEVENT (aka caldav)
    # If it raises an exception there's a connection problem
    try:
        if not con.test_connection():
            raise RemoteCalendarConnectionError(reason=l10n('remote-calendar-reason-doesnt-support-caldav'))
    except RemoteCalendarAuthenticationError as ex:
        raise RemoteCalendarAuthenticationException(reason=ex.reason)
    except TestConnectionFailed as ex:
        raise RemoteCalendarConnectionError(reason=ex.reason)

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

        external_connection = repo.external_connection.create(db, external_connection_schema)
    else:
        external_connection = repo.external_connection.update_token(
            db, connection.password, subscriber.id, models.ExternalConnectionType.caldav, caldav_id
        )

    con.sync_calendars(external_connection_id=external_connection.id)
    return True


@router.post('/', response_model=schemas.CalendarOut)
def create_my_calendar(
    calendar: schemas.CalendarConnection,
    db: Session = Depends(get_db),
    subscriber: models.Subscriber = Depends(get_subscriber),
):
    """endpoint to add a new CalDav calendar for authenticated subscriber"""

    # Test the connection first
    con = CalDavConnector(
        db=db,
        redis_instance=None,
        url=calendar.url,
        user=calendar.user,
        password=calendar.password,
        subscriber_id=subscriber.id,
        calendar_id=None,
    )

    # Make sure we can connect to the calendar before we save it
    if not con.test_connection():
        raise RemoteCalendarConnectionError()

    # create calendar
    try:
        cal = repo.calendar.create(db=db, calendar=calendar, subscriber_id=subscriber.id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color, connected=cal.connected)


@router.post('/disconnect')
def disconnect_account(
    type_id: Optional[str] = None,
    db: Session = Depends(get_db),
    subscriber: models.Subscriber = Depends(get_subscriber),
):
    """Disconnects a caldav account. Removes associated data from our services and deletes the connection details."""
    ec = utils.list_first(
        repo.external_connection.get_by_type(
            db, subscriber_id=subscriber.id, type=models.ExternalConnectionType.caldav, type_id=type_id
        )
    )

    if ec is None:
        raise RemoteCalendarConnectionError()

    # Check if any schedule uses a calendar from this connection as its default
    # If so, prevent disconnection to avoid breaking the user's booking setup
    schedules = repo.schedule.get_by_subscriber(db, subscriber.id)
    for schedule in schedules:
        if schedule.calendar and schedule.calendar.external_connection_id == ec.id:
            raise ConnectionContainsDefaultCalendarException()

    # Deserialize the url/user
    _, user = json.loads(ec.type_id)

    # Remove all the caldav calendars associated with this user
    repo.calendar.delete_by_subscriber_and_provider(
        db, subscriber.id, provider=models.CalendarProvider.caldav, user=user
    )

    # Remove their account details
    repo.external_connection.delete_by_type(db, subscriber.id, ec.type, ec.type_id)

    return True
