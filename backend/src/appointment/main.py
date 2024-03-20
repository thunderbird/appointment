"""Module: main

Boot application, init database, authenticate user and provide all API endpoints.
"""
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.middleware.sessions import SessionMiddleware
from starlette_context.middleware import RawContextMiddleware
from fastapi import Request

from .defines import APP_ENV_DEV, APP_ENV_TEST
from .middleware.l10n import L10n
# Ignore "Module level import not at top of file"
# ruff: noqa: E402
from .secrets import normalize_secrets

from google.auth.exceptions import RefreshError, DefaultCredentialsError
from .exceptions.google_api import APIGoogleRefreshError
import os

from dotenv import load_dotenv

import logging
import sys

import typer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import (
    http_exception_handler,
)

import sentry_sdk


def _common_setup():
    # load any available .env into env
    load_dotenv()

    # This needs to be ran before any other imports
    normalize_secrets()

    # init logging
    level = os.getenv("LOG_LEVEL", "ERROR")
    use_log_stream = os.getenv("LOG_USE_STREAM", False)

    log_config = {
        "format": "%(asctime)s %(levelname)-8s %(message)s",
        "level": getattr(logging, level),
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
    if use_log_stream:
        log_config["stream"] = sys.stdout
    else:
        log_config["filename"] = "appointment.log"

    logging.basicConfig(**log_config)

    logging.debug("Logger started!")

    if os.getenv("SENTRY_DSN") != "" and os.getenv("SENTRY_DSN") is not None:

        release_string = None
        release_version = os.getenv('RELEASE_VERSION')
        if release_version:
            release_string = f"appointment-backend@{release_version}"

        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=1.0,
            # Only profile staging for now
            profiles_sample_rate=1.0 if os.getenv("APP_ENV", "stage") else 0.0,
            send_default_pii=True if os.getenv("APP_ENV", "stage") else False,
            environment=os.getenv("APP_ENV", "dev"),
            release=release_string,
            integrations=[
                StarletteIntegration(
                    transaction_style="endpoint"
                ),
                FastApiIntegration(
                    transaction_style="endpoint"
                ),
            ],
        )


def server():
    """
    Main function for the fast api server
    """

    # Run common setup first
    _common_setup()

    # extra routes
    from .routes import api
    from .routes import auth
    from .routes import account
    from .routes import google
    from .routes import schedule
    from .routes import zoom
    from .routes import webhooks

    # Hide openapi url (which will also hide docs/redoc) if we're not dev
    openapi_url = '/openapi.json' if os.getenv('APP_ENV') == 'dev' else None

    # init app
    app = FastAPI(openapi_url=openapi_url)

    app.add_middleware(
        RawContextMiddleware,
        plugins=(
            L10n(),
        )
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET")
    )

    # allow requests from own frontend running on a different port
    app.add_middleware(
        CORSMiddleware,
        # Work around for now :)
        allow_origins=[
            os.getenv("FRONTEND_URL", "http://localhost:8080"),
            "https://stage.appointment.day",  # Temp for now!
            "https://accounts.google.com",
            "https://www.googleapis.com/auth/calendar",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def warn_about_deprecated_routes(request: Request, call_next):
        """Warn about clients using deprecated routes"""
        response = await call_next(request)
        if request.scope.get('route') and request.scope['route'].deprecated:
            app_env = os.getenv('APP_ENV')
            if app_env == APP_ENV_DEV:
                logging.warning(f"Use of deprecated route: `{request.scope['route'].path}`!")
            elif app_env == APP_ENV_TEST:
                # Stale test runtime error
                #raise RuntimeError(f"Test uses deprecated route: `{request.scope['route'].path}`!")
                # Just log for this PR, we'll fix it another PR.
                logging.error(f"Test uses deprecated route: `{request.scope['route'].path}`!")
        return response

    @app.exception_handler(DefaultCredentialsError)
    @app.exception_handler(RefreshError)
    async def catch_google_refresh_errors(request, exc):
        """Catch google refresh errors, and use our error instead."""
        return await http_exception_handler(request, APIGoogleRefreshError())


    # Mix in our extra routes
    app.include_router(api.router)
    app.include_router(auth.router)  # Special case!
    app.include_router(account.router, prefix="/account")
    app.include_router(google.router, prefix="/google")
    app.include_router(schedule.router, prefix="/schedule")
    app.include_router(webhooks.router, prefix="/webhooks")
    if os.getenv("ZOOM_API_ENABLED"):
        app.include_router(zoom.router, prefix="/zoom")

    return app


def cli():
    """
    Entrypoint for our typer cli
    """

    # Run common setup first
    _common_setup()

    from .routes import commands

    app = typer.Typer()
    # We don't have too many commands, so just dump them under main for now.
    app.add_typer(commands.router, name="main")
    app()
