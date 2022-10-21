"""Module: auth

Handle authentification with Firefox Sync and get subscription data.
"""
from sqlalchemy.orm import Session
from ..database import repo, schemas, models

# TODO: for now we simulate Firefox Sync with a hardcoded fake db
ff_sync_fake_users = {
  "admin@example.com": {
    "username": "admin",
    "email": "admin@example.com",
    "name": "Andy Admin",
    "level": models.SubscriberLevel.pro,
  }
}

class Auth:
  def __init__(self, db: Session):
    """verify Appointment subscription via Firefox Sync, return user or None"""
    self.subscriber = None
    # check if user is a subscriber
    authenticated_subscriber = self.authenticate_subscriber()
    if authenticated_subscriber:
      # search for subscriber in Appointment db
      db_subscriber = repo.get_subscriber_by_email(db=db, email=authenticated_subscriber['email'])
      # if authenticated subscriber doesn't exist yet, add them
      if db_subscriber is None:
        subscriber = schemas.SubscriberBase(**authenticated_subscriber)
        db_subscriber = repo.create_subscriber(db=db, subscriber=subscriber)
      self.subscriber = db_subscriber

  def authenticate_subscriber(self):
    """do actual authentication"""
    # TODO: check existing user session
    # TODO: if session, reset session expiration and continue with it
    # TODO: if no session: authenticate with Firefox Sync via Oauth2
    # TODO: and start new user session
    email = "admin@example.com" # TODO: for dev purposes
    user = self.get_subscriber(ff_sync_fake_users, email)
    if not user:
      return False
    return user

  def get_subscriber(self, db, email: str):
    if email in db:
      return db[email]
