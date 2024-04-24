"""Module: caldav

Handle connection to a CalDAV server.
"""
import json
import logging
import uuid
import zoneinfo
import os

import caldav.lib.error
import requests
from redis import Redis
from caldav import DAVClient
from fastapi import BackgroundTasks
from google.oauth2.credentials import Credentials
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta, timezone, UTC

from .. import utils
from ..defines import REDIS_REMOTE_EVENTS_KEY, DATEFMT
from .apis.google_client import GoogleClient
from ..database.models import CalendarProvider, BookingStatus
from ..database import schemas, models, repo
from ..controller.mailer import Attachment
from ..exceptions.validation import RemoteCalendarConnectionError
from ..l10n import l10n
from ..tasks.emails import send_invite_email


class BaseConnector:
    redis_instance: Redis | None
    subscriber_id: int
    calendar_id: int

    def __init__(self, subscriber_id: int, calendar_id: int | None, redis_instance: Redis | None = None):
        self.redis_instance = redis_instance
        self.subscriber_id = subscriber_id
        self.calendar_id = calendar_id

    def obscure_key(self, key):
        """Obscure part of a key with our encryption algo"""
        return utils.setup_encryption_engine().encrypt(key)

    def get_key_body(self, only_subscriber = False):
        parts = [self.obscure_key(self.subscriber_id)]
        if not only_subscriber:
            parts.append(self.obscure_key(self.calendar_id))

        return ":".join(parts)

    def get_cached_events(self, key_scope):
        """Retrieve any cached events, else returns None if redis is not available or there's no cache."""
        if self.redis_instance is None:
            return None

        key_scope = self.obscure_key(key_scope)

        encrypted_events = self.redis_instance.get(f'{REDIS_REMOTE_EVENTS_KEY}:{self.get_key_body()}:{key_scope}')
        if encrypted_events is None:
            return None

        return [schemas.Event.model_load_redis(blob) for blob in json.loads(encrypted_events)]

    def put_cached_events(self, key_scope, events: list[schemas.Event], expiry=os.getenv('REDIS_EVENT_EXPIRE_SECONDS')):
        """Sets the passed cached events with an option to set a custom expiry time."""
        if self.redis_instance is None:
            return False

        key_scope = self.obscure_key(key_scope)

        encrypted_events = json.dumps([event.model_dump_redis() for event in events])
        self.redis_instance.set(f'{REDIS_REMOTE_EVENTS_KEY}:{self.get_key_body()}:{key_scope}',
                                value=encrypted_events, ex=expiry)

        return True

    def bust_cached_events(self, all_calendars = False):
        """Delete cached events for a specific subscriber/calendar. 
        Optionally pass in all_calendars to remove all cached calendar events for a specific subscriber."""
        if self.redis_instance is None:
            return False

        # Scan returns a tuple like: (Cursor start, [...keys found])
        ret = self.redis_instance.scan(0, f'{REDIS_REMOTE_EVENTS_KEY}:{self.get_key_body(only_subscriber=all_calendars)}:*')

        if len(ret[1]) == 0:
            return False

        # Expand the list in position 1, which is a list of keys found from the scan
        self.redis_instance.delete(*ret[1])

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
        cache_scope = f"{start}_{end}"
        cached_events = self.get_cached_events(cache_scope)
        if cached_events:
            return cached_events

        time_min = datetime.strptime(start, DATEFMT).isoformat() + "Z"
        time_max = datetime.strptime(end, DATEFMT).isoformat() + "Z"

        # We're storing google cal id in user...for now.
        remote_events = self.google_client.list_events(self.remote_calendar_id, time_min, time_max, self.google_token)

        events = []
        for event in remote_events:
            status = event.get("status").lower()

            # Ignore cancelled events
            if status == "cancelled":
                continue

            # Mark tentative events
            attendees = event.get("attendees") or []
            tentative = any(
                (attendee.get("self") and attendee.get("responseStatus") == "tentative") for attendee in attendees
            )

            summary = event.get("summary", "Title not found!")
            description = event.get("description", "")

            all_day = "date" in event.get("start")

            start = datetime.strptime(event.get("start")["date"], DATEFMT) if all_day else datetime.fromisoformat(
                event.get("start")["dateTime"])
            end = datetime.strptime(event.get("end")["date"], DATEFMT) if all_day else datetime.fromisoformat(
                event.get("end")["dateTime"])

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

    def create_event(
        self,
        event: schemas.Event,
        attendee: schemas.AttendeeBase,
        organizer: schemas.Subscriber,
        organizer_email: str,
    ):
        """add a new event to the connected calendar"""

        description = [event.description]

        # Place url and phone in desc if available:
        if event.location.url:
            description.append(l10n('join-online', {'url': event.location.url}))

        if event.location.phone:
            description.append(l10n('join-phone', {'phone': event.location.phone}))

        body = {
            "iCalUID": event.uuid.hex,
            "summary": event.title,
            "location": event.location.name,
            "description": "\n".join(description),
            "start": {"dateTime": event.start.isoformat()},
            "end": {"dateTime": event.end.isoformat()},
            "attendees": [
                {"displayName": organizer.name, "email": organizer_email},
                {"displayName": attendee.name, "email": attendee.email},
            ],
            "organizer": {
                "displayName": organizer.name,
                "email": self.remote_calendar_id,
            }
        }
        self.google_client.create_event(calendar_id=self.remote_calendar_id, body=body, token=self.google_token)

        self.bust_cached_events()

        return event

    def delete_events(self, start):
        """delete all events in given date range from the server
           Not intended to be used in production. For cleaning purposes after testing only.
        """
        pass


class CalDavConnector(BaseConnector):
    def __init__(self, subscriber_id: int, calendar_id: int, redis_instance, url: str, user: str, password: str):
        super().__init__(subscriber_id, calendar_id, redis_instance)

        self.provider = CalendarProvider.caldav
        self.url = url
        self.password = password
        self.user = user
        # connect to CalDAV server
        self.client = DAVClient(url=url, username=user, password=password)

    def test_connection(self) -> bool:
        """Ensure the connection information is correct and the calendar connection works"""

        try:
            cal = self.client.calendar(url=self.url)
            supported_comps = cal.get_supported_components()
        except IndexError as ex:  # Library has an issue with top level urls, probably due to caldav spec?
            logging.error(f"Error testing connection {ex}")
            return False
        except KeyError as ex:
            logging.error(f"Error testing connection {ex}")
            return False
        except requests.exceptions.RequestException:  # Max retries exceeded, bad connection, missing schema, etc...
            return False
        except caldav.lib.error.NotFoundError:  # Good server, bad url.
            return False

        # They need at least VEVENT support for appointment to work.
        return 'VEVENT' in supported_comps

    def sync_calendars(self):
        # We don't sync anything for caldav, but might as well bust event cache.
        self.bust_cached_events(all_calendars=True)

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
        cache_scope = f"{start}_{end}"
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
            status = e.icalendar_component["status"].lower() if "status" in e.icalendar_component else ""

            # Ignore cancelled events
            if status == "cancelled":
                continue

            # Mark tentative events
            tentative = status == "tentative"

            events.append(
                schemas.Event(
                    title=e.vobject_instance.vevent.summary.value,
                    start=e.vobject_instance.vevent.dtstart.value,
                    end=e.vobject_instance.vevent.dtend.value,
                    all_day=not isinstance(e.vobject_instance.vevent.dtstart.value, datetime),
                    tentative=tentative,
                    description=e.icalendar_component["description"] if "description" in e.icalendar_component else "",
                )
            )

        self.put_cached_events(cache_scope, events)

        return events

    def create_event(
        self,
        event: schemas.Event,
        attendee: schemas.AttendeeBase,
        organizer: schemas.Subscriber,
        organizer_email: str
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
    ):
        """create an event in ical format for .ics file creation"""
        cal = Calendar()
        cal.add("prodid", "-//Thunderbird Appointment//tba.dk//")
        cal.add("version", "2.0")
        org = vCalAddress("MAILTO:" + organizer.email)
        org.params["cn"] = vText(organizer.name)
        org.params["role"] = vText("CHAIR")
        event = Event()
        event.add("uid", appointment.uuid.hex)
        event.add("summary", appointment.title)
        event.add("dtstart", slot.start.replace(tzinfo=timezone.utc))
        event.add(
            "dtend",
            slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration),
        )
        event.add("dtstamp", datetime.now(UTC))
        event["description"] = appointment.details
        event["organizer"] = org

        # Prefer the slot meeting link url over the appointment location url
        location_url = slot.meeting_link_url if slot.meeting_link_url is not None else appointment.location_url

        if location_url != "" or location_url is not None:
            event.add('location', location_url)

        cal.add_component(event)
        return cal.to_ical()

    def send_vevent(
        self,
        background_tasks: BackgroundTasks,
        appointment: models.Appointment,
        slot: schemas.Slot,
        organizer: schemas.Subscriber,
        attendee: schemas.AttendeeBase,
    ):
        """send a booking confirmation email to attendee with .ics file attached"""
        invite = Attachment(
            mime=("text", "calendar"),
            filename="AppointmentInvite.ics",
            data=self.create_vevent(appointment, slot, organizer),
        )
        background_tasks.add_task(send_invite_email, to=attendee.email, attachment=invite)

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
        schedule_end = min([datetime.combine(schedule.end_date, end_time_local),
                            farthest_booking]) if schedule.end_date else farthest_booking

        start_time = datetime.combine(now.min, start_time_local) - datetime.min
        end_time = datetime.combine(now.min, end_time_local) - datetime.min

        # Thanks to timezone conversion end_time can wrap around to the next day
        if start_time > end_time:
            end_time += timedelta(days=1)

        # All user defined weekdays, falls back to working week if invalid
        weekdays = schedule.weekdays if type(schedule.weekdays) is list else json.loads(schedule.weekdays)
        if not weekdays or len(weekdays) == 0:
            weekdays = [1, 2, 3, 4, 5]

        # Difference of the start and end time. Since our times are localized we start at 0, and go until we hit the diff.
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
                time_start -= (time_start % slot_duration_seconds)
                time_start += slot_duration_seconds

            date = datetime.fromordinal(ordinal)
            current_datetime = datetime(year=date.year, month=date.month, day=date.day, hour=start_time_local.hour,
                                        minute=start_time_local.minute, tzinfo=timezone)
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
    def events_roll_up_difference(a_list: list[schemas.SlotBase], b_list: list[schemas.Event]) -> list[
        schemas.SlotBase]:
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
                previous_collision_end = collisions[-1].start + timedelta(minutes=collisions[-1].duration) if len(collisions) else None

                # ...and the last item was a previous collision then extend the previous collision's duration
                if previous_collision_end and previous_collision_end.timestamp() == slot_start.timestamp():
                    collisions[-1].duration += slot.duration
                else:
                    # ...if the last item was a normal available time, then create a new collision
                    collisions.append(schemas.SlotBase(
                        start=slot_start,
                        duration=slot.duration,
                        booking_status=BookingStatus.booked
                    ))
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
        redis = None
    ) -> list[schemas.Event]:
        """This helper retrieves all events existing in given calendars for the scheduled date range
        """
        existing_events = []

        # handle calendar events
        for calendar in calendars:
            if calendar.provider == CalendarProvider.google:
                external_connection = utils.list_first(repo.external_connection.get_by_type(db, subscriber.id, schemas.ExternalConnectionType.google))

                if external_connection is None or external_connection.token is None:
                    raise RemoteCalendarConnectionError()

                con = GoogleConnector(
                    db=db,
                    redis_instance=redis,
                    google_client=google_client,
                    remote_calendar_id=calendar.user,
                    calendar_id=calendar.id,
                    subscriber_id=subscriber.id,
                    google_tkn=external_connection.token,
                )
            else:
                con = CalDavConnector(
                    redis_instance=redis,
                    url=calendar.url,
                    user=calendar.user,
                    password=calendar.password,
                    subscriber_id=subscriber.id,
                    calendar_id=calendar.id,
                )

            now = datetime.now()

            earliest_booking = now + timedelta(minutes=schedule.earliest_booking)
            farthest_booking = now + timedelta(minutes=schedule.farthest_booking)

            start = max([datetime.combine(schedule.start_date, schedule.start_time), earliest_booking])
            end = min([datetime.combine(schedule.end_date, schedule.end_time),
                       farthest_booking]) if schedule.end_date else farthest_booking

            try:
                existing_events.extend(con.list_events(start.strftime(DATEFMT), end.strftime(DATEFMT)))
            except requests.exceptions.ConnectionError:
                # Connection error with remote caldav calendar, don't crash this route.
                pass

        # handle already requested time slots
        for slot in schedule.slots:
            existing_events.append(schemas.Event(
                title=schedule.name,
                start=slot.start,
                end=slot.start + timedelta(minutes=slot.duration),
            ))

        return existing_events
