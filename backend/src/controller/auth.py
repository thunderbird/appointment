"""Module: auth

Handle authentification with Auth0 and get subscription data.
"""
import json
import os

from sqlalchemy.orm import Session
from ..database import repo, schemas, models
from fastapi import Security
from fastapi_auth0 import Auth0, Auth0User
from auth0.authentication import GetToken
from auth0.management import Auth0 as ManageAuth0
from auth0.exceptions import Auth0Error, RateLimitError, TokenValidationError
import logging

# Get the secrets from aws, and decode the json
auth0_secrets = os.getenv('AUTH0_SECRETS')
if auth0_secrets:
  auth0_secrets = json.loads(auth0_secrets)
else:
  auth0_secrets = {}

domain = auth0_secrets.get('domain') or os.getenv('AUTH0_API_DOMAIN')
api_client_id = auth0_secrets.get('client_id') or os.getenv('AUTH0_API_CLIENT_ID')
api_secret = auth0_secrets.get('secret') or os.getenv('AUTH0_API_SECRET')
api_audience = auth0_secrets.get('audience') or os.getenv('AUTH0_API_AUDIENCE')


class Auth:
  def __init__(self):
    """verify Appointment subscription via Auth0, return user or None"""
    scopes = {'read:calendars': 'Read Calendar Ressources'} # TODO
    self.auth0 = Auth0(domain=domain, api_audience=api_audience, scopes=scopes)
    self.subscriber = None

  def persist_user(self, db: Session, user: Auth0User):
    """Sync authed user to Appointment db"""
    if not db:
      return None
    # get the current user via the authed user
    api = self.init_management_api()
    if not api:
      return None
    authenticated_subscriber = api.users.get(user.id)
    # check if user exists as subsriber
    if authenticated_subscriber:
      # search for subscriber in Appointment db
      db_subscriber = repo.get_subscriber_by_email(db=db, email=authenticated_subscriber['email'])
      # if authenticated subscriber doesn't exist yet, add them
      if db_subscriber is None:
        subscriber = schemas.SubscriberBase(
          username = authenticated_subscriber['email'], # username == email for now
          email = authenticated_subscriber['email'],
          name = authenticated_subscriber['name'],
          level = models.SubscriberLevel.pro, # TODO
        )
        db_subscriber = repo.create_subscriber(db=db, subscriber=subscriber)
      self.subscriber = db_subscriber
    return self.subscriber

  def init_management_api(self):
    """Helper function to get a management api token"""
    try:
      get_token = GetToken(domain, api_client_id, client_secret=api_secret)
      token = get_token.client_credentials('https://{}/api/v2/'.format(domain))
      management = ManageAuth0(domain, token['access_token'])
    except Auth0Error as error:
      logging.error(error)
      return None
    except RateLimitError as error:
      logging.error(error)
      return None
    except TokenValidationError as error:
      logging.error(error)
      return None

    return management
