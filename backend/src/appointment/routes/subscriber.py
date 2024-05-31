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
    subscriber = repo.subscriber.get_by_email(db, email)
    if not subscriber:
        raise validation.SubscriberNotFoundException()
    
    # Set active flag to false on the subscribers model.
    return repo.subscriber.disable(db, subscriber)


@router.put("/enable/{email}")
def disable_subscriber(email: str, db: Session = Depends(get_db), _: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to disable a subscriber by email, needs admin permissions"""
    subscriber = repo.subscriber.get_by_email(db, email)
    if not subscriber:
        raise validation.SubscriberNotFoundException()
    
    # Set active flag to true on the subscribers model.
    return repo.subscriber.enable(db, subscriber)
