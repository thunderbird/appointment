"""Module: repo.invite

Repository providing CRUD functions for invite database models.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session
from .. import models, schemas
from ..models import InviteStatus


def get_by_subscriber(db: Session, subscriber_id: int) -> models.Invite:
    return db.query(models.Invite).filter(models.Invite.subscriber_id == subscriber_id).first()


def get_by_owner(db: Session, subscriber_id: int, status: Optional[InviteStatus] = None, only_unused: bool = False) -> list[models.Invite]:
    """Retrieve invites by the invite owner. Optionally filter by status, or unused."""
    query = db.query(models.Invite)
    filters = [models.Invite.owner_id == subscriber_id]
    if status:
        filters.append(models.Invite.status == status)
    if only_unused:
        filters.append(models.Invite.subscriber_id.is_(None))

    query = query.filter(*filters)
    return query.all()


def get_by_code(db: Session, code: str) -> models.Invite:
    """retrieve invite by code"""
    return db.query(models.Invite).filter(models.Invite.code == code).first()


def generate_codes(db: Session, n: int, owner_id: Optional[int] = None):
    """generate n invite codes and return the list of created invite objects"""
    codes = [str(uuid.uuid4()) for _ in range(n)]
    db_invites = []
    for code in codes:
        invite = schemas.Invite(code=code, owner_id=owner_id)
        db_invite = models.Invite(**invite.model_dump())
        db.add(db_invite)
        db.commit()
        db_invites.append(db_invite)
    return db_invites


def code_exists(db: Session, code: str):
    """true if invite code exists"""
    return True if get_by_code(db, code) is not None else False


def code_is_used(db: Session, code: str):
    """true if invite code is assigned to a user"""
    db_invite = get_by_code(db, code)
    return db_invite.is_used


def code_is_revoked(db: Session, code: str):
    """true if invite code is revoked"""
    db_invite = get_by_code(db, code)
    return db_invite.is_revoked


def code_is_available(db: Session, code: str):
    """true if invite code exists and can still be used"""
    db_invite = get_by_code(db, code)
    return db_invite and db_invite.is_available


def use_code(db: Session, code: str, subscriber_id: int):
    """assign given subscriber to an invite"""
    db_invite = get_by_code(db, code)
    if db_invite and db_invite.is_available:
        db_invite.subscriber_id = subscriber_id
        db.commit()
        db.refresh(db_invite)
        return True
    else:
        return False


def revoke_code(db: Session, code: str):
    """set existing invite code status to revoked"""
    db_invite = get_by_code(db, code)
    db_invite.status = models.InviteStatus.revoked
    db.commit()
    db.refresh(db_invite)
    return True


def get_waiting_list_entry_by_email(db: Session, email: str) -> models.WaitingList:
    return db.query(models.WaitingList).filter(models.WaitingList.email == email).first()


def add_to_waiting_list(db: Session, email: str):
    """Add a given email to the invite bucket"""
    # Check if they're already in the invite bucket
    bucket = get_waiting_list_entry_by_email(db, email)
    if bucket:
        # Already in waiting list
        return False

    bucket = models.WaitingList(email=email)
    db.add(bucket)
    db.commit()
    db.refresh(bucket)
    return True


def confirm_waiting_list_email(db: Session, email: str):
    """Flip the email_verified field to True"""
    bucket = get_waiting_list_entry_by_email(db, email)
    if not bucket:
        return False

    bucket.email_verified = True
    db.add(bucket)
    db.commit()
    db.refresh(bucket)
    return True


def remove_waiting_list_email(db: Session, email: str):
    """Remove an existing email from the waiting list"""
    bucket = get_waiting_list_entry_by_email(db, email)
    # Already done, lol!
    if not bucket:
        return True

    db.delete(bucket)
    db.commit()
    return True
