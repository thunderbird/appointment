from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from ..database import repo, schemas, models
from ..database.models import Subscriber
from ..dependencies.auth import get_admin_subscriber, get_subscriber
from ..dependencies.database import get_db

from ..exceptions import validation

router = APIRouter()

""" ADMIN ROUTES 
These require get_admin_subscriber!
"""

@router.get('/', response_model=list[schemas.SubscriberAdminOut])
def get_all_subscriber(request: Request, db: Session = Depends(get_db), _: Subscriber = Depends(get_admin_subscriber)):
    """List all existing invites, needs admin permissions"""
    response = db.query(models.Subscriber).all()
    return response


@router.put('/disable/{email}')
def disable_subscriber(
    email: str, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_admin_subscriber)
):
    """endpoint to mark a subscriber deleted by email, needs admin permissions"""
    subscriber_to_delete = repo.subscriber.get_by_email(db, email.lower())
    if not subscriber_to_delete:
        raise validation.SubscriberNotFoundException()
    if subscriber_to_delete.is_deleted:
        raise validation.SubscriberAlreadyDeletedException()
    if subscriber.email == subscriber_to_delete.email:
        raise validation.SubscriberSelfDeleteException()

    # Set active flag to false on the subscribers model.
    return repo.subscriber.disable(db, subscriber_to_delete)


@router.put('/enable/{email}')
def enable_subscriber(email: str, db: Session = Depends(get_db), _: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to enable a subscriber by email, needs admin permissions"""
    subscriber_to_enable = repo.subscriber.get_by_email(db, email.lower())
    if not subscriber_to_enable:
        raise validation.SubscriberNotFoundException()
    if not subscriber_to_enable.is_deleted:
        raise validation.SubscriberAlreadyEnabledException()

    # Set active flag to true on the subscribers model.
    return repo.subscriber.enable(db, subscriber_to_enable)


""" NON-ADMIN ROUTES """


@router.post('/setup')
def subscriber_is_setup(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Flips ftue_level to 1"""
    subscriber.ftue_level = 1
    db.add(subscriber)
    db.commit()

    return True
