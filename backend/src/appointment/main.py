"""Module: main

Boot application, init database, authenticate user and provide all API endpoints.

"""

from contextlib import asynccontextmanager
from urllib.parse import urlparse

from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.middleware.sessions import SessionMiddleware
from starlette_context.middleware import RawContextMiddleware
from fastapi import Request
from starlette_csrf import CSRFMiddleware

from .defines import APP_ENV_DEV, APP_ENV_TEST, APP_ENV_STAGE, APP_ENV_PROD, AuthScheme
from .exceptions.validation import APIRateLimitExceeded
from .dependencies.database import boot_redis_cluster, close_redis_cluster
from .middleware.l10n import L10n
from .middleware.SanitizeMiddleware import SanitizeMiddleware

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

from slowapi.errors import RateLimitExceeded


import sentry_sdk

from .utils import normalize_secrets


def _common_setup():
    # load any available .env into env
    if os.getenv('APP_ENV') != APP_ENV_TEST:
        load_dotenv()

    # This needs to be ran before any other imports
    normalize_secrets()

    # init logging
    level = os.getenv('LOG_LEVEL', 'ERROR')
    use_log_stream = os.getenv('LOG_USE_STREAM', False)

    log_config = {
        'format': '%(asctime)s %(levelname)-8s %(message)s',
        'level': getattr(logging, level),
        'datefmt': '%Y-%m-%d %H:%M:%S',
    }
    if use_log_stream:
        log_config['stream'] = sys.stdout
    else:
        log_config['filename'] = 'appointment.log'

    logging.basicConfig(**log_config)

    # Adjust caldav
    caldav_logger = logging.getLogger('caldav')
    caldav_logger.setLevel(logging.CRITICAL)

    logging.debug('Logger started!')

    if os.getenv('SENTRY_DSN') != '' and os.getenv('SENTRY_DSN') is not None:
        release_string = None
        release_version = os.getenv('RELEASE_VERSION')
        if release_version:
            release_string = f'appointment-backend@{release_version}'

        sample_rate = 0
        profile_traces_max = 0
        environment = os.getenv('APP_ENV', APP_ENV_STAGE)

        if environment == APP_ENV_STAGE:
            profile_traces_max = 0.25
            sample_rate = 1.0
        elif environment == APP_ENV_PROD:
            profile_traces_max = 0.66
            sample_rate = 1.0

        def traces_sampler(sampling_context):
            """Tell Sentry to ignore or reduce traces for particular routes"""
            asgi_scope = sampling_context.get('asgi_scope', {})
            path = asgi_scope.get('path')

            # Ignore health check and favicon.ico
            if path == '/' or path == '/favicon.ico':
                return 0

            return profile_traces_max

        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            sample_rate=sample_rate,
            environment=environment,
            release=release_string,
            integrations=[
                StarletteIntegration(transaction_style='endpoint'),
                FastApiIntegration(transaction_style='endpoint'),
            ],
            profiles_sampler=traces_sampler,
            traces_sampler=traces_sampler,
            attach_stacktrace=True,
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
    from .routes import caldav
    from .routes import google
    from .routes import schedule
    from .routes import invite
    from .routes import metrics
    from .routes import subscriber
    from .routes import zoom
    from .routes import waiting_list
    from .routes import webhooks

    # Hide openapi url (which will also hide docs/redoc) if we're not dev
    openapi_url = '/openapi.json' if os.getenv('APP_ENV') == APP_ENV_DEV else None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Boot the redis cluster as the app starts up
        boot_redis_cluster()
        yield
        close_redis_cluster()

    # init app
    app = FastAPI(openapi_url=openapi_url, lifespan=lifespan)

    @app.middleware('http')
    async def apply_x_forwarded_headers_to_client(request: Request, call_next):
        """Apply the x-forwarded-for to the client host if available"""
        ip_list = request.headers.get('x-forwarded-for')
        port = request.headers.get('x-forwarded-port')

        # Grab the client scope and turn it into a list
        client = list(request.scope.get('client'))

        # Apply our client and port if available
        if client is not None:
            if ip_list:
                client_ip = ip_list.split(',')
                client[0] = client_ip[0]
            if port:
                client[1] = int(port)

            # Transform it back into a tuple and update the request
            request.scope.update({'client': tuple(client)})

        response = await call_next(request)
        return response

    app.add_middleware(RawContextMiddleware, plugins=(L10n(),))

    # strip html tags from input requests
    app.add_middleware(SanitizeMiddleware)

    app.add_middleware(SessionMiddleware, secret_key=os.getenv('SESSION_SECRET'))

    # This needs to be below SessionMiddleware
    if AuthScheme.is_accounts():
        cookie_secure = True if os.getenv('FRONTEND_URL', '').startswith('https://') else False
        cookie_domain = None
        frontend_url = os.getenv('FRONTEND_URL', None)
        if frontend_url:
            frontend_url = urlparse(frontend_url)
        if frontend_url and frontend_url.hostname and frontend_url.hostname != '':
            cookie_domain = frontend_url.hostname

        app.add_middleware(
            CSRFMiddleware,
            secret=os.getenv('CSRF_SECRET'),
            cookie_domain=cookie_domain,
            cookie_secure=cookie_secure,
            header_name='X-CSRFToken',
        )

    # allow requests from own frontend running on a different port
    app.add_middleware(
        CORSMiddleware,
        # Work around for now :)
        allow_origins=[
            os.getenv('FRONTEND_URL', 'http://localhost:8080'),
            'https://stage.appointment.day',  # Temp for now!
            'https://accounts.google.com',
            'https://www.googleapis.com/auth/calendar',
        ],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    @app.middleware('http')
    async def warn_about_deprecated_routes(request: Request, call_next):
        """Warn about clients using deprecated routes"""
        response = await call_next(request)
        if request.scope.get('route') and request.scope['route'].deprecated:
            app_env = os.getenv('APP_ENV')
            if app_env == APP_ENV_DEV:
                logging.warning(f"Use of deprecated route: `{request.scope['route'].path}`!")
            elif app_env == APP_ENV_TEST:
                # Stale test runtime error
                raise RuntimeError(f"Test uses deprecated route: `{request.scope['route'].path}`!")
        return response

    @app.exception_handler(DefaultCredentialsError)
    @app.exception_handler(RefreshError)
    async def catch_google_refresh_errors(request, exc):
        """Catch google refresh errors, and use our error instead."""
        return await http_exception_handler(request, APIGoogleRefreshError())

    @app.exception_handler(RateLimitExceeded)
    async def catch_rate_limit_exceeded_errors(request, exc):
        return await http_exception_handler(request, APIRateLimitExceeded())

    # Mix in our extra routes
    app.include_router(api.router)
    app.include_router(auth.router)  # Special case!
    app.include_router(account.router, prefix='/account')
    app.include_router(caldav.router, prefix='/caldav')
    app.include_router(google.router, prefix='/google')
    app.include_router(schedule.router, prefix='/schedule')
    app.include_router(invite.router, prefix='/invite')
    app.include_router(metrics.router, prefix='/metrics')
    app.include_router(subscriber.router, prefix='/subscriber')
    app.include_router(waiting_list.router, prefix='/waiting-list')
    app.include_router(webhooks.router, prefix='/webhooks')
    if os.getenv('ZOOM_API_ENABLED'):
        app.include_router(zoom.router, prefix='/zoom')

    return app


def cli():
    """
    Entrypoint for our typer cli
    """

    # Run common setup first
    _common_setup()

    from .routes import commands

    app = typer.Typer(pretty_exceptions_enable=False)
    # We don't have too many commands, so just dump them under main for now.
    app.add_typer(commands.router, name='main')
    app()
