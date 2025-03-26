import logging
import os
import time
from typing import Optional

import sentry_sdk.metrics
from redis import Redis, RedisCluster
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


_redis_instance: Optional[RedisCluster] = None


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


def boot_redis_cluster():
    """Open a connection to a redis cluster"""
    global _redis_instance
    if not os.getenv('REDIS_URL') or not os.getenv('REDIS_USE_CLUSTER'):
        return None

    host = os.getenv('REDIS_URL')
    port = int(os.getenv('REDIS_PORT'))
    password = os.getenv('REDIS_PASSWORD')
    ssl = (
        True
        if os.getenv('REDIS_USE_SSL')
        and (os.getenv('REDIS_USE_SSL').lower() == 'true' or os.getenv('REDIS_USE_SSL').lower() == '1')
        else False
    )
    timer_boot = time.perf_counter_ns()

    # Retry strategy
    retry = Retry(ExponentialBackoff(), 3)

    _redis_instance = RedisCluster(
        host=host,
        port=port,
        password=password,
        ssl=ssl,
        decode_responses=True,
        skip_full_coverage_check=True,
        retry=retry,
        cluster_error_retry_attempts=1,
    )
    sentry_sdk.set_measurement('redis_boot_time', time.perf_counter_ns() - timer_boot, 'nanosecond')
    logging.info('Connected to redis cluster')


def close_redis_cluster():
    """Close a connection to a redis cluster"""
    global _redis_instance
    if not _redis_instance or not os.getenv('REDIS_URL') or not os.getenv('REDIS_USE_CLUSTER'):
        return None

    _redis_instance.close()
    logging.info('Closed connection to redis cluster')


def get_redis(db=None) -> Redis | RedisCluster | None:
    """Retrieves a redis instance or None if redis isn't available."""
    # TODO: Create pool and simply grab instance?
    if os.getenv('REDIS_URL') is None:
        return None

    host = os.getenv('REDIS_URL')
    port = int(os.getenv('REDIS_PORT'))
    if db is None:
        db = os.getenv('REDIS_DB')
    password = os.getenv('REDIS_PASSWORD')
    ssl = (
        True
        if os.getenv('REDIS_USE_SSL')
        and (os.getenv('REDIS_USE_SSL').lower() == 'true' or os.getenv('REDIS_USE_SSL').lower() == '1')
        else False
    )

    timer_boot = time.perf_counter_ns()

    if os.getenv('REDIS_USE_CLUSTER'):
        return _redis_instance

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


def get_shared_redis() -> Redis | RedisCluster | None:
    """Retrieve a connection to the redis instance that is shared between services. Currently used for obtaining profile
    information via a session key."""
    return get_redis(os.getenv('TB_ACCOUNTS_REDIS_DB'))
