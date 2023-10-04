"""Module: main

Boot application, init database, authenticate user and provide all API endpoints.
"""
# Ignore "Module level import not at top of file"
# ruff: noqa: E402
from .secrets import normalize_secrets

from google.auth.exceptions import RefreshError
from .exceptions.google_api import APIGoogleRefreshError
import os

from dotenv import load_dotenv

# load any available .env into env
load_dotenv()

# This needs to be ran before any other imports
normalize_secrets()

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import (
    http_exception_handler,
)

import sentry_sdk

# init logging
level = os.getenv("LOG_LEVEL", "ERROR")
use_log_stream = os.getenv("LOG_USE_STREAM", False)
# TODO: limit log file size
# https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler
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

if os.getenv("SENTRY_DSN") != "" or os.getenv("SENTRY_DSN") is not None:
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
    # extra routes
    from .routes import api
    from .routes import account
    from .routes import google
    from .routes import schedule

    # init app
    app = FastAPI()

    # allow requests from own frontend running on a different port
    app.add_middleware(
        CORSMiddleware,
        # Work around for now :)
        allow_origins=[
            os.getenv("FRONTEND_URL", "http://localhost:8080"),
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
        return await http_exception_handler(request, APIGoogleRefreshError())

    # Mix in our extra routes
    app.include_router(api.router)
    app.include_router(account.router, prefix="/account")
    app.include_router(google.router, prefix="/google")
    app.include_router(schedule.router, prefix="/schedule")

    return app


def cli():
    """
    A very simple cli handler
    """
    if len(sys.argv) < 2:
        print("No command specified")
        return

    command = sys.argv[1:]

    if command[0] == 'update-db':
        from .commands import update_db
        update_db.run()
