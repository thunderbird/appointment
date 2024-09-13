from fastapi import APIRouter, Depends, BackgroundTasks

from sqlalchemy.orm import Session

from ..database import repo, schemas, models
from ..database.models import Subscriber
from ..database.schemas import SendInviteEmailIn
from ..dependencies.auth import get_admin_subscriber
from ..dependencies.database import get_db

from ..exceptions import validation
from ..exceptions.validation import CreateSubscriberFailedException, CreateSubscriberAlreadyExistsException
from ..tasks.emails import send_invite_account_email

router = APIRouter()


"""
ADMIN ROUTES
"""


@router.get('/', response_model=list[schemas.Invite])
def get_all_invites(db: Session = Depends(get_db), _admin: Subscriber = Depends(get_admin_subscriber)):
    """List all existing invites, needs admin permissions"""
    return db.query(models.Invite).all()


@router.post('/generate/{n}', response_model=list[schemas.Invite])
def generate_invite_codes(n: int, db: Session = Depends(get_db), _admin: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to generate n invite codes, needs admin permissions"""
    return repo.invite.generate_codes(db, n)


@router.put('/revoke/{code}')
def revoke_invite_code(code: str, db: Session = Depends(get_db), admin: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to revoke a given invite code and mark in unavailable, needs admin permissions"""
    if not repo.invite.code_exists(db, code):
        raise validation.InviteCodeNotFoundException()
    if not repo.invite.code_is_available(db, code):
        raise validation.InviteCodeNotAvailableException()
    return repo.invite.revoke_code(db, code)


@router.post('/send', response_model=schemas.Invite)
def send_invite_email(
    data: SendInviteEmailIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    # Note admin must be here to for permission reasons
    _admin: Subscriber = Depends(get_admin_subscriber),
):
    """With a given email address, generate a subscriber and email them, welcoming them to Thunderbird Appointment."""
    email = data.email

    lookup = repo.subscriber.get_by_email(db, email)

    if lookup:
        raise CreateSubscriberAlreadyExistsException()

    invite_code = repo.invite.generate_codes(db, 1)[0]
    subscriber = repo.subscriber.create(
        db,
        schemas.SubscriberBase(
            email=email,
            username=email,
        ),
    )

    if not subscriber:
        raise CreateSubscriberFailedException()

    invite_code.subscriber_id = subscriber.id
    db.add(invite_code)
    db.commit()

    background_tasks.add_task(send_invite_account_email, to=email)

    return invite_code
