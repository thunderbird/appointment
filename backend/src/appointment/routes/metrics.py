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
        'apmt.user.locale': data.locale,
        'apmt.user.theme': data.theme,
        'apmt.user.screen': data.resolution,
        'apmt.user.ftue_max_level': subscriber.ftue_level
    })
    posthog.capture(distinct_id=subscriber.unique_hash, event='apmt.page.loaded', properties=payload)

    return True


@router.post('/ftue-step')
def ftue_step(
    request: Request,
    data: schemas.FTUEStepIn,
    posthog: Posthog | None = Depends(get_posthog),
    subscriber: Subscriber | None = Depends(get_subscriber),
):
    payload = {
        'apmt.ftue.step.name': data.step_name,
        'apmt.ftue.step.level': data.step_level
    }
    posthog.set(distinct_id=subscriber.unique_hash, properties=payload)
    posthog.capture(distinct_id=subscriber.unique_hash, event='apmt.ftue.step', properties={
        'step_name': data.step_name,
        'step_level': data.step_level
    })
