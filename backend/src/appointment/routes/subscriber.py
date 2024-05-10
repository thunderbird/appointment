import time

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ..database import repo, schemas, models
from ..database.models import Subscriber
from ..dependencies.auth import get_admin_subscriber
from ..dependencies.database import get_db

from ..exceptions import validation

router = APIRouter()


@router.get('/', response_model=list[schemas.SubscriberAdminOut])
def get_all_subscriber(db: Session = Depends(get_db), _: Subscriber = Depends(get_admin_subscriber)):
    """List all existing invites, needs admin permissions"""
    response = db.query(models.Subscriber).all()
    return response


@router.put("/disable/{email}")
def disable_subscriber(email: str, db: Session = Depends(get_db), _: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to disable a subscriber by email, needs admin permissions"""
    # TODO: Add status to subscriber, and disable it instead.
    raise NotImplementedError

    subscriber = repo.subscriber.get_by_email(db, email)
    if not subscriber:
        raise validation.SubscriberNotFoundException()
    # TODO: CAUTION! This actually deletes the subscriber. We might want to only disable them.
    # This needs an active flag on the subscribers model.
    return repo.subscriber.delete(db, subscriber)
