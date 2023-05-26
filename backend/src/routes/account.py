from fastapi import APIRouter, Depends, HTTPException

from ..controller import data
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber

from fastapi.responses import StreamingResponse

from ..exceptions.account_api import AccountDeletionException

router = APIRouter()


@router.get("/download")
def download_data(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
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
