"""This file handles routing for console commands"""
from contextlib import contextmanager
import os

import typer
from ..commands import update_db, download_legal

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
