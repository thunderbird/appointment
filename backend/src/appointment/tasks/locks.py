import logging
import os
import uuid
from contextlib import contextmanager
from appointment.dependencies.database import get_redis

DEFAULT_LOCK_TTL_SECONDS = 60 * 60


class TaskLockFailed(Exception):
    """Raised when a task lock cannot be acquired."""


def _task_lock_key(task_name: str) -> str:
    return f'lock:task:{task_name}'


def acquire_task_lock(redis_instance, task_name: str, ttl_seconds: int = DEFAULT_LOCK_TTL_SECONDS) -> str | None:
    lock_key = _task_lock_key(task_name)
    lock_token = str(uuid.uuid4())
    lock_acquired = bool(redis_instance.set(lock_key, lock_token, nx=True, ex=ttl_seconds))
    if not lock_acquired:
        return None
    return lock_token


def release_task_lock(redis_instance, task_name: str, lock_token: str):
    """Only delete the lock if still owned by this task instance."""
    lock_key = _task_lock_key(task_name)

    with redis_instance.pipeline() as pipe:
        pipe.watch(lock_key)
        if pipe.get(lock_key) == lock_token:
            pipe.multi()
            pipe.delete(lock_key)
            pipe.execute()
        else:
            pipe.unwatch()


@contextmanager
def task_lock(task_name: str, ttl_seconds: int = DEFAULT_LOCK_TTL_SECONDS):
    """Context manager that acquires and releases a distributed task lock.

    Raises TaskLockFailed if Redis is available but the lock is already held.
    When Redis is unavailable, execution proceeds without a lock.
    """
    import sentry_sdk

    redis_instance = get_redis(os.getenv('REDIS_CELERY_DB'))
    lock_token = None

    if redis_instance is not None:
        lock_token = acquire_task_lock(redis_instance, task_name, ttl_seconds)
        if lock_token is None:
            raise TaskLockFailed(f'Failed to acquire lock for {task_name}')
    else:
        logging.warning(f'Redis unavailable; running {task_name} without distributed lock.')

    try:
        yield
    except Exception as e:
        logging.warning(f'{task_name} failed: {e}')
        sentry_sdk.capture_exception(e)
        raise
    finally:
        if lock_token is not None:
            try:
                release_task_lock(redis_instance, task_name, lock_token)
            except Exception as e:
                logging.warning(f'Failed to release {task_name} lock: {e}')
                sentry_sdk.capture_exception(e)
