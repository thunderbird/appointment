import json
import logging

import sentry_sdk
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from appointment.celery_app import celery
from appointment.controller.apis.google_client import GoogleClient, SendUpdates
from appointment.controller import zoom
from appointment.database import repo, models, schemas
from appointment.database.models import MeetingLinkProviderType
from appointment.defines import FALLBACK_LOCALE
from appointment.dependencies.database import get_engine_and_session
from appointment.dependencies.google import get_google_client
from appointment.l10n import l10n

log = logging.getLogger(__name__)


@celery.task
def renew_google_channels():
    from appointment.commands.renew_google_channels import run

    log.info('Starting Google Calendar channel renewal')
    run()
    log.info('Google Calendar channel renewal complete')


@celery.task
def process_google_event_changes(calendar_id: int, changed_events: list[dict]):
    """Process changed events from a Google Calendar push notification."""
    google_client = get_google_client()

    _, SessionLocal = get_engine_and_session()
    db = SessionLocal()

    try:
        calendar = repo.calendar.get(db, calendar_id)
        if not calendar or not calendar.external_connection or not calendar.external_connection.token:
            log.warning(f'[tasks.google] Calendar {calendar_id} missing or has no external connection')
            return

        google_token = Credentials.from_authorized_user_info(
            json.loads(calendar.external_connection.token), google_client.SCOPES
        )
        remote_calendar_id = calendar.user

        for event in changed_events:
            google_event_id = event.get('id')
            if not google_event_id:
                continue

            appointment = repo.appointment.get_by_calendar_and_external_id(db, calendar_id, google_event_id)
            if not appointment:
                continue

            slot = appointment.slots[0] if appointment.slots else None
            if not slot or not slot.attendee:
                continue

            if event.get('status') == 'cancelled':
                _handle_event_cancelled(db, appointment, slot)
                continue

            attendees = event.get('attendees', [])
            if not attendees:
                continue

            self_attendee = next((a for a in attendees if a.get('self')), None)
            if self_attendee:
                _handle_subscriber_rsvp(
                    db, appointment, slot, self_attendee.get('responseStatus'),
                    google_client, google_token, remote_calendar_id,
                )

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
        log.error(f'[tasks.google] Error processing event changes: {e}')
        if sentry_sdk.is_initialized():
            sentry_sdk.capture_exception(e)
    finally:
        db.close()



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

    log.info(
        f'[tasks.google] Event cancelled for appointment {appointment.id}, '
        f'slot {slot.id} marked as cancelled'
    )


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
            from appointment.controller.calendar import Tools

            subscriber = appointment.calendar.owner
            title = Tools.default_event_title(slot, subscriber)
            repo.appointment.update_title(db, appointment.id, title)

            location_url = appointment.location_url
            if appointment.meeting_link_provider == MeetingLinkProviderType.zoom:
                location_url = zoom.create_meeting_link(db, slot, subscriber, title) or location_url

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
                    for att in remote_event.get('attendees', []):
                        if att.get('self'):
                            att['responseStatus'] = 'accepted'
                    body['attendees'] = remote_event['attendees']

                google_client.patch_event(
                    remote_calendar_id, appointment.external_id, body, google_token,
                )
            except Exception:
                log.warning('[tasks.google] Failed to confirm event in Google')

        log.info(
            f'[tasks.google] Subscriber confirmed appointment {appointment.id} '
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
                        send_updates=SendUpdates.ALL,
                    )
                except Exception:
                    log.warning('[tasks.google] Failed to delete declined event from Google')

            log.info(
                f'[tasks.google] Subscriber declined appointment {appointment.id} '
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
                    log.warning('[tasks.google] Failed to delete declined event from Google')

            log.info(
                f'[tasks.google] Bookee declined appointment {appointment.id}, '
                f'slot {slot.id} marked as declined'
            )

    elif response_status == 'accepted':
        log.info(
            f'[tasks.google] Bookee accepted appointment {appointment.id}, '
            f'slot {slot.id}'
        )
