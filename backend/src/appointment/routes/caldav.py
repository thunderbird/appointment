import json
from urllib.parse import urlparse

import requests

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from appointment import utils
from appointment.controller.apis.google_client import GoogleClient
from appointment.controller.calendar import CalDavConnector, Tools, GoogleConnector
from appointment.database import models, schemas, repo
from appointment.dependencies.auth import get_subscriber
from appointment.dependencies.database import get_db
from appointment.dependencies.google import get_google_client
from appointment.exceptions.validation import RemoteCalendarConnectionError

router = APIRouter()


@router.post('/auth')
def caldav_autodiscover_auth(
    connection: schemas.CalendarConnection,
    db: Session = Depends(get_db),
    subscriber: models.Subscriber = Depends(get_subscriber),
):
    """Connects a principal caldav server"""

    # Do a dns lookup first
    parsed_url = urlparse(connection.url)
    lookup_url = Tools.dns_caldav_lookup(parsed_url.hostname)
    if lookup_url:
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


@router.get('/dns')
def dns_lookup(subscriber: models.Subscriber = Depends(get_subscriber)):
    """Dns lookup for caldav information based on the subscriber's preferred email"""
    caldav_url = Tools.dns_caldav_lookup(subscriber.preferred_email.split('@')[1])
    caldav_url = Tools.fix_caldav_urls(caldav_url)

    return {
        'url': caldav_url
    }
