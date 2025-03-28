import math

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


@router.post('/', response_model=schemas.InviteAdminOut)
def get_all_invites(
    data: schemas.ListResponseIn, db: Session = Depends(get_db), _admin: Subscriber = Depends(get_admin_subscriber)
):
    """List all existing invites, needs admin permissions"""
    page = data.page - 1
    per_page = data.per_page

    total_count = db.query(models.Invite).count()
    invites = db.query(models.Invite).order_by('time_created').offset(page * per_page).limit(per_page).all()

    return schemas.InviteAdminOut(
        items=invites,
        page_meta=schemas.Paginator(
            page=data.page, per_page=per_page, count=len(invites), total_pages=math.ceil(total_count / per_page)
        ),
    )


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
    # Note admin must be here for permission reasons
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

    waiting_list_entry = repo.invite.get_waiting_list_entry_by_email(db, email)
    date = waiting_list_entry.time_created if waiting_list_entry else ''

    background_tasks.add_task(send_invite_account_email, date=date, to=email, lang=subscriber.language)

    return invite_code
