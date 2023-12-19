import os
from typing import Annotated

from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from sqlalchemy.orm import Session

from ..database import repo, schemas
from ..dependencies.database import get_db
from ..exceptions.validation import APISubscriberNotFound

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_from_token(db, token: str):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('JWT_ALGO')])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(401, "Could not validate credentials")
    except JWTError:
        raise HTTPException(401, "Could not validate credentials")

    id = sub.replace('uid-', '')
    return repo.get_subscriber(db, int(id))


def get_subscriber(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """Automatically retrieve and return the subscriber"""
    user = get_user_from_token(db, token)

    if user is None:
        raise APISubscriberNotFound()

    return user
