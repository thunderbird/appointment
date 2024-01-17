"""Module: main

Boot application, init database, authenticate user and provide all API endpoints.
"""
from starlette.middleware.sessions import SessionMiddleware
from starlette_context.middleware import RawContextMiddleware

from .l10n import l10n
from .middleware.l10n import L10n
# Ignore "Module level import not at top of file"
# ruff: noqa: E402
from .secrets import normalize_secrets

from google.auth.exceptions import RefreshError
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
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=1.0,
            environment=os.getenv("APP_ENV", "dev"),
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

    @app.exception_handler(RefreshError)
    async def catch_google_refresh_errors(request, exc):
        """Catch google refresh errors, and use our error instead."""
        return await http_exception_handler(request, APIGoogleRefreshError(message=l10n('google-connection-error')))

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

    from .routes import console

    app = typer.Typer()
    app.add_typer(console.router, name="main")
    app()
