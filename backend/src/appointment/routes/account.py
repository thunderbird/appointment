import os
from collections import defaultdict

from appointment.defines import AuthScheme
from fastapi import APIRouter, Depends, HTTPException
from posthog import Posthog
import argon2.exceptions

from ..controller import data
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber, ExternalConnectionType
from ..database.repo.external_connection import get_by_type
from ..database import schemas

from fastapi.responses import StreamingResponse

from ..dependencies.metrics import get_posthog
from ..exceptions.account_api import AccountDeletionException

from ..l10n import l10n
from .. import utils


router = APIRouter()


@router.get('/external-connections', tags=['no-cache'])
def get_external_connections(subscriber: Subscriber = Depends(get_subscriber)):
    # This could be moved to a helper function in the future
    # Create a list of supported external connections
    external_connections = defaultdict(list)

    if os.getenv('ZOOM_API_ENABLED'):
        external_connections['zoom'] = []

    for ec in subscriber.external_connections:
        external_connections[ec.type.name].append(
            schemas.ExternalConnectionOut(
                id=ec.id, owner_id=ec.owner_id, type=ec.type.name, type_id=ec.type_id, name=ec.name
            )
        )

    return external_connections


@router.post('/download')
def download_data(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Download your account data in zip format! Returns a streaming response with the zip buffer."""
    zip_buffer = data.download(db, subscriber)
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type='application/x-zip-compressed',
        headers={'Content-Disposition': 'attachment; filename=data.zip'},
    )


@router.delete('/delete')
def delete_account(
    form_data: schemas.CheckPassword,
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
    posthog: Posthog = Depends(get_posthog),
):
    """Delete your account and all the data associated with it forever!"""
    # For the password scheme, we need to verify the password before we can delete the account.
    # TODO: For the OIDC scheme, we need a re-auth through Keycloak and change the frontend password confirmation flow
    if AuthScheme.is_password():
        try:
            utils.verify_password(form_data.password, subscriber.password)
        except argon2.exceptions.VerifyMismatchError:
            raise HTTPException(status_code=401, detail=l10n('password-mismatch'))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Do the deletion and catch any exceptions that might occur
    try:
        return data.delete_account(db, subscriber)
    except AccountDeletionException as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get('/available-emails')
def get_available_emails(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Return the list of emails they can use within Thunderbird Appointment"""
    google_connections = get_by_type(db, subscriber_id=subscriber.id, type=ExternalConnectionType.google)

    emails = {subscriber.email, *[connection.name for connection in google_connections]} - {subscriber.preferred_email}

    return [subscriber.preferred_email, *emails]
