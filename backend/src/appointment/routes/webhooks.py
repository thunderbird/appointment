import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import sentry_sdk
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from ..controller import zoom
from ..controller.google_watch import teardown_watch_channel
from ..database import repo
from ..dependencies.database import get_db
from ..dependencies.zoom import get_webhook_auth as get_webhook_auth_zoom
from ..tasks.google import sync_google_calendar_changes

router = APIRouter()


@router.post('/zoom-deauthorization')
def zoom_deauthorization(
    request: Request, db: Session = Depends(get_db), webhook_payload: dict | None = Depends(get_webhook_auth_zoom)
):
    if not webhook_payload:
        logging.warning('Invalid zoom webhook event received.')
        return

    user_id = webhook_payload.get('user_id')

    subscriber = repo.external_connection.get_subscriber_by_zoom_user_id(db, user_id)

    if not subscriber:
        logging.warning('Zoom webhook event received for non-existent user.')
        return

    try:
        zoom.disconnect(db, subscriber.id, user_id)
    except Exception as ex:
        sentry_sdk.capture_exception(ex)
        logging.error(f'Error disconnecting zoom connection: {ex}')


@router.post('/google-calendar')
def google_calendar_notification(
    request: Request,
    db: Session = Depends(get_db),
):
    """Webhook endpoint for Google Calendar push notifications.
    Google sends a POST here whenever events change on a watched calendar.

    Returns 200 immediately and defers all Google API work to a celery
    task so we stay within Google's expected response window and avoid
    duplicate deliveries from retries.
    """
    channel_id = request.headers.get('X-Goog-Channel-Id')
    resource_state = request.headers.get('X-Goog-Resource-State')

    success_response = Response(status_code=200)

    # Google sends a 'sync' notification when the channel is first created; just acknowledge it
    if not channel_id or resource_state == 'sync':
        return success_response

    channel = repo.google_calendar_channel.get_by_channel_id(db, channel_id)
    if not channel:
        logging.warning(f'[webhooks.google_calendar] Unknown channel_id: {channel_id}')
        return success_response

    incoming_state = request.headers.get('X-Goog-Channel-Token')
    if incoming_state != channel.state:
        logging.warning(f'[webhooks.google_calendar] State mismatch for channel {channel_id}')
        return success_response

    calendar = channel.calendar
    if not calendar:
        repo.google_calendar_channel.delete(db, channel)
        return success_response
    if not calendar.connected:
        teardown_watch_channel(db, calendar)
        return success_response

    # Google re-states the channel's expiration on every notification, so keep our
    # copy honest -- it is what is_push_active() trusts.
    expiration = _parse_expiration(request.headers.get('X-Goog-Channel-Expiration'))

    repo.google_calendar_channel.record_notification(db, channel, expiration=expiration)

    sync_google_calendar_changes.delay(channel_id)

    return success_response


def _parse_expiration(raw: str | None) -> datetime | None:
    """Parse the X-Goog-Channel-Expiration header into an aware UTC datetime.

    The header is an RFC-1123 date string, e.g. 'Tue, 19 Nov 2013 01:13:52 GMT' --
    *not* the epoch-milliseconds integer that the watch API response body uses for
    the same value (see google_watch.setup_watch_channel, which parses that one).
    Ref: https://developers.google.com/workspace/calendar/api/guides/push

    A naive result is rejected rather than assumed to be UTC: record_notification
    stores whatever it is given as naive-UTC, so an unzoned parse would write a
    timestamp of unknown offset into the column is_push_active() trusts.
    """
    if not raw:
        return None
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        logging.warning(f'[webhooks.google_calendar] Unparsable X-Goog-Channel-Expiration: {raw!r}')
        return None

    if parsed.tzinfo is None:
        logging.warning(f'[webhooks.google_calendar] X-Goog-Channel-Expiration has no timezone: {raw!r}')
        return None

    return parsed.astimezone(timezone.utc)
