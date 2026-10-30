"""This file handles routing for console commands"""

from contextlib import contextmanager
import os
import tempfile

import typer
from ..commands import (
    update_db,
    download_legal,
    setup,
    generate_documentation_pages,
    renew_google_channels,
    backfill_google_channels,
)

router = typer.Typer()


@contextmanager
def cron_lock(lock_name):
    """Context manager helper to create a cron lockfile or error out with FileExistsError."""
    lock_file_name = os.path.join(tempfile.gettempdir(), f'{lock_name}.lock')

    # O_EXCL makes the existence check and creation atomic, and refuses to follow
    # a pre-planted symlink. Raises FileExistsError if the lock is already held.
    fd = os.open(lock_file_name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        yield
    finally:
        os.close(fd)
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


@router.command('refresh-zoom-tokens')
def refresh_tokens():
    from ..tasks.zoom import refresh_zoom_tokens as refresh_zoom_tokens_task

    refresh_zoom_tokens_task.delay()
    print('refresh-zoom-tokens task queued.')
