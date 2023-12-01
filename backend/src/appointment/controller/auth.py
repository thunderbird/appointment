"""Module: auth

Handle authentification with Auth0 and get subscription data.
"""
import logging
import os
import hashlib
import hmac
import secrets

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

        # Ugly hack for testing
        if os.getenv('APP_ENV') == 'test':
            from types import SimpleNamespace
            self.auth0 = SimpleNamespace(implicit_scheme=lambda x: x, get_user=lambda x: x)
            return

        self.auth0 = Auth0(domain=domain, api_audience=api_audience, scopes=scopes, auto_error=False)

    def persist_user(self, db: Session, user: Auth0User, timezone: str):
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
                    timezone=timezone,
                    level=models.SubscriberLevel.pro,  # TODO
                )
                db_subscriber = repo.create_subscriber(db=db, subscriber=subscriber)

            # Generate an initial short link hash if they don't have one already
            if db_subscriber.short_link_hash is None:
                repo.update_subscriber(
                    db,
                    schemas.SubscriberAuth(
                        email=db_subscriber.email,
                        username=db_subscriber.username,
                        short_link_hash=secrets.token_hex(32),
                    ),
                    db_subscriber.id,
                )

            return db_subscriber
        return None

    def init_management_api(self):
        """Helper function to get a management api token"""
        try:
            get_token = GetToken(domain, api_client_id, client_secret=api_secret)
            token = get_token.client_credentials("https://{}/api/v2/".format(domain))
            management = ManageAuth0(domain, token["access_token"])
        except RateLimitError as error:
            logging.error("[auth.init_management_api] A rate limit error occurred: " + str(error))
            return None
        except Auth0Error as error:
            logging.error("[auth.init_management_api] An Auth0 error occurred: " + str(error))
            return None
        except TokenValidationError as error:
            logging.error("[auth.init_management_api] A token validation error occurred" + str(error))
            return None

        return management


def sign_url(url: str):
    """helper to sign a given url"""
    secret = os.getenv("SIGNED_SECRET")

    if not secret:
        raise RuntimeError("Missing signed secret environment variable")

    key = bytes(secret, "UTF-8")
    message = f"{url}".encode()
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature


def signed_url_by_subscriber(subscriber: schemas.Subscriber):
    """helper to generated signed url for given subscriber"""
    short_url = os.getenv("SHORT_BASE_URL")
    base_url = f"{os.getenv('FRONTEND_URL')}/user"

    # If we don't have a short url, then use the default url with /user added to it
    if not short_url:
        short_url = base_url

    # We sign with a different hash that the end-user doesn't have access to
    # We also need to use the default url, as short urls are currently setup as a redirect
    url = f"{base_url}/{subscriber.username}/{subscriber.short_link_hash}"

    signature = sign_url(url)

    # We return with the signed url signature
    return f"{short_url}/{subscriber.username}/{signature}"
