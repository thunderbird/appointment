
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ..database import repo, schemas, models
from ..database.models import Subscriber
from ..dependencies.auth import get_admin_subscriber
from ..dependencies.database import get_db

from ..exceptions import validation

router = APIRouter()


@router.get('/', response_model=list[schemas.Invite])
def get_all_invites(db: Session = Depends(get_db), admin: Subscriber = Depends(get_admin_subscriber)):
    """List all existing invites, needs admin permissions"""
    return db.query(models.Invite).all()


@router.post("/generate/{n}", response_model=list[schemas.Invite])
def generate_invite_codes(n: int, db: Session = Depends(get_db), admin: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to generate n invite codes, needs admin permissions"""
    return repo.invite.generate_codes(db, n)


@router.put("/redeem/{code}")
def use_invite_code(code: str, db: Session = Depends(get_db)):
    raise NotImplementedError

    """endpoint to create a new subscriber and update the corresponding invite"""
    if not repo.invite.code_exists(db, code):
        raise validation.InviteCodeNotFoundException()
    if not repo.invite.code_is_available(db, code):
        raise validation.InviteCodeNotAvailableException()
    # TODO: get email from admin panel
    email = 'placeholder@mozilla.org'
    subscriber = repo.subscriber.create(db, schemas.SubscriberBase(email=email, username=email))
    return repo.invite.use_code(db, code, subscriber.id)


@router.put("/revoke/{code}")
def revoke_invite_code(code: str, db: Session = Depends(get_db), admin: Subscriber = Depends(get_admin_subscriber)):
    """endpoint to revoke a given invite code and mark in unavailable, needs admin permissions"""
    if not repo.invite.code_exists(db, code):
        raise validation.InviteCodeNotFoundException()
    if not repo.invite.code_is_available(db, code):
        raise validation.InviteCodeNotAvailableException()
    return repo.invite.revoke_code(db, code)
