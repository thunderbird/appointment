import os
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException

from ..controller import data
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber, ExternalConnectionType
from ..database import schemas

from fastapi.responses import StreamingResponse

from ..exceptions.account_api import AccountDeletionException

router = APIRouter()


@router.get("/external-connections")
def get_external_connections(subscriber: Subscriber = Depends(get_subscriber)):
    # This could be moved to a helper function in the future
    # Create a list of supported external connections
    external_connections = defaultdict(list)

    if os.getenv('ZOOM_API_ENABLED'):
        external_connections['Zoom'] = []

    for ec in subscriber.external_connections:
        external_connections[ec.type.name].append(schemas.ExternalConnectionOut(owner_id=ec.owner_id, type=ec.type.name,
                                                                            type_id=ec.type_id, name=ec.name))

    return external_connections

@router.get("/download")
def download_data(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Download your account data in zip format! Returns a streaming response with the zip buffer."""
    zip_buffer = data.download(db, subscriber)
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=data.zip"},
    )


@router.delete("/delete")
def delete_account(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Delete your account and all the data associated with it forever!"""
    try:
        return data.delete_account(db, subscriber)
    except AccountDeletionException as e:
        raise HTTPException(status_code=500, detail=e.message)
