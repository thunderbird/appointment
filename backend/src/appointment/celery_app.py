import os

import sentry_sdk
from celery import Celery
from dotenv import load_dotenv
from appointment.defines import ONE_DAY_IN_SECONDS, SEVEN_DAYS_IN_SECONDS


def _base_redis_url() -> str:
    """Build a redis(s):// base URL from the app's REDIS_* env vars."""
    host = os.getenv('REDIS_URL', 'localhost')
    port = os.getenv('REDIS_PORT', '6379')
    password = os.getenv('REDIS_PASSWORD', '')
    use_ssl = os.getenv('REDIS_USE_SSL', '')

    scheme = 'rediss' if use_ssl.lower() in ('true', '1') else 'redis'
    auth = f':{password}@' if password else ''
    return f'{scheme}://{auth}{host}:{port}'


def create_celery_app() -> Celery:
    load_dotenv()

    redis_url = _base_redis_url()

    broker_url = '/'.join(filter(None, [os.getenv('CELERY_BROKER') or redis_url, os.getenv('REDIS_CELERY_DB')]))
    result_backend = '/'.join(
        filter(None, [os.getenv('CELERY_BACKEND') or redis_url, os.getenv('REDIS_CELERY_RESULTS_DB')])
    )

    if broker_url.startswith('rediss://'):
        broker_url = f'{broker_url}?ssl_cert_reqs=CERT_REQUIRED'
    if result_backend.startswith('rediss://'):
        result_backend = f'{result_backend}?ssl_cert_reqs=CERT_REQUIRED'

    result_expires = 3600
    task_always_eager = os.getenv('CELERY_EAGER', 'False') == 'True'

    sentry_sdk.set_extra('CELERY_BROKER_URL', broker_url)
    sentry_sdk.set_extra('CELERY_RESULT_BACKEND', result_backend)
    sentry_sdk.set_extra('CELERY_RESULT_EXPIRES', result_expires)
    sentry_sdk.set_extra('CELERY_TASK_ALWAYS_EAGER', task_always_eager)

    google_channel_ttl = float(os.getenv('GOOGLE_CHANNEL_TTL_IN_SECONDS', SEVEN_DAYS_IN_SECONDS))
    google_channel_renew_interval = google_channel_ttl - ONE_DAY_IN_SECONDS

    app = Celery('appointment')

    app.config_from_object({
        'broker_url': broker_url,
        'result_backend': result_backend,
        'result_expires': result_expires,
        'task_always_eager': task_always_eager,
        'broker_connection_retry_on_startup': True,
        'task_default_queue': 'appointment',
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json'],
        'timezone': 'UTC',
        'enable_utc': True,
        'beat_schedule': {
            'heartbeat-every-60s': {
                'task': 'appointment.tasks.health.heartbeat',
                'schedule': 60.0,
            },
            'renew-google-channels': {
                'task': 'appointment.tasks.google.renew_google_channels',
                'schedule': google_channel_renew_interval,
            },
        },
        'beat_schedule_filename': 'celerybeat-appointment-schedule',
    })

    app.autodiscover_tasks(['appointment'])

    return app


celery = create_celery_app()
