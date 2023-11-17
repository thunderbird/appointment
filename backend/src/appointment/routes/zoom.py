import json
import os

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..controller.apis.zoom_client import ZoomClient
from ..controller.auth import sign_url
from ..database import repo, schemas
from ..database.models import Subscriber, ExternalConnectionType
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db
from ..dependencies.zoom import get_zoom_client

router = APIRouter()


@router.get("/auth")
def zoom_auth(
    subscriber: Subscriber = Depends(get_subscriber),
    zoom_client: ZoomClient = Depends(get_zoom_client),
):
    """Starts the zoom oauth process"""

    url, state = zoom_client.get_redirect_url(state=sign_url(str(subscriber.id)))

    return {'url': url}


@router.get("/callback")
def zoom_callback(
    code: str,
    state: str,
    zoom_client: ZoomClient = Depends(get_zoom_client),
    subscriber: Subscriber = Depends(get_subscriber),
    db=Depends(get_db),
):
    if sign_url(str(subscriber.id)) != state:
        raise RuntimeError("States do not match!")

    creds = zoom_client.get_credentials(code)

    # Get the zoom user info, so we can associate their id with their appointment subscriber
    zoom_user_info = zoom_client.get_me()

    external_connection_schema = schemas.ExternalConnection(
        name=zoom_user_info['email'],
        type=ExternalConnectionType.zoom,
        type_id=zoom_user_info['id'],
        owner_id=subscriber.id,
        token=json.dumps(creds)
    )

    if len(repo.get_external_connections_by_type(db, subscriber.id, external_connection_schema.type, external_connection_schema.type_id)) == 0:
        repo.create_subscriber_external_connection(db, external_connection_schema)

    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/account")


@router.post("/disconnect")
def disconnect_account(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    """We only have one zoom account, so we can just remove it. If it doesn't even exist return false."""
    zoom_connection = subscriber.get_external_connection(ExternalConnectionType.zoom)

    if zoom_connection:
        repo.delete_external_connections_by_type_id(db, subscriber.id, zoom_connection.type, zoom_connection.type_id)
    else:
        return False

    return True
