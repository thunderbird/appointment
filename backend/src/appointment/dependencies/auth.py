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
        sub = payload.get("sub")
        iat = payload.get("iat")
        if sub is None:
            raise HTTPException(401, "Could not validate credentials")
    except JWTError:
        raise HTTPException(401, "Could not validate credentials")

    id = sub.replace('uid-', '')
    subscriber = repo.get_subscriber(db, int(id))

    # Token has been expired by us - temp measure to avoid spinning a refresh system, or a deny list for this issue
    if subscriber.minimum_valid_iat_time and not iat:
        raise HTTPException(401, "Could not validate credentials")
    elif subscriber.minimum_valid_iat_time and subscriber.minimum_valid_iat_time.timestamp() > int(iat):
        raise HTTPException(401, "Could not validate credentials")

    return subscriber


def get_subscriber(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """Automatically retrieve and return the subscriber"""
    user = get_user_from_token(db, token)

    if user is None:
        raise HTTPException(403, detail='Missing bearer token')

    return user
