import os
from datetime import timedelta, datetime, UTC
from typing import Annotated

import argon2.exceptions
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from argon2 import PasswordHasher

from fastapi import APIRouter, Depends, HTTPException

from ..database import repo, schemas
from ..database.models import Subscriber

from ..dependencies.database import get_db
from ..dependencies.auth import get_subscriber

router = APIRouter()
ph = PasswordHasher()


def verify_password(password, hashed_password):
    ph.verify(hashed_password, password)


def get_password_hash(password):
    return ph.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('JWT_SECRET'), algorithm=os.getenv('JWT_ALGO'))
    return encoded_jwt


@router.post("/token")
def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """Retrieve an access token from a given username and password."""
    subscriber = repo.get_subscriber_by_username(db, form_data.username)
    if not subscriber or subscriber.password is None:
        raise HTTPException(status_code=403, detail="User credentials mismatch")

    # Verify the incoming password, and re-hash our password if needed
    try:
        verify_password(form_data.password, subscriber.password)
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(status_code=403, detail="User credentials mismatch")

    if ph.check_needs_rehash(subscriber.password):
        subscriber.password = get_password_hash(form_data.password)
        db.add(subscriber)
        db.commit()

    # Generate our jwt token, we only store the username on the token
    access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_IN_MINS')))
    access_token = create_access_token(
        data={"sub": subscriber.username}, expires_delta=access_token_expires
    )

    """Log a user in with the passed username and password information"""
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.SubscriberBase)
def me(
    subscriber: Subscriber = Depends(get_subscriber),
):
    """Return the currently authed user model
    """
    return schemas.SubscriberBase(
         username=subscriber.username, email=subscriber.email, name=subscriber.name, level=subscriber.level, timezone=subscriber.timezone
    )
