import os
import time

import sentry_sdk.metrics
from redis import Redis, RedisCluster
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_engine_and_session():
    database_url = os.getenv('DATABASE_URL')
    connect_args = {}

    if 'sqlite://' in database_url:
        connect_args = {'check_same_thread': False}

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


def get_redis() -> Redis | RedisCluster | None:
    """Retrieves a redis instance or None if redis isn't available."""
    # TODO: Create pool and simply grab instance?
    if os.getenv('REDIS_URL') is None:
        return None

    host = os.getenv('REDIS_URL')
    port = int(os.getenv('REDIS_PORT'))
    db = os.getenv('REDIS_DB')
    password = os.getenv('REDIS_PASSWORD')
    ssl = True if os.getenv('REDIS_USE_SSL') and (os.getenv('REDIS_USE_SSL').lower() == 'true' or os.getenv('REDIS_USE_SSL').lower() == '1') else False

    timer_boot = time.perf_counter_ns()

    if os.getenv('REDIS_USE_CLUSTER'):
        cluster = RedisCluster(
            host=host,
            port=port,
            password=password,
            ssl=ssl,
            decode_responses=True,
        )

        sentry_sdk.set_measurement('redis_boot_time', time.perf_counter_ns() - timer_boot, 'nanosecond')

        return cluster

    redis = Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        ssl=ssl,
        decode_responses=True,
    )

    sentry_sdk.set_measurement('redis_boot_time', time.perf_counter_ns() - timer_boot, 'nanosecond')
    return redis
