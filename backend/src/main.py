"""Module: main

Boot application, init database, authenticate user and provide all API endpoints.
"""
# Ignore "Module level import not at top of file"
# ruff: noqa: E402
from .secrets import normalize_secrets

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

# database
from .database import models
from .database.database import engine

models.Base.metadata.create_all(bind=engine)

# extra routes
from .routes import google
from .routes import api

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

# Mix in our extra routes
app.include_router(api.router)
app.include_router(google.router, prefix="/google")
