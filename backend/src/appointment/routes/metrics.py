import hashlib

from fastapi import APIRouter, Request, Depends
from posthog import Posthog

from ..database import schemas
from ..database.models import Subscriber
from ..dependencies.auth import get_subscriber, get_subscriber_or_none

from ..dependencies.metrics import get_posthog

router = APIRouter()

def get_api_url(request: Request):
    return f'{request.url.scheme}://{request.headers.get("Host")}/api/v1{request.url.path}'


def get_api_path(request: Request):
    return f'/api/v1{request.url.path}'


@router.post('/page-load')
def page_load(
    request: Request,
    data: schemas.PageLoadIn,
    posthog: Posthog | None = Depends(get_posthog),
    subscriber: Subscriber | None = Depends(get_subscriber_or_none),
):
    if posthog is None:
        return False

    url = get_api_path(request)
    current_url = get_api_url(request)

    lang = request.headers.get('Accept-Language', 'en-US').split(',')[0]
    payload = {
        'hostname': request.headers.get('Host'),
        'language': lang,
        'url': url,
        'referrer': request.headers.get('Referer'),
        'screen': data.resolution,
        'locale': data.locale,
        'theme': data.theme,
        '$current_url': current_url,
    }

    if not subscriber:
        sauce = '-'.join([request.client.host, data.browser_version, data.os_version])

        hash_instance = hashlib.sha3_256()
        hash_instance.update(sauce.encode('utf-8'))
        distinct_id = f'anon-{hash_instance.hexdigest()}'
    else:
        distinct_id = subscriber.unique_hash

    # We only want to set user info if they're logged in, because most of this info isn't set yet...
    if subscriber:
        posthog.set(distinct_id=distinct_id, properties={
            'apmt.user.locale': data.locale,
            'apmt.user.theme': data.theme,
            'apmt.user.screen': data.resolution,
            'apmt.user.ftue_max_level': subscriber.ftue_level
        })

    # Set a display id
    posthog.set(distinct_id=distinct_id, properties={
        'display_id': distinct_id
    })

    posthog.capture(distinct_id=distinct_id, event='apmt.page.loaded', properties=payload)
    return {'id': distinct_id}


@router.post('/ftue-step')
def ftue_step(
    request: Request,
    data: schemas.FTUEStepIn,
    posthog: Posthog | None = Depends(get_posthog),
    subscriber: Subscriber | None = Depends(get_subscriber),
):

    current_url = get_api_url(request)
    payload = {
        'apmt.ftue.step.name': data.step_name,
        'apmt.ftue.step.level': data.step_level,
        '$current_url': current_url
    }
    posthog.set(distinct_id=subscriber.unique_hash, properties=payload)
    posthog.capture(distinct_id=subscriber.unique_hash, event='apmt.ftue.step', properties={
        'step_name': data.step_name,
        'step_level': data.step_level
    })
