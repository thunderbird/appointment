"""Module: caldav

Handle connection to a CalDAV server.
"""
import json
import logging
from caldav import DAVClient
from google.oauth2.credentials import Credentials
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta, timezone

from .google_client import GoogleClient
from ..database import schemas
from ..database.models import CalendarProvider
from ..controller.mailer import Attachment, InvitationMail


class GoogleConnector:
    """Generic interface for Google Calendar REST API. This should match CaldavConnector (except for the constructor)"""

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
        # Create the creds class from our token (this requires a refresh token!!)
        self.google_token = Credentials.from_authorized_user_info(json.loads(google_tkn), self.google_client.SCOPES)

    def sync_calendars(self):
        """Sync our google calendars"""

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
        time_min = datetime.strptime(start, "%Y-%m-%d").isoformat() + "Z"
        time_max = datetime.strptime(end, "%Y-%m-%d").isoformat() + "Z"

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
            description.append(f"Join online at: {event.location.url}")

        if event.location.phone:
            description.append(f"Join by phone: {event.location.phone}")

        body = {
            "summary": event.title,
            "location": event.location.name,
            "description": "\n".join(description),
            "start": {"dateTime": event.start + "+00:00"},
            "end": {"dateTime": event.end + "+00:00"},
            "attendees": [
                {"displayName": organizer.name, "email": organizer.email},
                {"displayName": attendee.name, "email": attendee.email},
            ],
        }
        self.google_client.create_event(calendar_id=self.calendar_id, body=body, token=self.google_token)
        return event

    def delete_events(self, start):
        """delete all events in given date range from the server"""
        # Not used?
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
            start=datetime.strptime(start, "%Y-%m-%d"),
            end=datetime.strptime(end, "%Y-%m-%d"),
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
        """delete all events in given date range from the server"""
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
        event.add("summary", appointment.title)
        event.add("dtstart", slot.start.replace(tzinfo=timezone.utc))
        event.add(
            "dtend",
            slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration),
        )
        event.add("dtstamp", datetime.utcnow())
        event["description"] = appointment.details
        event["organizer"] = org
        cal.add_component(event)
        return cal.to_ical()

    def send_vevent(
        self,
        appointment: schemas.Appointment,
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
        mail = InvitationMail(sender=organizer.email, to=attendee.email, attachments=[invite])
        mail.send()

    def available_slots_from_schedule(s: schemas.ScheduleBase):
        """This helper calculates a list of slots according to the given schedule."""
        now = datetime.now()
        earliest_start = now + timedelta(minutes=s.earliest_booking)
        farthest_end = now + timedelta(minutes=s.farthest_booking)
        start = max([datetime.combine(s.start_date, s.start_time), earliest_start])
        end = min([datetime.combine(s.end_date, s.end_time), farthest_end])
        slots = []
        # set the first date to an allowed weekday
        weekdays = s.weekdays if type(s.weekdays) == list else json.loads(s.weekdays)
        if not weekdays or len(weekdays) == 0:
            weekdays = [1,2,3,4,5]
        while start.isoweekday() not in weekdays:
            start = start + timedelta(days=1)
        # init date generation: pointer holds the current slot start datetime
        pointer = start
        counter = 0
        # set fix event limit of 1000 for now for performance reasons. Can be removed later.
        while pointer < end and counter < 1000:
            counter += 1
            slots.append(schemas.SlotBase(start=pointer, duration=s.slot_duration))
            next_start = pointer + timedelta(minutes=s.slot_duration)
            # if the next slot still fits into the current day
            if next_start.time() < s.end_time:
                pointer = next_start
            # if the next slot has to be on the next available day
            else:
                next_date = datetime.combine(pointer.date() + timedelta(days=1), s.start_time)
                # check weekday and skip da if it isn't allowed
                while next_date.isoweekday() not in weekdays:
                    next_date = next_date + timedelta(days=1)
                pointer = next_date
        return slots

    def events_set_difference(a: list[schemas.SlotBase], b: list[schemas.SlotBase]):
        """This helper removes all events from list A, which have a time collision with any event in list B
        and returns all remaining elements from A as new list.
        """
        # TODO: implement A-B
        return a
