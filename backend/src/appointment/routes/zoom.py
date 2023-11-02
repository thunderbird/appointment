import json
import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from ..controller.apis.zoom_client import ZoomClient
from ..database import repo, schemas
from ..database.models import Subscriber, ExternalConnectionType
from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db
from ..dependencies.zoom import get_zoom_client

router = APIRouter()


@router.get("/auth")
def zoom_auth(
    request: Request,
    zoom_client: ZoomClient = Depends(get_zoom_client),
):
    """Starts the zoom oauth process"""

    url, state = zoom_client.get_redirect_url()

    request.session['state'] = state

    return url


@router.get("/callback")
def zoom_callback(
    request: Request,
    code: str,
    state: str,
    zoom_client: ZoomClient = Depends(get_zoom_client),
    subscriber: Subscriber = Depends(get_subscriber),
    db=Depends(get_db),
):
    print(request.session)
    if request.session.get('state', None) != state:
        raise RuntimeError("States do not match!")

    request.session['state'] = None

    creds = zoom_client.get_credentials(code)

    # Get the zoom user info, so we can associate their id with their appointment subscriber
    zoom_user_info = zoom_client.get_me()

    external_connection_schema = schemas.ExternalConnection(
        type=ExternalConnectionType.Zoom,
        type_id=zoom_user_info['id'],
        owner_id=subscriber.id,
        token=json.dumps(creds)
    )

    if repo.get_external_connection_by_type(db, subscriber.id, external_connection_schema.type, external_connection_schema.type_id) is None:
        repo.create_subscriber_external_connection(db, external_connection_schema)

    #return zoom_user_info
    return RedirectResponse(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/settings/account")
