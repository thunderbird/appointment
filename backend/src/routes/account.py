from fastapi import APIRouter, Depends

from ..controller import data
from sqlalchemy.orm import Session

from ..dependencies.auth import get_subscriber
from ..dependencies.database import get_db

from ..database.models import Subscriber

from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/download")
def download_data(
    db: Session = Depends(get_db),
    subscriber: Subscriber = Depends(get_subscriber),
):
    zip_buffer = data.download(db, subscriber)
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=data.zip"}
    )


@router.delete("/delete")
def delete_account(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    return data.delete_account(db, subscriber)
