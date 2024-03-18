import os

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_engine_and_session():
    database_url = os.getenv("DATABASE_URL")
    connect_args = {}

    if "sqlite://" in database_url:
        connect_args = {"check_same_thread": False}

    engine = create_engine(database_url, connect_args=connect_args)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, session_local


def get_db():
    """run database session"""
    _, session = get_engine_and_session()

    db = session()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> Redis | None:
    """Retrieves a redis instance or None if redis isn't available."""
    # TODO: Create pool and simply grab instance?
    if os.getenv('REDIS_URL') is None:
        return None

    return Redis(
        host=os.getenv('REDIS_URL'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True,
    )
