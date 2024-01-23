"""Module: caldav

Handle connection to a CalDAV server.
"""
import json

import caldav.lib.error
import requests
from caldav import DAVClient
from google.oauth2.credentials import Credentials
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta, timezone, UTC
from zoneinfo import ZoneInfo
from dateutil.parser import parse

from .apis.google_client import GoogleClient
from ..database import schemas, models
from ..database.models import CalendarProvider
from ..controller.mailer import Attachment, InvitationMail
from ..l10n import l10n

DATEFMT = "%Y-%m-%d"


class GoogleConnector:
    """Generic interface for Google Calendar REST API.
       This should match CaldavConnector (except for the constructor).
    """

    def __init__(
        self,
        db,
        google_client: GoogleClient,
        calendar_id,
        subscriber_id,
        google_tkn: str = None,
    ):
        # store credentials of remote location
        self.db = db
        self.google_client = google_client
        self.provider = CalendarProvider.google
        self.calendar_id = calendar_id
        self.subscriber_id = subscriber_id
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
        time_min = datetime.strptime(start, DATEFMT).isoformat() + "Z"
        time_max = datetime.strptime(end, DATEFMT).isoformat() + "Z"

        # We're storing google cal id in user...for now.
        remote_events = self.google_client.list_events(self.calendar_id, time_min, time_max, self.google_token)

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

            start = event.get("start")["date"] if all_day else event.get("start")["dateTime"]
            end = event.get("end")["date"] if all_day else event.get("end")["dateTime"]

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

        return events

    def create_event(
        self,
        event: schemas.Event,
        attendee: schemas.AttendeeBase,
        organizer: schemas.Subscriber,
    ):
        """add a new event to the connected calendar"""

        description = [event.description]

        # Place url and phone in desc if available:
        if event.location.url:
            description.append(l10n('join-online', {'url': event.location.url}))

        if event.location.phone:
            description.append(l10n('join-phone', {'phone': event.location.phone}))

        body = {
            "summary": event.title,
            "location": event.location.name,
            "description": "\n".join(description),
            "start": {"dateTime": event.start},
            "end": {"dateTime": event.end},
            "attendees": [
                {"displayName": organizer.name, "email": organizer.email},
                {"displayName": attendee.name, "email": attendee.email},
            ],
        }
        self.google_client.create_event(calendar_id=self.calendar_id, body=body, token=self.google_token)
        return event

    def delete_events(self, start):
        """delete all events in given date range from the server
           Not intended to be used in production. For cleaning purposes after testing only.
        """
        pass


class CalDavConnector:
    def __init__(self, url: str, user: str, password: str):
        # store credentials of remote location
        self.provider = CalendarProvider.caldav
        self.url = url
        self.user = user
        self.password = password
        # connect to CalDAV server
        self.client = DAVClient(url=url, username=user, password=password)

    def test_connection(self) -> bool:
        """Ensure the connection information is correct and the calendar connection works"""
        cal = self.client.calendar(url=self.url)

        try:
            supported_comps = cal.get_supported_components()
        except IndexError:  # Library has an issue with top level urls, probably due to caldav spec?
            return False
        except requests.exceptions.RequestException:  # Max retries exceeded, bad connection, missing schema, etc...
            return False
        except caldav.lib.error.NotFoundError:  # Good server, bad url.
            return False

        # They need at least VEVENT support for appointment to work.
        return 'VEVENT' in supported_comps

    def sync_calendars(self):
        pass

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
                    title=str(e.vobject_instance.vevent.summary.value),
                    start=str(e.vobject_instance.vevent.dtstart.value),
                    end=str(e.vobject_instance.vevent.dtend.value),
                    all_day=not isinstance(e.vobject_instance.vevent.dtstart.value, datetime),
                    tentative=tentative,
                    description=e.icalendar_component["description"] if "description" in e.icalendar_component else "",
                )
            )
        return events

    def create_event(
        self,
        event: schemas.Event,
        attendee: schemas.AttendeeBase,
        organizer: schemas.Subscriber,
    ):
        """add a new event to the connected calendar"""
        calendar = self.client.calendar(url=self.url)
        # save event
        caldavEvent = calendar.save_event(
            dtstart=datetime.fromisoformat(event.start),
            dtend=datetime.fromisoformat(event.end),
            summary=event.title,
            # TODO: handle location
            description=event.description,
        )
        # save attendee data
        caldavEvent.add_attendee((organizer.name, organizer.email))
        caldavEvent.add_attendee((attendee.name, attendee.email))
        caldavEvent.save()
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
        return count


class Tools:
    def create_vevent(
        self,
        appointment: schemas.Appointment | schemas.AppointmentBase,
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
        appointment: schemas.Appointment | schemas.AppointmentBase,
        slot: schemas.Slot,
        organizer: schemas.Subscriber,
        attendee: schemas.AttendeeBase,
    ):
        """send a booking confirmation email to attendee with .ics file attached"""
        invite = Attachment(
            mime=("text", "calendar"),
            filename="invite.ics",
            data=self.create_vevent(appointment, slot, organizer),
        )
        mail = InvitationMail(to=attendee.email, attachments=[invite])
        mail.send()

    @staticmethod
    def available_slots_from_schedule(s: models.Schedule) -> list[schemas.SlotBase]:
        """This helper calculates a list of slots according to the given schedule configuration."""
        slots = []

        now = datetime.now()

        # FIXME: Currently the earliest booking acts in normal days, not within the scheduled days.
        # So if they have the schedule setup for weekdays, it will count weekends too.
        earliest_booking = now + timedelta(minutes=s.earliest_booking)
        # We add a day here because it should be inclusive of the final day.
        farthest_booking = now + timedelta(days=1, minutes=s.farthest_booking)

        schedule_start = max([datetime.combine(s.start_date, s.start_time), earliest_booking])
        schedule_end = min([datetime.combine(s.end_date, s.end_time), farthest_booking]) if s.end_date else farthest_booking

        start_time = datetime.combine(now.min, s.start_time) - datetime.min
        end_time = datetime.combine(now.min, s.end_time) - datetime.min

        # Thanks to timezone conversion end_time can wrap around to the next day
        if start_time > end_time:
            end_time += timedelta(days=1)

        # All user defined weekdays, falls back to working week if invalid
        weekdays = s.weekdays if type(s.weekdays) == list else json.loads(s.weekdays)
        if not weekdays or len(weekdays) == 0:
            weekdays = [1, 2, 3, 4, 5]

        # Between the available booking time
        for ordinal in range(schedule_start.toordinal(), schedule_end.toordinal()):
            date = datetime.fromordinal(ordinal)
            current_datetime = datetime(year=date.year, month=date.month, day=date.day)
            # Check if this weekday is within our schedule
            if current_datetime.isoweekday() in weekdays:
                # Generate each timeslot based on the selected duration
                # We just loop through the start and end time and step by slot duration in seconds.
                slots += [
                    schemas.SlotBase(start=current_datetime + timedelta(seconds=time), duration=s.slot_duration)
                    for time in range(int(start_time.total_seconds()), int(end_time.total_seconds()), s.slot_duration * 60)
                ]

        return slots

    def events_set_difference(a_list: list[schemas.SlotBase], b_list: list[schemas.Event]) -> list[schemas.SlotBase]:
        """This helper removes all events from list A, which have a time collision with any event in list B
           and returns all remaining elements from A as new list.
        """
        available_slots = []
        for a in a_list:
            a_start = a.start
            a_end = a_start + timedelta(minutes=a.duration)
            collision_found = False
            for b in b_list:
                b_start = parse(b.start)
                b_end = parse(b.end)
                # if there is an overlap of both date ranges, a collision was found
                # see https://en.wikipedia.org/wiki/De_Morgan%27s_laws
                if a_start.timestamp() < b_end.timestamp() and a_end.timestamp() > b_start.timestamp():
                    collision_found = True
                    break
            if not collision_found:
                available_slots.append(a)
        return available_slots

    def existing_events_for_schedule(
        schedule: schemas.Schedule,
        calendars: list[schemas.Calendar],
        subscriber: schemas.Subscriber,
        google_client: GoogleClient,
        db
    ) -> list[schemas.Event]:
        """This helper retrieves all events existing in given calendars for the scheduled date range
        """
        existingEvents = []
        # handle calendar events
        for calendar in calendars:
            if calendar.provider == CalendarProvider.google:
                con = GoogleConnector(
                    db=db,
                    google_client=google_client,
                    calendar_id=calendar.user,
                    subscriber_id=subscriber.id,
                    google_tkn=subscriber.google_tkn,
                )
            else:
                con = CalDavConnector(calendar.url, calendar.user, calendar.password)
            farthest_end = datetime.now(UTC) + timedelta(minutes=schedule.farthest_booking)
            start = schedule.start_date.strftime(DATEFMT)
            end = schedule.end_date.strftime(DATEFMT) if schedule.end_date else farthest_end.strftime(DATEFMT)
            existingEvents.extend(con.list_events(start, end))
        # handle already requested time slots
        for slot in schedule.slots:
            existingEvents.append(schemas.Event(
                title=schedule.name,
                start=slot.start.isoformat(),
                end=(slot.start + timedelta(minutes=slot.duration)).isoformat(),
            ))
        return existingEvents
