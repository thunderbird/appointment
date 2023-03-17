"""Module: auth

Handle authentification with Auth0 and get subscription data.
"""
from sqlalchemy.orm import Session
from ..database import repo, schemas, models
from fastapi import Security
from fastapi_auth0 import Auth0, Auth0User
from auth0.authentication import GetToken
from auth0.management import Auth0 as ManageAuth0
from ..config import config

domain = config('AUTH0_API_DOMAIN')
api_client_id = config('AUTH0_API_CLIENT_ID')
api_secret = config('AUTH0_API_SECRET')
api_audience = config('AUTH0_API_AUDIENCE')


class Auth:
  def __init__(self):
    """verify Appointment subscription via Auth0, return user or None"""
    scopes = {'read:calendars': 'Read Calendar Ressources'} # TODO
    self.auth0 = Auth0(domain=domain, api_audience=api_audience, scopes=scopes)
    self.subscriber = None

  def persist_user(self, db: Session, user: Auth0User):
    """Sync authed user to Appointment db"""
    # get the current user via the authed user
    api = self.init_management_api()
    authenticated_subscriber = api.users.get(user.id)
    # check if user exists as subsriber
    if db and authenticated_subscriber:
      # search for subscriber in Appointment db
      db_subscriber = repo.get_subscriber_by_email(db=db, email=authenticated_subscriber['email'])
      # if authenticated subscriber doesn't exist yet, add them
      if db_subscriber is None:
        subscriber = schemas.SubscriberBase(
          username = "", # TODO
          email = authenticated_subscriber['email'],
          name = authenticated_subscriber['name'],
          level = models.SubscriberLevel.pro, # TODO
        )
        db_subscriber = repo.create_subscriber(db=db, subscriber=subscriber)
      self.subscriber = db_subscriber#
    return self.subscriber

  def init_management_api(self):
    """Helper function to get a management api token"""
    get_token = GetToken(domain, api_client_id, client_secret=api_secret)
    token = get_token.client_credentials('https://{}/api/v2/'.format(domain))
    return ManageAuth0(domain, token['access_token'])
