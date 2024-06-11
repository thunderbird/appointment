import json
import os

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..controller.apis.zoom_client import ZoomClient
from ..controller.auth import sign_url
from ..database import repo, schemas, models
from ..database.models import Subscriber, ExternalConnectionType
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db
from ..dependencies.zoom import get_zoom_client
from ..l10n import l10n

router = APIRouter()


@router.get('/auth')
def zoom_auth(
    request: Request,
    subscriber: Subscriber = Depends(get_subscriber),
    zoom_client: ZoomClient = Depends(get_zoom_client),
):
    """Starts the zoom oauth process"""

    url, state = zoom_client.get_redirect_url(state=sign_url(str(subscriber.id)))

    # We'll need to store this in session
    request.session['zoom_state'] = state
    request.session['zoom_user_id'] = subscriber.id

    return {'url': url}


@router.get('/callback')
def zoom_callback(
    request: Request,
    code: str,
    state: str,
    db=Depends(get_db),
):
    if 'zoom_state' not in request.session or request.session['zoom_state'] != state:
        raise HTTPException(400, l10n('oauth-error'))
    if 'zoom_user_id' not in request.session or 'zoom_user_id' == '':
        raise HTTPException(400, l10n('oauth-error'))

    # Retrieve the user id set at the start of the zoom oauth process
    subscriber = repo.subscriber.get(db, request.session['zoom_user_id'])

    # Clear zoom session keys
    request.session.pop('zoom_state')
    request.session.pop('zoom_user_id')

    # Generate the zoom client instance based on our subscriber
    # This can't be set as a dep injection since subscriber is based on session.
    zoom_client: ZoomClient = get_zoom_client(subscriber)

    creds = zoom_client.get_credentials(code)

    # Get the zoom user info, so we can associate their id with their appointment subscriber
    zoom_user_info = zoom_client.get_me()

    external_connection_schema = schemas.ExternalConnection(
        name=zoom_user_info['email'],
        type=ExternalConnectionType.zoom,
        type_id=zoom_user_info['id'],
        owner_id=subscriber.id,
        token=json.dumps(creds),
    )

    if (
        len(
            repo.external_connection.get_by_type(
                db, subscriber.id, external_connection_schema.type, external_connection_schema.type_id
            )
        )
        == 0
    ):
        repo.external_connection.create(db, external_connection_schema)

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/account")


@router.post('/disconnect')
def disconnect_account(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """We only have one zoom account, so we can just remove it. If it doesn't even exist return false."""
    zoom_connection = subscriber.get_external_connection(ExternalConnectionType.zoom)

    if zoom_connection:
        repo.external_connection.delete_by_type(db, subscriber.id, zoom_connection.type, zoom_connection.type_id)
        schedules = repo.schedule.get_by_subscriber(db, subscriber.id)
        for schedule in schedules:
            if schedule.meeting_link_provider == models.MeetingLinkProviderType.zoom:
                schedule.meeting_link_provider = models.MeetingLinkProviderType.none
                db.add(schedule)
        db.commit()
    else:
        return False

    return True
