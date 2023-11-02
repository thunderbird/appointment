from fastapi import Depends, Security, Request
from fastapi_auth0 import Auth0User
from sqlalchemy.orm import Session

from ..controller.auth import Auth
from ..database import repo
from ..dependencies.database import get_db


auth = Auth()


def get_subscriber(
    request: Request,
    db: Session = Depends(get_db),
    #_=Depends(auth.auth0.implicit_scheme),
    #user: Auth0User = Security(auth.auth0.get_user),
):
    """Automatically retrieve and return the subscriber based on the authenticated Auth0 user"""
    user = repo.get_subscriber_by_email(db, 'melissa@thunderbird.net')#user.email)
    request.session['user_id'] = user.id

    return user
