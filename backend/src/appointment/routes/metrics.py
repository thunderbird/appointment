from fastapi import APIRouter, Request, Depends
from posthog import Posthog

from ..database import schemas
from ..database.models import Subscriber
from ..dependencies.auth import get_subscriber

from ..dependencies.metrics import get_posthog

router = APIRouter()


@router.post('/page-load')
def page_load(
    request: Request,
    data: schemas.PageLoadIn,
    posthog: Posthog | None = Depends(get_posthog),
    subscriber: Subscriber | None = Depends(get_subscriber),
):
    if posthog is None or subscriber is None:
        return False

    url = f'/api/v1{request.url.path}'
    lang = request.headers.get('Accept-Language', 'en-US').split(',')[0]
    payload = {
        'hostname': request.headers.get('Host'),
        'language': lang,
        'url': url,
        'referrer': request.headers.get('Referer'),
        'screen': data.resolution,
        'locale': data.locale,
        'theme': data.theme,
    }
    posthog.set(distinct_id=subscriber.unique_hash, properties={
        'apmt.user': {
            'locale': data.locale,
            'theme': data.theme,
            'screen': data.resolution,
            'ftue_max_level': subscriber.ftue_level
        }
    })
    posthog.capture(distinct_id=subscriber.unique_hash, event='page.loaded', properties=payload)

    return True


@router.post('/ftue-step')
def ftue_step(
    request: Request,
    data: schemas.FTUEStepIn,
    posthog: Posthog | None = Depends(get_posthog),
    subscriber: Subscriber | None = Depends(get_subscriber),
):
    posthog.set(distinct_id=subscriber.unique_hash, properties={
        'apmt.ftue': {
            'step.name': data.step_name,
            'step.level': data.step_level,
        }
    })
