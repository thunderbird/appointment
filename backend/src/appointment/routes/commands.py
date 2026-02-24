"""This file handles routing for console commands"""

from contextlib import contextmanager
import os

import typer
from ..commands import update_db, download_legal, setup, generate_documentation_pages, renew_google_channels, backfill_google_channels

router = typer.Typer()


@contextmanager
def cron_lock(lock_name):
    """Context manager helper to create a cron lockfile or error out with FileExistsError."""
    lock_file_name = f'/tmp/{lock_name}.lock'

    # Lock file exists? Don't run
    if os.path.isfile(lock_file_name):
        raise FileExistsError

    fh = open(lock_file_name, 'w+')
    try:
        yield
    finally:
        fh.close()
        os.remove(lock_file_name)


@router.command('update-db')
def update_database():
    update_db.run()


@router.command('download-legal')
def download_legal_docs():
    download_legal.run()


@router.command('generate-docs')
def generate_docs():
    generate_documentation_pages.run()


@router.command('setup')
def setup_app():
    setup.run()


@router.command('renew-google-channels')
def renew_channels():
    try:
        with cron_lock('renew_google_channels'):
            renew_google_channels.run()
    except FileExistsError:
        print('renew-google-channels is already running, skipping.')


@router.command('backfill-google-channels')
def backfill_channels():
    try:
        with cron_lock('backfill_google_channels'):
            backfill_google_channels.run()
    except FileExistsError:
        print('backfill-google-channels is already running, skipping.')
