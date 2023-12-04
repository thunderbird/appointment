import os
from typing import Annotated

from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from sqlalchemy.orm import Session

from ..database import repo, schemas
from ..dependencies.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_from_token(db, token: str):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('JWT_ALGO')])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(401, "Could not validate credentials")
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise HTTPException(401, "Could not validate credentials")

    return repo.get_subscriber_by_username(db, token_data.username)


def get_subscriber(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """Automatically retrieve and return the subscriber based on the authenticated Auth0 user"""

    user = get_user_from_token(db, token)

    # Error out if auth0 didn't find a user
    if user is None:
        raise HTTPException(403, detail='Missing bearer token')

    user = repo.get_subscriber_by_email(db, user.email)

    # Error out if we didn't find a user
    if user is None:
        raise HTTPException(400, detail='Unknown user')

    return user
