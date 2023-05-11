"""Module: auth

Handle authentification with Auth0 and get subscription data.
"""
import logging
import os

from sqlalchemy.orm import Session
from ..database import repo, schemas, models
from fastapi_auth0 import Auth0, Auth0User
from auth0.authentication import GetToken
from auth0.management import Auth0 as ManageAuth0
from auth0.exceptions import Auth0Error, RateLimitError, TokenValidationError


domain = os.getenv("AUTH0_API_DOMAIN")
api_client_id = os.getenv("AUTH0_API_CLIENT_ID")
api_secret = os.getenv("AUTH0_API_SECRET")
api_audience = os.getenv("AUTH0_API_AUDIENCE")


class Auth:
    def __init__(self):
        """verify Appointment subscription via Auth0, return user or None"""
        scopes = {"read:calendars": "Read Calendar Ressources"}  # TODO
        self.auth0 = Auth0(domain=domain, api_audience=api_audience, scopes=scopes)

    def persist_user(self, db: Session, user: Auth0User):
        """Sync authed user to Appointment db"""
        if not db:
            return None
        # get the current user via the authed user
        api = self.init_management_api()
        if not api:
            logging.warning(
                "[auth.persist_user] A frontend authed user (ID: %s, name: %s) was not found via management API",
                str(user.id),
                user.name,
            )
            return None
        authenticated_subscriber = api.users.get(user.id)
        # check if user exists as subsriber
        if authenticated_subscriber:
            # search for subscriber in Appointment db
            db_subscriber = repo.get_subscriber_by_email(db=db, email=authenticated_subscriber["email"])
            # if authenticated subscriber doesn't exist yet, add them
            if db_subscriber is None:
                subscriber = schemas.SubscriberBase(
                    username=authenticated_subscriber["email"],  # username == email for now
                    email=authenticated_subscriber["email"],
                    name=authenticated_subscriber["name"],
                    level=models.SubscriberLevel.pro,  # TODO
                )
                db_subscriber = repo.create_subscriber(db=db, subscriber=subscriber)
            return db_subscriber
        return None

    def init_management_api(self):
        """Helper function to get a management api token"""
        try:
            get_token = GetToken(domain, api_client_id, client_secret=api_secret)
            token = get_token.client_credentials("https://{}/api/v2/".format(domain))
            management = ManageAuth0(domain, token["access_token"])
        except Auth0Error as error:
            logging.error("[auth.init_management_api] An Auth0 error occured: " + str(error))
            return None
        except RateLimitError as error:
            logging.error("[auth.init_management_api] A rate limit error occured: " + str(error))
            return None
        except TokenValidationError as error:
            logging.error("[auth.init_management_api] A token validation error occured" + str(error))
            return None

        return management
