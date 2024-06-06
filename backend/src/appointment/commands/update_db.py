import os

from ..database import models
from alembic.runtime import migration

from ..dependencies.database import get_engine_and_session


def run():
    print("Checking if we have a fresh database...")

    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    from alembic import command
    from alembic.config import Config

    # TODO: Does this work on stage?
    alembic_cfg = Config("./alembic.ini")

    # If we have our database url env variable set, use that instead!
    if os.getenv("DATABASE_URL"):
        alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

    engine, _ = get_engine_and_session()

    with engine.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        # Returns a tuple, empty if there's no revisions saved
        revisions = context.get_current_heads()

        # If we have no revisions, then fully create the database from the model metadata,
        # and set our revision number to the latest revision. Otherwise run any new migrations
        if len(revisions) == 0:
            print("Initializing database, and setting it to the latest revision")
            models.Base.metadata.create_all(bind=engine)
            command.stamp(alembic_cfg, "head")
        else:
            print("Database already initialized, running migrations")
            command.upgrade(alembic_cfg, "head")
