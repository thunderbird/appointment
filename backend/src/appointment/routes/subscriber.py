import math

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session, joinedload

from ..database import repo, schemas, models
from ..database.models import Subscriber
from ..dependencies.auth import get_admin_subscriber, get_subscriber
from ..dependencies.database import get_db

from ..exceptions import validation

router = APIRouter()

""" ADMIN ROUTES 
These require get_admin_subscriber!
"""


@router.post('/', response_model=schemas.SubscriberAdminOut)
def get_all_subscriber(
    data: schemas.ListResponseIn, db: Session = Depends(get_db), _: Subscriber = Depends(get_admin_subscriber)
):
    """List all existing invites, needs admin permissions"""
    page = data.page - 1
    per_page = data.per_page

    total_count = db.query(models.Subscriber).count()
    subscribers = (
        db.query(models.Subscriber)
        .options(joinedload(models.Subscriber.invite))
        .order_by('time_created')
        .offset(page * per_page)
        .limit(per_page)
        .all()
    )

    return schemas.SubscriberAdminOut(
        items=subscribers,
        page_meta=schemas.Paginator(
            page=data.page,
            per_page=per_page,
            count=len(subscribers),
            total_pages=math.ceil(total_count / per_page)
        ),
    )


@router.put('/disable/{id}')
def disable_subscriber(
    id: str, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_admin_subscriber)
):
    """endpoint to mark a subscriber deleted by id, needs admin permissions"""
    subscriber_to_delete = repo.subscriber.get(db, int(id))
    if not subscriber_to_delete:
        raise validation.SubscriberNotFoundException()
    if subscriber_to_delete.is_deleted:
        raise validation.SubscriberAlreadyDeletedException()
    if subscriber.email == subscriber_to_delete.email:
        raise validation.SubscriberSelfDeleteException()

    # Set active flag to false on the subscribers model.
    return repo.subscriber.disable(db, subscriber_to_delete)


@router.put('/enable/{id}')
def enable_subscriber(id: str, db: Session = Depends(get_db), _: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to enable a subscriber by id, needs admin permissions"""
    subscriber_to_enable = repo.subscriber.get(db, int(id))
    if not subscriber_to_enable:
        raise validation.SubscriberNotFoundException()
    if not subscriber_to_enable.is_deleted:
        raise validation.SubscriberAlreadyEnabledException()

    # Set active flag to true on the subscribers model.
    return repo.subscriber.enable(db, subscriber_to_enable)


@router.put('/hard-delete/{id}')
def hard_delete_subscriber(
    id: str, db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_admin_subscriber)
):
    """endpoint to hard-delete a subscriber by email, needs admin permissions"""
    subscriber_to_delete = repo.subscriber.get(db, int(id))
    if not subscriber_to_delete:
        raise validation.SubscriberNotFoundException()
    if not subscriber_to_delete.is_deleted:
        raise validation.SubscriberNotDisabledException()
    if subscriber.email == subscriber_to_delete.email:
        raise validation.SubscriberSelfDeleteException()

    # Nuke their account
    return repo.subscriber.hard_delete(db, subscriber_to_delete)


""" NON-ADMIN ROUTES """


@router.post('/setup')
def subscriber_is_setup(db: Session = Depends(get_db), subscriber: Subscriber = Depends(get_subscriber)):
    """Flips ftue_level to 1"""
    subscriber.ftue_level = 1
    db.add(subscriber)
    db.commit()

    return True
