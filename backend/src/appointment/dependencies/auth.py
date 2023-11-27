import os
from typing import Annotated

from fastapi import Depends, Security, Request, HTTPException
from fastapi_auth0 import Auth0User
from sqlalchemy.orm import Session

from ..controller.auth import Auth
from ..database import repo
from ..dependencies.database import get_db


def get_subscriber(
    request: Request,
    db: Session = Depends(get_db),
    user: Auth0User = Security(Auth().auth0.get_user),
):
    """Automatically retrieve and return the subscriber based on the authenticated Auth0 user"""

    # Error out if auth0 didn't find a user
    if user is None:
        raise HTTPException(403, detail='Missing bearer token')

    user = repo.get_subscriber_by_email(db, user.email)

    # Error out if we didn't find a user
    if user is None:
        raise HTTPException(400, detail='Unknown user')

    return user
