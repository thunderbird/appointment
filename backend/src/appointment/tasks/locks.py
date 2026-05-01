import uuid


DEFAULT_LOCK_TTL_SECONDS = 60 * 60


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
    lock_key = _task_lock_key(task_name)

    # Only delete lock if still owned by this task instance.
    release_script = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""
    redis_instance.eval(release_script, 1, lock_key, lock_token)
