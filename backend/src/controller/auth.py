"""Module: auth

Handle authentification with Firefox Sync and get subscription data.
"""
from sqlalchemy.orm import Session
from ..database import repo, schemas


class Auth:
  def __init__(self, db: Session):
    self.subscriber = None
    self.verify_subscriber(db)
      
  def verify_subscriber(self, db: Session):
    """verify Appointment subscription via Firefox Sync, return user ID or None"""
    # TODO: check existing user session
    # TODO: if session, reset session expiration and continue with it
    # TODO: if no session: authenticate with Firefox Sync via Oauth2
    # TODO: and start new user session
    fsuser_id = 1 # for development purposes now
    # get subscriber
    db_subscriber = repo.get_subscriber(db=db, subscriber_id=fsuser_id)
    # if user is verified but doesn't exist yet, add them
    if db_subscriber is None:
      subscriber = schemas.SubscriberBase(username='admin', email='admin@example.com', level=2)
      db_subscriber = repo.create_subscriber(db=db, subscriber=subscriber)
    self.subscriber = db_subscriber
