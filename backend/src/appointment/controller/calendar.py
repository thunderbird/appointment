"""Module: caldav

Handle connection to a CalDAV server.
"""

import json
import logging
import time
import zoneinfo
import os
from urllib.parse import urlparse, urljoin

import caldav.lib.error
import requests
import sentry_sdk
from dns.exception import DNSException
from redis import Redis, RedisCluster
from caldav import DAVClient
from fastapi import BackgroundTasks
from google.oauth2.credentials import Credentials
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta, timezone, UTC
from zoneinfo import ZoneInfo
from enum import Enum

from sqlalchemy.orm import Session

from .. import utils
from ..defines import REDIS_REMOTE_EVENTS_KEY, DATEFMT, DEFAULT_CALENDAR_COLOUR
from .apis.google_client import GoogleClient
from ..database.models import CalendarProvider, BookingStatus
from ..database import schemas, models, repo
from ..controller.mailer import Attachment
from ..exceptions.calendar import TestConnectionFailed
from ..exceptions.validation import RemoteCalendarConnectionError
from ..l10n import l10n
from ..tasks.emails import send_invite_email, send_pending_email, send_rejection_email

class RemoteEventState(Enum):
    CANCELLED = 'CANCELLED'
    TENTATIVE = 'TENTATIVE'
    CONFIRMED = 'CONFIRMED'

class BaseConnector:
    redis_instance: Redis | RedisCluster | None
    subscriber_id: int
    calendar_id: int

    def __init__(self, subscriber_id: int, calendar_id: int | None, redis_instance: Redis | RedisCluster | None = None):
        self.redis_instance = redis_instance
        self.subscriber_id = subscriber_id
        self.calendar_id = calendar_id

    def obscure_key(self, key):
        """Obscure part of a key with our encryption algo"""
        return utils.setup_encryption_engine().encrypt(key)

    def get_key_body(self, only_subscriber=False):
        parts = [self.obscure_key(self.subscriber_id)]
        if not only_subscriber:
            parts.append(self.obscure_key(self.calendar_id))

        return ':'.join(parts)

    def get_cached_events(self, key_scope):
        """Retrieve any cached events, else returns None if redis is not available or there's no cache."""
        if self.redis_instance is None:
            return None

        key_scope = self.obscure_key(key_scope)

        timer_boot = time.perf_counter_ns()

        encrypted_events = self.redis_instance.get(f'{REDIS_REMOTE_EVENTS_KEY}:{self.get_key_body()}:{key_scope}')
        if encrypted_events is None:
            sentry_sdk.set_measurement('redis_get_miss_time', time.perf_counter_ns() - timer_boot, 'nanosecond')
            return None

        sentry_sdk.set_measurement('redis_get_hit_time', time.perf_counter_ns() - timer_boot, 'nanosecond')

        return [schemas.Event.model_load_redis(blob) for blob in json.loads(encrypted_events)]

    def put_cached_events(
        self,
        key_scope,
        events: list[schemas.Event],
        expiry=os.getenv('REDIS_EVENT_EXPIRE_SECONDS', 900)
    ):
        """Sets the passed cached events with an option to set a custom expiry time."""
        if self.redis_instance is None:
            return False

        key_scope = self.obscure_key(key_scope)
        timer_boot = time.perf_counter_ns()

        encrypted_events = json.dumps([event.model_dump_redis() for event in events])
        self.redis_instance.set(
            f'{REDIS_REMOTE_EVENTS_KEY}:{self.get_key_body()}:{key_scope}', value=encrypted_events, ex=expiry
        )
        sentry_sdk.set_measurement('redis_put_time', time.perf_counter_ns() - timer_boot, 'nanosecond')

        return True

    def bust_cached_events(self, all_calendars=False):
        """Delete cached events for a specific subscriber/calendar.
        Optionally pass in all_calendars to remove all cached calendar events for a specific subscriber."""
        if self.redis_instance is None:
            return False

        timer_boot = time.perf_counter_ns()

        # Scan returns a tuple like: (Cursor start, [...keys found])
        ret = self.redis_instance.scan(
            0, f'{REDIS_REMOTE_EVENTS_KEY}:{self.get_key_body(only_subscriber=all_calendars)}:*'
        )

        if len(ret[1]) == 0:
            return False

        # Expand the list in position 1, which is a list of keys found from the scan
        self.redis_instance.delete(*ret[1])

        sentry_sdk.set_measurement('redis_bust_time', time.perf_counter_ns() - timer_boot, 'nanosecond')

        return True


class GoogleConnector(BaseConnector):
    """Generic interface for Google Calendar REST API.
    This should match CaldavConnector (except for the constructor).
    """

    def __init__(
        self,
        subscriber_id,
        calendar_id,
        redis_instance,
        db,
        remote_calendar_id,
        google_client: GoogleClient,
        google_tkn: str = None,
    ):
        super().__init__(subscriber_id, calendar_id, redis_instance)

        self.db = db
        self.google_client = google_client
        self.provider = CalendarProvider.google
        self.remote_calendar_id = remote_calendar_id
        self.google_token = None
        # Create the creds class from our token (requires a refresh token)
        if google_tkn:
            self.google_token = Credentials.from_authorized_user_info(json.loads(google_tkn), self.google_client.SCOPES)

    def get_busy_time(self, calendar_ids: list, start: str, end: str):
        """Retrieve a list of { start, end } dicts that will indicate busy time for a user
        Note: This does not use the remote_calendar_id from the class,
        all calendars must be available under the google_token provided to the class"""
        time_min = datetime.strptime(start, DATEFMT).isoformat() + 'Z'
        time_max = datetime.strptime(end, DATEFMT).isoformat() + 'Z'

        results = []
        for calendars in utils.chunk_list(calendar_ids, chunk_by=5):
            results += self.google_client.get_free_busy(calendars, time_min, time_max, self.google_token)
        return results

    def test_connection(self) -> bool:
        """This occurs during Google OAuth login"""
        return bool(self.google_token)

    def sync_calendars(self):
        """Sync google calendars"""

        # We only support google right now!
        self.google_client.sync_calendars(db=self.db, subscriber_id=self.subscriber_id, token=self.google_token)
        # We should refresh any events we might have for every calendar
        self.bust_cached_events(all_calendars=True)

    def list_calendars(self):
        """find all calendars on the remote server"""
        calendars = []
        remote_calendars = self.google_client.list_calendars(self.google_token)
        for c in remote_calendars:
            calendars.append(
                schemas.CalendarConnectionOut(
                    title=c.summary,
                    url=str(c.id),
                    user=c.id,
                )
            )

        return calendars

    def list_events(self, start, end):
        """find all events in given date range on the remote server"""
        cache_scope = f'{start}_{end}'
        cached_events = self.get_cached_events(cache_scope)
        if cached_events:
            return cached_events

        time_min = datetime.strptime(start, DATEFMT).isoformat() + 'Z'
        time_max = datetime.strptime(end, DATEFMT).isoformat() + 'Z'

        # We're storing google cal id in user...for now.
        remote_events = self.google_client.list_events(self.remote_calendar_id, time_min, time_max, self.google_token)

        events = []
        for event in remote_events:
            # If the event doesn't have transparency assume its opaque (and thus blocks time) by default.
            transparency = event.get('transparency', 'opaque').lower()
            status = event.get('status').lower()

            # Ignore cancelled events or non-time blocking events
            if status == 'cancelled' or transparency == 'transparent':
                continue

            # Grab the attendee list for marking tentative events / filtering out declined events
            attendees = event.get('attendees') or []
            declined = any(
                (attendee.get('self') and attendee.get('responseStatus') == 'declined') for attendee in attendees
            )

            # Don't show declined events
            if declined:
                continue

            # Mark tentative events
            tentative = any(
                (attendee.get('self') and attendee.get('responseStatus') == 'tentative') for attendee in attendees
            )

            summary = event.get('summary', 'Title not found!')
            description = event.get('description', '')

            all_day = 'date' in event.get('start')

            start = (
                datetime.strptime(event.get('start')['date'], DATEFMT)
                if all_day
                else datetime.fromisoformat(event.get('start')['dateTime'])
            )
            end = (
                datetime.strptime(event.get('end')['date'], DATEFMT)
                if all_day
                else datetime.fromisoformat(event.get('end')['dateTime'])
            )

            events.append(
                schemas.Event(
                    title=summary,
                    start=start,
                    end=end,
                    all_day=all_day,
                    tentative=tentative,
                    description=description,
                )
            )

        self.put_cached_events(cache_scope, events)

        return events

    def save_event(
        self,
        event: schemas.Event,
        attendee: schemas.AttendeeBase,
        organizer: schemas.Subscriber,
        organizer_email: str,
    ) -> schemas.Event:
        """add a new event to the connected calendar"""

        description = [event.description]

        # Place url and phone in desc if available:
        if event.location.url:
            description.append(l10n('join-online', {'url': event.location.url}))

        if event.location.phone:
            description.append(l10n('join-phone', {'phone': event.location.phone}))

        body = {
            'iCalUID': event.uuid.hex,
            'summary': event.title,
            'location': event.location.url if event.location.url else None,
            'description': '\n'.join(description),
            'start': {'dateTime': event.start.isoformat()},
            'end': {'dateTime': event.end.isoformat()},
            'attendees': [
                {'displayName': organizer.name, 'email': organizer_email, 'responseStatus': 'accepted'},
                {'displayName': attendee.name, 'email': attendee.email, 'responseStatus': 'accepted'},
            ],
            'organizer': {
                'displayName': organizer.name,
                'email': self.remote_calendar_id,
            },
        }

        new_event = self.google_client.save_event(
            calendar_id=self.remote_calendar_id,
            body=body,
            token=self.google_token
        )

        # Fill in the external_id so we can delete events later!
        event.external_id = new_event.get('id')

        self.bust_cached_events()

        return event

    def delete_event(self, uid: str):
        """Delete remote event of given external_id
        """
        self.google_client.delete_event(calendar_id=self.remote_calendar_id, event_id=uid, token=self.google_token)
        self.bust_cached_events()

    def delete_events(self, start):
        """delete all events in given date range from the server
        Not intended to be used in production. For cleaning purposes after testing only.
        """
        pass


class CalDavConnector(BaseConnector):
    def __init__(
        self,
        db: Session,
        subscriber_id: int,
        calendar_id: int,
        redis_instance,
        url: str,
        user: str,
        password: str
    ):
        super().__init__(subscriber_id, calendar_id, redis_instance)

        self.db = db
        self.provider = CalendarProvider.caldav
        self.url = url
        self.password = password
        self.user = user

        # connect to the CalDAV server
        self.client = DAVClient(url=self.url, username=self.user, password=self.password)

    def get_busy_time(self, calendar_ids: list, start: str, end: str):
        """Retrieve a list of { start, end } dicts that will indicate busy time for a user
        Note: This does not use the remote_calendar_id from the class"""
        time_min = datetime.strptime(start, DATEFMT)
        time_max = datetime.strptime(end, DATEFMT)

        perf_start = time.perf_counter_ns()

        calendar = self.client.calendar(url=calendar_ids[0])
        response = calendar.freebusy_request(time_min, time_max)

        perf_end = time.perf_counter_ns()
        print(f"CALDAV FreeBusy response: {(perf_end - perf_start) / 1000000000} seconds")


        items = []

        # This is sort of dumb, freebusy object isn't exposed in the icalendar instance except through a list of tuple
        # props; luckily the value is a vPeriod which is a tuple of date times/timedelta (0 = Start, 1 = End)
        for prop in response.icalendar_instance.property_items():
            if prop[0].lower() != 'freebusy':
                continue

            # Tuple of start datetime and end datetime (or timedelta!)
            period = prop[1].dt
            items.append({
                'start': period[0],
                'end': period[1] if isinstance(period[1], datetime) else period[0] + period[1]
            })

        return items

    def test_connection(self) -> bool:
        """Ensure the connection information is correct and the calendar connection works"""

        supports_vevent = False

        try:
            cals = self.client.principal()
            for cal in cals.calendars():
                supported_comps = cal.get_supported_components()
                supports_vevent = 'VEVENT' in supported_comps
                # If one supports it, then that's good enough!
                if supports_vevent:
                    break
        except IndexError as ex:
            # Library has an issue with top level urls, probably due to caldav spec?
            logging.error(f'IE: Error testing connection {ex}')
            raise TestConnectionFailed(reason=None)
        except KeyError as ex:
            logging.error(f'KE: Error testing connection {ex}')
            raise TestConnectionFailed(reason=None)
        except requests.exceptions.RequestException:
            raise TestConnectionFailed(reason=None)
        except NotImplementedError:
            # Doesn't support authorization by digest, bearer, or basic header values
            raise TestConnectionFailed(reason=l10n('remote-calendar-reason-doesnt-support-auth'))
        except (
            caldav.lib.error.NotFoundError,
            caldav.lib.error.PropfindError,
            caldav.lib.error.AuthorizationError
        ) as ex:
            """
            NotFoundError: Good server, bad url.
            PropfindError: Some properties could not be retrieved.
            AuthorizationError: Credentials are not accepted.
            """
            logging.error(f'Test Connection Error: {ex}')

            # Don't use the default "no reason" error message if we encounter it.
            if ex.reason == caldav.lib.error.DAVError.reason:
                ex.reason = None
            if ex.reason == 'Unauthorized':
                # ex.reason seems to be pulling from status codes for some errors?
                # Let's replace this with our own.
                ex.reason = l10n('remote-calendar-reason-unauthorized')

            raise TestConnectionFailed(reason=ex.reason)

        # They need at least VEVENT support for appointment to work.
        return supports_vevent

    def sync_calendars(self):
        error_occurred = False

        principal = self.client.principal()
        for cal in principal.calendars():
            # Does this calendar support vevents?
            supported_comps = cal.get_supported_components()

            if 'VEVENT' not in supported_comps:
                continue

            calendar = schemas.CalendarConnection(
                title=cal.name,
                url=str(cal.url),
                user=self.user,
                password=self.password,
                provider=CalendarProvider.caldav,
                color=DEFAULT_CALENDAR_COLOUR  # Pick a default colour for now!
            )

            # add calendar
            try:
                repo.calendar.update_or_create(
                    db=self.db, calendar=calendar, calendar_url=calendar.url, subscriber_id=self.subscriber_id
                )
            except Exception as err:
                logging.warning(
                    f'[calendar.sync_calendars] Error occurred while creating calendar. Error: {str(err)}'
                )
                error_occurred = True

        if not error_occurred:
            self.bust_cached_events(all_calendars=True)

        return error_occurred

    def list_calendars(self):
        """find all calendars on the remote server"""
        calendars = []
        principal = self.client.principal()
        for c in principal.calendars():
            calendars.append(
                schemas.CalendarConnectionOut(
                    title=c.name,
                    url=str(c.url),
                    user=self.user,
                )
            )
        return calendars

    def list_events(self, start, end):
        """find all events in given date range on the remote server"""
        cache_scope = f'{start}_{end}'
        cached_events = self.get_cached_events(cache_scope)
        if cached_events:
            return cached_events

        events = []
        calendar = self.client.calendar(url=self.url)
        result = calendar.search(
            start=datetime.strptime(start, DATEFMT),
            end=datetime.strptime(end, DATEFMT),
            event=True,
            expand=True,
        )
        for e in result:
            transparency = e.icalendar_component['transp'].lower() if 'transp' in e.icalendar_component else 'opaque'
            status = e.icalendar_component['status'].lower() if 'status' in e.icalendar_component else ''

            # Ignore cancelled events
            if status == 'cancelled' or transparency == 'transparent':
                continue

            vevent = e.vobject_instance.vevent
            if not vevent:
                continue

            event_components = vevent.components()

            # Ignore events with missing datetime data
            if 'dtstart' not in event_components or (
                'dtend' not in event_components and 'duration' not in event_components
            ):
                continue

            # Mark tentative events
            tentative = status == 'tentative'

            title = vevent.summary.value if 'summary' in event_components else l10n('event-summary-default')
            start = vevent.dtstart.value
            # get_duration grabs either end or duration into a timedelta
            end = start + e.get_duration()
            # if start doesn't hold time information (no datetime), it's a whole day
            all_day = not isinstance(start, datetime)

            events.append(
                schemas.Event(
                    title=title,
                    start=start,
                    end=end,
                    all_day=all_day,
                    tentative=tentative,
                    description=e.icalendar_component['description'] if 'description' in e.icalendar_component else '',
                )
            )

        self.put_cached_events(cache_scope, events)

        return events

    def save_event(
        self, event: schemas.Event, attendee: schemas.AttendeeBase, organizer: schemas.Subscriber, organizer_email: str
    ):
        """add a new event to the connected calendar"""
        calendar = self.client.calendar(url=self.url)
        # save event
        caldav_event = calendar.save_event(
            uid=event.uuid,
            dtstart=event.start,
            dtend=event.end,
            summary=event.title,
            # TODO: handle location
            description=event.description,
        )
        # save attendee data
        caldav_event.add_attendee((organizer.name, organizer_email))
        caldav_event.add_attendee((attendee.name, attendee.email))
        caldav_event.save()

        self.bust_cached_events()

        return event

    def delete_event(self, uid: str):
        """Delete remote event of given uid
        """
        event = self.client.calendar(url=self.url).event_by_uid(uid)
        event.delete()
        self.bust_cached_events()

    def delete_events(self, start):
        """delete all events in given date range from the server
        Not intended to be used in production. For cleaning purposes after testing only.
        """
        calendar = self.client.calendar(url=self.url)
        result = calendar.events()
        count = 0
        for e in result:
            if str(e.vobject_instance.vevent.dtstart.value).startswith(start):
                e.delete()
                count += 1

        self.bust_cached_events()

        return count


class Tools:
    def create_vevent(
        self,
        appointment: schemas.Appointment,
        slot: schemas.Slot,
        organizer: schemas.Subscriber,
        event_status = RemoteEventState.CONFIRMED.value,
    ):
        """create an event in ical format for .ics file creation"""
        cal = Calendar()
        cal.add('prodid', '-//Thunderbird Appointment//tba.dk//')
        cal.add('version', '2.0')
        cal.add('method', 'CANCEL' if event_status == RemoteEventState.CANCELLED.value else 'REQUEST')
        org = vCalAddress('MAILTO:' + organizer.preferred_email)
        org.params['cn'] = vText(organizer.preferred_email)
        org.params['role'] = vText('CHAIR')
        event = Event()
        event.add('uid', appointment.uuid.hex)
        event.add('summary', appointment.title)
        event.add('dtstart', slot.start.replace(tzinfo=timezone.utc))
        event.add(
            'dtend',
            slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration),
        )
        event.add('dtstamp', datetime.now(UTC))
        event.add('status', event_status)
        event['description'] = appointment.details
        event['organizer'] = org

        # Prefer the slot meeting link url over the appointment location url
        location_url = slot.meeting_link_url if slot.meeting_link_url is not None else appointment.location_url

        if location_url:
            event.add('location', location_url)

        cal.add_component(event)
        return cal.to_ical()


    def send_invitation_vevent(
        self,
        background_tasks: BackgroundTasks,
        appointment: models.Appointment,
        slot: schemas.Slot,
        organizer: schemas.Subscriber,
        attendee: schemas.AttendeeBase,
    ):
        """send a booking confirmation email to attendee with .ics file attached"""
        ics_file = Attachment(
            mime=('text', 'calendar'),
            filename='AppointmentInvite.ics',
            data=self.create_vevent(appointment, slot, organizer),
        )
        if attendee.timezone is None:
            attendee.timezone = 'UTC'
        date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(attendee.timezone))
        # Send mail
        background_tasks.add_task(
            send_invite_email,
            organizer.name,
            organizer.email,
            date=date,
            duration=slot.duration,
            to=attendee.email,
            attachment=ics_file
        )

    def send_hold_vevent(
        self,
        background_tasks: BackgroundTasks,
        appointment: models.Appointment,
        slot: schemas.Slot,
        organizer: schemas.Subscriber,
        attendee: schemas.AttendeeBase,
    ):
        """send a hold booking email to attendee with .ics file attached"""
        ics_file = Attachment(
            mime=('text', 'calendar'),
            filename='AppointmentInvite.ics',
            data=self.create_vevent(appointment, slot, organizer, RemoteEventState.TENTATIVE.value),
        )
        if attendee.timezone is None:
            attendee.timezone = 'UTC'
        date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(attendee.timezone))
        # Send mail
        background_tasks.add_task(
            send_pending_email,
            organizer.name,
            date=date,
            to=attendee.email,
            attachment=ics_file
        )

    def send_cancel_vevent(
        self,
        background_tasks: BackgroundTasks,
        appointment: models.Appointment,
        slot: schemas.Slot,
        organizer: schemas.Subscriber,
        attendee: schemas.AttendeeBase,
    ):
        """send a hold booking email to attendee with .ics file attached"""
        ics_file = Attachment(
            mime=('text', 'calendar'),
            filename='AppointmentInvite.ics',
            data=self.create_vevent(appointment, slot, organizer, RemoteEventState.CANCELLED.value),
        )
        if attendee.timezone is None:
            attendee.timezone = 'UTC'
        date = slot.start.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(attendee.timezone))
        # Send mail
        background_tasks.add_task(
            send_rejection_email,
            organizer.name,
            date=date,
            to=attendee.email,
            attachment=ics_file
        )


    @staticmethod
    def available_slots_from_schedule(schedule: models.Schedule) -> list[schemas.SlotBase]:
        """This helper calculates a list of slots according to the given schedule configuration."""
        slots = []

        now = datetime.now()

        subscriber = schedule.calendar.owner
        timezone = zoneinfo.ZoneInfo(subscriber.timezone)

        now_tz = datetime.now(tz=timezone)
        not_tz_midnight = now_tz.replace(hour=0, minute=0, second=0, microsecond=0)
        now_tz_total_seconds = now_tz.timestamp() - not_tz_midnight.timestamp()

        # Start and end time in the subscriber's timezone
        start_time_local = schedule.start_time_local
        end_time_local = schedule.end_time_local

        # FIXME: Currently the earliest booking acts in normal days, not within the scheduled days.
        # So if they have the schedule setup for weekdays, it will count weekends too.
        earliest_booking = now + timedelta(minutes=schedule.earliest_booking)
        # We add a day here because it should be inclusive of the final day.
        farthest_booking = now + timedelta(days=1, minutes=schedule.farthest_booking)

        schedule_start = max([datetime.combine(schedule.start_date, start_time_local), earliest_booking])
        schedule_end = (
            min([datetime.combine(schedule.end_date, end_time_local), farthest_booking])
            if schedule.end_date
            else farthest_booking
        )

        start_time = datetime.combine(now.min, start_time_local) - datetime.min
        end_time = datetime.combine(now.min, end_time_local) - datetime.min

        # Thanks to timezone conversion end_time can wrap around to the next day
        if start_time > end_time:
            end_time += timedelta(days=1)

        # All user defined weekdays, falls back to working week if invalid
        weekdays = schedule.weekdays if isinstance(schedule.weekdays, list) else json.loads(schedule.weekdays)
        if not weekdays or len(weekdays) == 0:
            weekdays = [1, 2, 3, 4, 5]

        # Difference of the start and end time.
        # Since our times are localized we start at 0, and go until we hit the diff.
        total_time = int(end_time.total_seconds()) - int(start_time.total_seconds())

        slot_duration_seconds = schedule.slot_duration * 60

        # Between the available booking time
        for ordinal in range(schedule_start.toordinal(), schedule_end.toordinal()):
            time_start = 0

            # If it's today and now is greater than our normal start time...
            if now_tz.toordinal() == ordinal and now_tz_total_seconds > start_time.total_seconds():
                # Note: This is in seconds!
                # Get the offset from now to 0:00:00, and adjust it so 0 aligns with our start_time.
                # (So if the date is today it's 9am, and our start time is also 9am then time_start should be 0)
                time_start = int(now_tz_total_seconds - start_time.total_seconds())

                # Round up to the nearest slot duration, I'm bad at math...
                # Get the remainder of the slow, subtract that from our time_start, then add the slot duration back in.
                time_start -= time_start % slot_duration_seconds
                time_start += slot_duration_seconds

            date = datetime.fromordinal(ordinal)
            current_datetime = datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_time_local.hour,
                minute=start_time_local.minute,
                tzinfo=timezone,
            )
            # Check if this weekday is within our schedule
            if current_datetime.isoweekday() in weekdays:
                # Generate each timeslot based on the selected duration
                # We just loop through the difference of the start and end time and step by slot duration in seconds.
                slots += [
                    schemas.SlotBase(start=current_datetime + timedelta(seconds=time), duration=schedule.slot_duration)
                    for time in range(time_start, total_time, slot_duration_seconds)
                ]

        return slots

    @staticmethod
    def events_roll_up_difference(
        a_list: list[schemas.SlotBase], b_list: list[schemas.Event]
    ) -> list[schemas.SlotBase]:
        """This helper rolls up all events from list A, which have a time collision with any event in list B
        and returns all remaining elements from A as new list.
        """

        def is_blocker(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime):
            """
            if there is an overlap of both date ranges, a collision was found
            see https://en.wikipedia.org/wiki/De_Morgan%27s_laws
            """
            return a_start.timestamp() < b_end.timestamp() and a_end.timestamp() > b_start.timestamp()

        available_slots = []
        collisions = []

        for slot in a_list:
            slot_start = slot.start
            slot_end = slot.start + timedelta(minutes=slot.duration)

            # If any of the events are overlap the slot time...
            if any([is_blocker(slot_start, slot_end, event.start, event.end) for event in b_list]):
                previous_collision_end = (
                    collisions[-1].start + timedelta(minutes=collisions[-1].duration) if len(collisions) else None
                )

                # ...and the last item was a previous collision then extend the previous collision's duration
                if previous_collision_end and previous_collision_end.timestamp() == slot_start.timestamp():
                    collisions[-1].duration += slot.duration
                else:
                    # ...if the last item was a normal available time, then create a new collision
                    collisions.append(
                        schemas.SlotBase(start=slot_start, duration=slot.duration, booking_status=BookingStatus.booked)
                    )
            else:
                # ...Otherwise, just append the normal available time.
                available_slots.append(slot)

        # Append the two lists
        available_slots = available_slots + collisions

        # And sort!
        available_slots = sorted(available_slots, key=lambda slot: slot.start.timestamp())

        return available_slots

    @staticmethod
    def existing_events_for_schedule(
        schedule: models.Schedule,
        calendars: list[schemas.Calendar],
        subscriber: models.Subscriber,
        google_client: GoogleClient,
        db,
        redis=None,
    ) -> list[schemas.Event]:
        """This helper retrieves all events existing in given calendars for the scheduled date range"""
        existing_events = []
        google_calendars = []

        now = datetime.now()

        earliest_booking = now + timedelta(minutes=schedule.earliest_booking)
        farthest_booking = now + timedelta(minutes=schedule.farthest_booking)

        start = max([datetime.combine(schedule.start_date, schedule.start_time), earliest_booking])
        end = (
            min([datetime.combine(schedule.end_date, schedule.end_time), farthest_booking])
            if schedule.end_date
            else farthest_booking
        )

        # handle calendar events
        for calendar in calendars:
            if calendar.provider == CalendarProvider.google:
                google_calendars.append(calendar)
            else:
                # Caldav - We don't have a smart way to batch these right now so just call them 1 by 1
                con = CalDavConnector(
                    db=db,
                    redis_instance=redis,
                    url=calendar.url,
                    user=calendar.user,
                    password=calendar.password,
                    subscriber_id=subscriber.id,
                    calendar_id=calendar.id,
                )

                try:
                    existing_events.extend([
                        schemas.Event(
                            start=busy.get('start'),
                            end=busy.get('end'),
                            title='Busy'
                        ) for busy in
                        con.get_busy_time([calendar.url], start.strftime(DATEFMT), end.strftime(DATEFMT))
                    ])

                    # We're good here, continue along the loop
                    continue
                except caldav.lib.error.ReportError:
                    logging.debug("[Tools.existing_events_for_schedule] CalDAV server does not support FreeBusy API.")
                    pass

                # Okay maybe this server doesn't support freebusy, try the old way
                try:
                    existing_events.extend(con.list_events(start.strftime(DATEFMT), end.strftime(DATEFMT)))
                except requests.exceptions.ConnectionError:
                    # Connection error with remote caldav calendar, don't crash this route.
                    pass

        # Batch up google calendar calls since we can only have one google calendar connected
        if len(google_calendars) > 0 and google_calendars[0].provider == CalendarProvider.google:
            external_connection = utils.list_first(
                repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google)
            )
            if external_connection is None or external_connection.token is None:
                raise RemoteCalendarConnectionError()

            con = GoogleConnector(
                db=db,
                redis_instance=redis,
                google_client=google_client,
                remote_calendar_id=google_calendars[0].user,  # This isn't used for get_busy_time but is still needed.
                calendar_id=google_calendars[0].id,  # This isn't used for get_busy_time but is still needed.
                subscriber_id=subscriber.id,
                google_tkn=external_connection.token,
            )
            existing_events.extend([
                schemas.Event(
                    start=busy.get('start'),
                    end=busy.get('end'),
                    title='Busy'
                ) for busy in con.get_busy_time(
                    [calendar.user for calendar in google_calendars],
                    start.strftime(DATEFMT),
                    end.strftime(DATEFMT)
                )
            ])

        # handle already requested time slots
        for slot in schedule.slots:
            existing_events.append(
                schemas.Event(
                    title=schedule.name,
                    start=slot.start,
                    end=slot.start + timedelta(minutes=slot.duration),
                )
            )

        return existing_events

    @staticmethod
    def dns_caldav_lookup(url, secure=True):
        import dns.resolver

        secure_character = 's' if secure else ''
        dns_url = f'_caldav{secure_character}._tcp.{url}'
        path = ''

        # Check if they have a caldav subdomain, on error just return none
        try:
            records = dns.resolver.resolve(dns_url, 'SRV')
        except DNSException:
            return None, None

        # Check if they have any relative paths setup
        try:
            txt_records = dns.resolver.resolve(dns_url, 'TXT')

            for txt_record in txt_records:
                # Remove any quotes from the txt record
                txt_record = str(txt_record).replace('"', '')
                if txt_record.startswith('path='):
                    path = txt_record[5:]
        except DNSException:
            pass

        # Append a slash at the end if it's missing
        path += '' if path.endswith('/') else '/'

        # Grab the first item or None
        caldav_host = None
        port = 443 if secure else 80
        ttl = records.rrset.ttl or 300
        if len(records) > 0:
            port = str(records[0].port)
            caldav_host = str(records[0].target)[:-1]

            # Service not provided
            if caldav_host == ".":
                return None, None

        if '://' in caldav_host:
            # Remove any protocols first!
            caldav_host.replace('http://', '').replace('https://', '')

        # We should only be pulling the secure link
        caldav_host = f'http{secure_character}://{caldav_host}:{port}{path}'

        return caldav_host, ttl

    @staticmethod
    def well_known_caldav_lookup(url: str) -> str|None:
        parsed_url = urlparse(url)

        # Do they have a well-known?
        if parsed_url.path == '' and parsed_url.hostname != '':
            try:
                response = requests.get(urljoin(url, '/.well-known/caldav'), allow_redirects=False)
                if response.is_redirect:
                    redirect = response.headers.get('Location')
                    if redirect:
                        # Fastmail really needs that ending slash
                        return redirect if redirect.endswith('/') else redirect + '/'
            except requests.exceptions.ConnectionError:
                # Ignore connection errors here
                pass
        return None

    @staticmethod
    def fix_caldav_urls(url: str) -> str:
        """Fix up some common url issues with some caldav providers"""
        parsed_url = urlparse(url)

        # If for some reason we don't have a hostname, there's nothing to fix
        # and we just throw back that weird url
        if not parsed_url.hostname:
            return url

        # Handle any fastmail issues
        if parsed_url.hostname.endswith('fastmail.com'):
            if not parsed_url.path.startswith('/dav'):
                url = f'{url}/dav/'

            # Url needs to end with slash
            if not url.endswith('/'):
                url += '/'

        # Google is weird - We also don't support them right now.
        elif (
            parsed_url.hostname.endswith('api.googlecontent.com')
            or parsed_url.hostname.endswith('apidata.googleusercontent.com')
        ):
            if len(parsed_url.path) == 0:
                url += '/caldav/v2/'
        elif parsed_url.hostname.endswith('.calendar.google.com'):
            # Use the caldav url instead
            url = 'https://api.googlecontent.com/caldav/v2/'

        return url

    @staticmethod
    def default_event_title(slot: schemas.Slot, owner: schemas.Subscriber, prefix='') -> str:
        """Builds a default event title for scheduled bookings
           The prefix can be used e.g. for "HOLD: " events
        """
        attendee_name = slot.attendee.name if slot.attendee.name is not None else slot.attendee.email
        owner_name = owner.name if owner.name is not None else owner.email
        return l10n('event-title-template', { 'prefix': prefix, 'name1': owner_name, 'name2': attendee_name })
