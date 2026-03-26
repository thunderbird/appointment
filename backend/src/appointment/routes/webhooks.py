import json
import logging

import requests
import sentry_sdk
from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from ..controller import auth, data, zoom
from ..controller.apis.fxa_client import FxaClient
from ..controller.apis.google_client import GoogleClient
from ..controller.calendar import Tools
from ..controller.google_watch import teardown_watch_channel
from ..database import repo, models, schemas
from ..database.models import MeetingLinkProviderType
from ..defines import FALLBACK_LOCALE
from ..dependencies.database import get_db, get_redis
from ..dependencies.fxa import get_webhook_auth as get_webhook_auth_fxa, get_fxa_client
from ..dependencies.google import get_google_client
from ..dependencies.zoom import get_zoom_client, get_webhook_auth as get_webhook_auth_zoom
from ..exceptions.account_api import AccountDeletionSubscriberFail
from ..exceptions.fxa_api import MissingRefreshTokenException
from ..l10n import l10n

router = APIRouter()


@router.post('/fxa-process')
def fxa_process(
    db: Session = Depends(get_db),
    decoded_token: dict = Depends(get_webhook_auth_fxa),
    fxa_client: FxaClient = Depends(get_fxa_client),
):
    """Main for webhooks regarding fxa"""

    subscriber: models.Subscriber = repo.external_connection.get_subscriber_by_fxa_uid(db, decoded_token.get('sub'))
    if not subscriber:
        logging.warning('FXA webhook event received for non-existent user.')
        return

    subscriber_external_connection = subscriber.get_external_connection(models.ExternalConnectionType.fxa)
    fxa_client.setup(subscriber.id, token=subscriber_external_connection.token)

    for event, event_data in decoded_token.get('events', {}).items():
        match event:
            case 'https://schemas.accounts.firefox.com/event/password-change':
                # Ensure we ignore out of date requests, also .timestamp() returns seconds, but we get the time in ms.
                # TODO: We may need a last update timestamp JUST for token field changes.
                token_last_updated = subscriber_external_connection.time_updated.timestamp() * 1000
                if token_last_updated > event_data.get('changeTime'):
                    logging.info('Ignoring out of date logout request.')
                    break

                try:
                    auth.logout(db, subscriber, fxa_client)
                except MissingRefreshTokenException:
                    logging.warning("Subscriber doesn't have refresh token.")
                except requests.exceptions.HTTPError as ex:
                    sentry_sdk.capture_exception(ex)
                    logging.error(f'Error logging out user: {ex.response}')
            case 'https://schemas.accounts.firefox.com/event/profile-change':
                if event_data.get('email') is not None:
                    # Update the subscriber's email, we do this first in case there's a problem with get_profile()
                    subscriber.email = event_data.get('email').lower()
                    db.add(subscriber)
                    db.commit()

                try:
                    profile = fxa_client.get_profile()
                    # Update profile with fxa info
                    repo.subscriber.update(
                        db,
                        schemas.SubscriberIn(
                            avatar_url=profile['avatar'], name=subscriber.name, username=subscriber.username
                        ),
                        subscriber.id,
                    )
                except Exception as ex:
                    logging.error(f'Error updating user: {ex}')

                # Finally log the subscriber out
                try:
                    auth.logout(db, subscriber, fxa_client)
                except MissingRefreshTokenException:
                    logging.warning("Subscriber doesn't have refresh token.")
                except requests.exceptions.HTTPError as ex:
                    sentry_sdk.capture_exception(ex)
                    logging.error(f'Error logging out user: {ex.response}')
            case 'https://schemas.accounts.firefox.com/event/delete-user':
                try:
                    data.delete_account(db, subscriber)
                except AccountDeletionSubscriberFail as ex:
                    sentry_sdk.capture_exception(ex)
                    logging.error(f'Account deletion webhook failed: {ex.message}')

            case _:
                logging.warning(f'Ignoring event {event}')


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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    google_client: GoogleClient = Depends(get_google_client),
):
    """Webhook endpoint for Google Calendar push notifications.
    Google sends a POST here whenever events change on a watched calendar."""
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

    calendar = channel.calendar
    if not calendar:
        repo.google_calendar_channel.delete(db, channel)
        return success_response
    if not calendar.connected:
        teardown_watch_channel(db, google_client, calendar)
        return success_response

    external_connection = calendar.external_connection
    if not external_connection or not external_connection.token:
        teardown_watch_channel(db, google_client, calendar)
        return success_response

    token = Credentials.from_authorized_user_info(
        json.loads(external_connection.token), google_client.SCOPES
    )

    if not channel.sync_token:
        sync_token = google_client.get_initial_sync_token(calendar.user, token)
        if sync_token:
            repo.google_calendar_channel.update_sync_token(db, channel, sync_token)
        return success_response

    changed_events, new_sync_token = google_client.list_events_sync(
        calendar.user, channel.sync_token, token
    )

    if changed_events is None:
        # Sync token expired -- do a full re-sync to get a fresh one
        fresh_token = google_client.get_initial_sync_token(calendar.user, token)
        if fresh_token:
            repo.google_calendar_channel.update_sync_token(db, channel, fresh_token)
        return success_response

    if new_sync_token:
        repo.google_calendar_channel.update_sync_token(db, channel, new_sync_token)

    background_tasks.add_task(
        _process_google_event_changes,
        calendar_id=calendar.id,
        changed_events=changed_events,
        google_client=google_client,
        google_token=token,
        remote_calendar_id=calendar.user,
    )

    return success_response



def _process_google_event_changes(
    calendar_id: int,
    changed_events: list[dict],
    google_client: GoogleClient,
    google_token,
    remote_calendar_id: str,
):
    """Process changed events from a Google Calendar push notification.
    Runs as a background task to avoid blocking the webhook response."""
    from ..dependencies.database import get_engine_and_session

    _, SessionLocal = get_engine_and_session()
    db = SessionLocal()

    try:
        for event in changed_events:
            google_event_id = event.get('id')
            if not google_event_id:
                continue

            appointment = _find_appointment_by_external_id(db, calendar_id, google_event_id)
            if not appointment:
                continue

            slot = appointment.slots[0] if appointment.slots else None
            if not slot or not slot.attendee:
                continue

            # Subscriber deleted/cancelled the event from Google Calendar
            if event.get('status') == 'cancelled':
                _handle_event_cancelled(db, appointment, slot)
                continue

            attendees = event.get('attendees', [])
            if not attendees:
                continue

            # Check if the subscriber (calendar owner) responded via Google Calendar
            self_attendee = next((a for a in attendees if a.get('self')), None)
            if self_attendee:
                _handle_subscriber_rsvp(
                    db, appointment, slot, self_attendee.get('responseStatus'),
                    google_client, google_token, remote_calendar_id,
                )

            # Check if the bookee responded via Google Calendar
            attendee_email = slot.attendee.email.lower()
            google_attendee = next(
                (a for a in attendees if a.get('email', '').lower() == attendee_email),
                None,
            )
            if not google_attendee:
                continue

            response_status = google_attendee.get('responseStatus')
            _handle_bookee_rsvp(
                db, appointment, slot, response_status, google_client, google_token, remote_calendar_id
            )
    except Exception as e:
        logging.error(f'[webhooks.google_calendar] Error processing event changes: {e}')
        if sentry_sdk.is_initialized():
            sentry_sdk.capture_exception(e)
    finally:
        db.close()


def _find_appointment_by_external_id(
    db: Session, calendar_id: int, external_id: str
) -> models.Appointment | None:
    """Find an appointment on the given calendar matching the Google event ID."""
    appointments = (
        db.query(models.Appointment)
        .filter(models.Appointment.calendar_id == calendar_id)
        .all()
    )
    for appointment in appointments:
        if appointment.external_id == external_id:
            return appointment
    return None


def _handle_event_cancelled(
    db: Session,
    appointment: models.Appointment,
    slot: models.Slot,
):
    """Handle a Google Calendar event that was deleted/cancelled by the subscriber."""
    if slot.booking_status not in (models.BookingStatus.requested, models.BookingStatus.booked):
        return

    slot_update = schemas.SlotUpdate(booking_status=models.BookingStatus.cancelled)
    repo.slot.update(db, slot.id, slot_update)

    logging.info(
        f'[webhooks.google_calendar] Event cancelled for appointment {appointment.id}, '
        f'slot {slot.id} marked as cancelled'
    )


def _create_zoom_meeting_link(
    db: Session,
    slot: models.Slot,
    subscriber: models.Subscriber,
    title: str,
) -> str | None:
    """Try to create a Zoom meeting link and persist it on the slot.

    Returns the join URL on success, or ``None`` on any failure.
    """
    try:
        zoom_client = get_zoom_client(subscriber)
        response = zoom_client.create_meeting(title, slot.start.isoformat(), slot.duration, subscriber.timezone)
        if 'id' in response:
            join_url = zoom_client.get_meeting(response['id'])['join_url']
            slot.meeting_link_id = response['id']
            slot.meeting_link_url = join_url
            db.add(slot)
            db.commit()
            return join_url
    except Exception as err:
        logging.error(f'[webhooks.google_calendar] Zoom meeting creation error: {err}')
        if sentry_sdk.is_initialized():
            sentry_sdk.capture_exception(err)
    return None


def _handle_subscriber_rsvp(
    db: Session,
    appointment: models.Appointment,
    slot: models.Slot,
    response_status: str,
    google_client: GoogleClient,
    google_token,
    remote_calendar_id: str,
):
    """React to the subscriber (calendar owner) accepting/declining via Google Calendar."""
    if response_status == 'accepted':
        if (
            appointment.status != models.AppointmentStatus.opened
            or slot.booking_status != models.BookingStatus.requested
        ):
            return

        repo.appointment.update_status(db, appointment.id, models.AppointmentStatus.closed)
        repo.slot.book(db, slot.id)

        if appointment.external_id:
            subscriber = appointment.calendar.owner
            title = Tools.default_event_title(slot, subscriber)
            repo.appointment.update_title(db, appointment.id, title)

            location_url = appointment.location_url
            if appointment.meeting_link_provider == MeetingLinkProviderType.zoom:
                location_url = _create_zoom_meeting_link(db, slot, subscriber, title) or location_url

            owner_lang = subscriber.language if subscriber.language else FALLBACK_LOCALE
            body = {'status': 'confirmed', 'summary': title}

            if location_url:
                body['location'] = location_url

            description = [appointment.details or '']
            if location_url:
                description.append(l10n('join-online', {'url': location_url}, lang=owner_lang))

            body['description'] = '\n'.join(description)

            try:
                remote_event = google_client.get_event(remote_calendar_id, appointment.external_id, google_token)
                if remote_event and remote_event.get('attendees'):
                    for att in remote_event['attendees']:
                        if att.get('self'):
                            att['responseStatus'] = 'accepted'
                    body['attendees'] = remote_event['attendees']

                google_client.patch_event(
                    remote_calendar_id, appointment.external_id, body, google_token,
                )
            except Exception:
                logging.warning('[webhooks.google_calendar] Failed to confirm event in Google')

        logging.info(
            f'[webhooks.google_calendar] Subscriber confirmed appointment {appointment.id} '
            f'via Google Calendar, slot {slot.id} booked'
        )

    elif response_status == 'declined':
        if slot.booking_status in (models.BookingStatus.requested, models.BookingStatus.booked):
            slot_update = schemas.SlotUpdate(booking_status=models.BookingStatus.declined)
            repo.slot.update(db, slot.id, slot_update)

            if appointment.external_id:
                try:
                    google_client.delete_event(
                        remote_calendar_id, appointment.external_id, google_token,
                        send_updates='all',
                    )
                except Exception:
                    logging.warning('[webhooks.google_calendar] Failed to delete declined event from Google')

            logging.info(
                f'[webhooks.google_calendar] Subscriber declined appointment {appointment.id} '
                f'via Google Calendar, slot {slot.id} marked as declined'
            )


def _handle_bookee_rsvp(
    db: Session,
    appointment: models.Appointment,
    slot: models.Slot,
    response_status: str,
    google_client: GoogleClient,
    google_token,
    remote_calendar_id: str,
):
    """React to the bookee's RSVP status change from Google Calendar."""
    if response_status == 'declined':
        if slot.booking_status in (models.BookingStatus.requested, models.BookingStatus.booked):
            slot_update = schemas.SlotUpdate(booking_status=models.BookingStatus.declined)
            repo.slot.update(db, slot.id, slot_update)

            if appointment.external_id:
                try:
                    google_client.delete_event(remote_calendar_id, appointment.external_id, google_token)
                except Exception:
                    logging.warning('[webhooks.google_calendar] Failed to delete declined event from Google')

            logging.info(
                f'[webhooks.google_calendar] Bookee declined appointment {appointment.id}, '
                f'slot {slot.id} marked as declined'
            )

    elif response_status == 'accepted':
        logging.info(
            f'[webhooks.google_calendar] Bookee accepted appointment {appointment.id}, '
            f'slot {slot.id}'
        )
