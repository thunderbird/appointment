from fastapi import Depends, Security
from fastapi_auth0 import Auth0User
from sqlalchemy.orm import Session

from ..controller.auth import Auth
from ..database import repo
from ..database.database import SessionLocal


def get_db():
    """run database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


auth = Auth()


def get_subscriber(
    db: Session = Depends(get_db),
    _=Depends(auth.auth0.implicit_scheme),
    user: Auth0User = Security(auth.auth0.get_user),
):
    """Automatically retrieve and return the subscriber based on the authenticated Auth0 user"""
    return repo.get_subscriber_by_email(db, user.email)
