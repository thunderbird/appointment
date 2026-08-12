import json
import logging
import os
from datetime import datetime, timedelta, timezone

import sentry_sdk
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from appointment.celery_app import celery
from appointment.controller.apis.google_client import EventStatus, GoogleClient, ResponseStatus, SendUpdates
from appointment.controller import zoom
from appointment.database import repo, models, schemas
from appointment.database.models import MeetingLinkProviderType
from appointment.defines import FALLBACK_LOCALE
from appointment.dependencies.database import get_engine_and_session, get_redis
from appointment.dependencies.google import get_google_client
from appointment.l10n import l10n

log = logging.getLogger(__name__)


@celery.task
def renew_google_channels():
    from appointment.commands.renew_google_channels import run

    log.info('Starting Google Calendar channel renewal')
    try:
        run()
    except Exception as e:
        log.error(f'Google Calendar channel renewal failed: {e}')
        sentry_sdk.capture_exception(e)
        raise
    log.info('Google Calendar channel renewal complete')


@celery.task
def reconcile_google_channels():
    """Periodically sync channels that push has not refreshed recently.

    Push delivery is best-effort: Google does not guarantee a notification for
    every change, and a channel can go quiet because nothing happened or because
    delivery is broken -- the two are indistinguishable from our side. This sweep
    removes the need to tell them apart by syncing any channel that has not been
    refreshed within the reconcile interval, which bounds how long a dropped
    notification can go unnoticed.

    If this sweep itself stops working, `last_synced_at` ages past MAX_SYNC_AGE
    and is_push_active() turns false, so read paths return to polling Google.
    """
    from appointment.controller.google_watch import MAX_SYNC_AGE

    _, SessionLocal = get_engine_and_session()
    db = SessionLocal()

    reconciled = 0
    skipped = 0

    try:
        interval = timedelta(seconds=reconcile_interval_seconds())
        synced_before = (datetime.now(tz=timezone.utc) - interval).replace(tzinfo=None)
        channels = repo.google_calendar_channel.get_stale(db, synced_before=synced_before)

        for channel in channels:
            calendar = channel.calendar
            if not calendar or not calendar.connected:
                skipped += 1
                continue

            try:
                sync_google_calendar_changes(channel.channel_id)
                reconciled += 1
            except Exception as ex:
                # One bad channel must not stop the sweep for everyone else.
                log.warning(f'[tasks.google] Reconcile failed for channel {channel.channel_id}: {ex}')
                sentry_sdk.capture_exception(ex)
                skipped += 1
    finally:
        db.close()

    log.info(
        f'[tasks.google] Reconciliation complete: {reconciled} synced, {skipped} skipped '
        f'(channels unsynced for > {reconcile_interval_seconds()}s; '
        f'push is distrusted entirely after {int(MAX_SYNC_AGE.total_seconds())}s)'
    )


def reconcile_interval_seconds() -> int:
    """How stale a channel may get before the sweep re-syncs it."""
    return int(os.getenv('GOOGLE_RECONCILE_INTERVAL_SECONDS', 900))


@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def stop_google_channel(self, channel_id: str, resource_id: str, token_json: str):
    """Stop a Google Calendar push notification channel, with automatic retries."""
    google_client = get_google_client()
    token = Credentials.from_authorized_user_info(
        json.loads(token_json), google_client.SCOPES
    )
    google_client.stop_channel(channel_id, resource_id, token)
    log.info(f'Stopped Google Calendar channel {channel_id}')


@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def sync_google_calendar_changes(self, channel_id: str):
    """Fetch and process changed events for a Google Calendar push notification.

    Called by the webhook handler after lightweight validation.  Handles sync
    token management, event fetching via the Google API, and event processing
    with automatic retries on transient failures.
    """
    google_client = get_google_client()

    _, SessionLocal = get_engine_and_session()
    db = SessionLocal()

    try:
        channel = repo.google_calendar_channel.get_by_channel_id(db, channel_id)
        if not channel:
            log.warning(f'[tasks.google] Channel {channel_id} not found, skipping')
            return

        calendar = channel.calendar
        if not calendar or not calendar.connected:
            log.warning(f'[tasks.google] Calendar for channel {channel_id} missing or disconnected')
            return

        external_connection = calendar.external_connection
        if not external_connection or not external_connection.token:
            log.warning(f'[tasks.google] No token for calendar on channel {channel_id}')
            return

        google_token = Credentials.from_authorized_user_info(
            json.loads(external_connection.token), google_client.SCOPES
        )

        if not channel.sync_token:
            sync_token = google_client.get_initial_sync_token(calendar.user, google_token)
            if sync_token:
                repo.google_calendar_channel.record_sync(db, channel, sync_token)

        changed_events, new_sync_token = google_client.list_events_sync(
            calendar.user, channel.sync_token, google_token
        )

        if changed_events is None:
            # 410 Gone: Google invalidated our sync token, so the delta we would
            # have received is unrecoverable. Re-establishing the token alone
            # would silently swallow those changes, so do a bounded full resync
            # to catch up before resuming incremental sync.
            _recover_from_invalid_sync_token(db, channel, calendar, google_client, google_token)
            return

        if changed_events:
            _process_changed_events(
                db, calendar.id, changed_events, google_client, google_token, calendar.user
            )

        # Stamp the watermark only after the changes have been applied: it is what
        # is_push_active() trusts, so it must never run ahead of the local state.
        repo.google_calendar_channel.record_sync(db, channel, new_sync_token)

        if changed_events:
            # The calendar moved, so any cached availability for this subscriber
            # is now suspect. Busting is what lets read paths serve from cache
            # between notifications instead of polling Google every request.
            _bust_subscriber_cache(calendar)
    finally:
        db.close()


def _bust_subscriber_cache(calendar: models.Calendar):
    """Drop cached remote events/free-busy for the calendar's owner.

    Deliberately busts every calendar of the subscriber rather than just this
    one: free/busy entries are cached per *set* of calendars, so an entry
    covering this calendar can be filed under another calendar's key.

    Never raises -- a failed bust costs staleness until the TTL expires, but must
    not fail the sync that has already been applied.
    """
    from appointment.controller.calendar import BaseConnector

    try:
        redis_instance = get_redis()
        if redis_instance is None:
            return

        connector = BaseConnector(
            subscriber_id=calendar.owner_id,
            calendar_id=calendar.id,
            redis_instance=redis_instance,
        )
        deleted = connector.bust_cached_events(all_calendars=True)
        log.info(f'[tasks.google] Busted {deleted} cached entries for subscriber {calendar.owner_id}')
    except Exception as ex:
        log.warning(f'[tasks.google] Failed to bust cache for calendar {calendar.id}: {ex}')
        sentry_sdk.capture_exception(ex)


def _recover_from_invalid_sync_token(
    db: Session,
    channel: models.GoogleCalendarChannel,
    calendar: models.Calendar,
    google_client: GoogleClient,
    google_token,
):
    """Recover after Google answers 410 fullSyncRequired.

    An invalidated sync token means we cannot know what changed. Recovery is:
      1. drop the cache, so reads stop trusting anything derived from the lost
         delta and fall back to Google,
      2. re-scan a bounded forward window and re-apply RSVP/cancellation state,
         so bookings that changed during the blackout are not missed,
      3. establish a fresh token and re-stamp the watermark.

    If step 3 fails the watermark is left alone, so is_push_active() ages the
    channel out and read paths return to polling -- stale, never silently wrong.
    """
    log.info(f'[tasks.google] Sync token invalidated for channel {channel.channel_id}, running full resync')

    _bust_subscriber_cache(calendar)

    now = datetime.now(tz=timezone.utc)
    window_days = int(os.getenv('GOOGLE_FULL_RESYNC_WINDOW_DAYS', 90))
    try:
        events = google_client.list_events(
            calendar.user,
            now.isoformat(),
            (now + timedelta(days=window_days)).isoformat(),
            google_token,
        )
        if events:
            _process_changed_events(
                db, calendar.id, events, google_client, google_token, calendar.user
            )
    except Exception as ex:
        # Fall through to re-establish the token regardless; the reconciliation
        # sweep will retry, and until it succeeds the stale watermark keeps read
        # paths polling.
        log.warning(f'[tasks.google] Full resync scan failed for channel {channel.channel_id}: {ex}')
        sentry_sdk.capture_exception(ex)

    fresh_token = google_client.get_initial_sync_token(calendar.user, google_token)
    if fresh_token:
        repo.google_calendar_channel.record_sync(db, channel, fresh_token)
    else:
        log.warning(
            f'[tasks.google] Could not re-establish sync token for channel {channel.channel_id}; '
            f'push stays untrusted until reconciliation succeeds'
        )


def _process_changed_events(
    db, calendar_id: int, changed_events: list[dict],
    google_client: GoogleClient, google_token, remote_calendar_id: str,
):
    """Walk through changed events and dispatch to the appropriate RSVP / cancellation handler."""
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

        if event.get('status') == EventStatus.CANCELLED:
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
    response_status: ResponseStatus,
    google_client: GoogleClient,
    google_token,
    remote_calendar_id: str,
):
    """React to the subscriber (calendar owner) accepting/declining via Google Calendar."""
    if response_status == ResponseStatus.ACCEPTED:
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
            body = {'status': EventStatus.CONFIRMED, 'summary': title}

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
                            att['responseStatus'] = ResponseStatus.ACCEPTED
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

    elif response_status == ResponseStatus.DECLINED:
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
    response_status: ResponseStatus,
    google_client: GoogleClient,
    google_token,
    remote_calendar_id: str,
):
    """React to the bookee's RSVP status change from Google Calendar."""
    if response_status == ResponseStatus.DECLINED:
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

    elif response_status == ResponseStatus.ACCEPTED:
        log.info(
            f'[tasks.google] Bookee accepted appointment {appointment.id}, '
            f'slot {slot.id}'
        )
