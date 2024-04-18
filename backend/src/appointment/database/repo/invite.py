"""Module: repo.invite

Repository providing CRUD functions for invite database models. 
"""

import uuid

from sqlalchemy.orm import Session
from .. import models, schemas


def get_by_code(db: Session, code: str):
    """retrieve invite by code"""
    return db.query(models.Invite).filter(models.Invite.code == code).first()


def generate_codes(db: Session, n: int):
    """generate n invite codes and return the list of created invite objects"""
    codes = [str(uuid.uuid4()) for _ in range(n)]
    db_invites = []
    for code in codes:
        invite = schemas.Invite(code=code)
        db_invite = models.Invite(**invite.dict())
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
