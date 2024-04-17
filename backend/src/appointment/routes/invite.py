
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ..database import repo, schemas, models
from ..dependencies.auth import get_subscriber, get_subscriber_from_signed_url
from ..dependencies.database import get_db

from ..exceptions import validation

router = APIRouter()


@router.post("/{n}", response_model=list[schemas.Invite])
def generate_invite_codes(n: int, db: Session = Depends(get_db)):
    """endpoint to generate n invite codes"""
    return repo.generate_invite_codes(db, n)


@router.put("/redeem/{code}")
def use_invite_code(code: str, db: Session = Depends(get_db)):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not repo.invite_code_exists(db, code):
        raise validation.InviteCodeNotFoundException()
    if not repo.invite_code_is_available(db, code):
        raise validation.InviteCodeNotAvailableException()
    # TODO: get email from admin panel
    email = 'placeholder@mozilla.org'
    subscriber = repo.create_subscriber(db, schemas.SubscriberBase(email=email, username=email))
    return repo.use_invite_code(db, code, subscriber.id)


@router.put("/revoke/{code}")
def use_invite_code(code: str, db: Session = Depends(get_db)):
    """endpoint to update an existing calendar connection for authenticated subscriber"""
    if not repo.invite_code_exists(db, code):
        raise validation.InviteCodeNotFoundException()
    if not repo.invite_code_is_available(db, code):
        raise validation.InviteCodeNotAvailableException()
    return repo.revoke_invite_code(db, code)
