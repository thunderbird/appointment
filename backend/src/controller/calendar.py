"""Module: caldav

Handle connection to a CalDAV server.
"""
import json
from caldav import DAVClient
from google.oauth2.credentials import Credentials
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, date, timedelta, timezone

from .google import GoogleClient
from ..database import schemas, repo
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
            status = event.get("status")

            # Ignore cancelled events
            if status == "cancelled":
                continue

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
    def __init__(self, provider: int, url: str, user: str, password: str, google_tkn: str = None):
        # store credentials of remote location
        self.provider = provider
        self.url = url
        self.user = user
        self.password = password
        self.google_token = google_tkn
        # connect to CalDAV server
        if provider == CalendarProvider.google:
            raise DeprecationWarning()

        if provider == CalendarProvider.caldav:
            # https://github.com/python-caldav/caldav/blob/master/examples/basic_usage_examples.py
            self.client = DAVClient(url=url, username=user, password=password)

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
        if self.provider == CalendarProvider.google:
            result = (
                self.client.events()
                .list(
                    calendarId=self.user,
                    timeMin=datetime.strptime(start, "%Y-%m-%d").isoformat() + "Z",
                    timeMax=datetime.strptime(end, "%Y-%m-%d").isoformat() + "Z",
                    maxResults=1000,  # TODO
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            for e in result.get("items", []):
                events.append(
                    schemas.Event(
                        title=e["summary"],
                        start=e["start"]["date"] if "date" in e["start"] else e["start"]["dateTime"],
                        end=e["end"]["date"] if "date" in e["end"] else e["end"]["dateTime"],
                        all_day="date" in e["start"],
                        description=e["description"] if "description" in e else "",
                    )
                )
        if self.provider == CalendarProvider.caldav:
            calendar = self.client.calendar(url=self.url)
            result = calendar.search(
                start=datetime.strptime(start, "%Y-%m-%d"),
                end=datetime.strptime(end, "%Y-%m-%d"),
                event=True,
                expand=True,
            )
            for e in result:
                events.append(
                    schemas.Event(
                        title=str(e.vobject_instance.vevent.summary.value),
                        start=str(e.vobject_instance.vevent.dtstart.value),
                        end=str(e.vobject_instance.vevent.dtend.value),
                        all_day=not isinstance(e.vobject_instance.vevent.dtstart.value, datetime),
                        description=e.icalendar_component["description"]
                        if "description" in e.icalendar_component
                        else "",
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
        if self.provider == CalendarProvider.google:
            googleEvent = {
                "summary": event.title,
                # 'location': event.location_url, # TODO handle location types
                "description": event.description,
                "start": {"dateTime": event.start + "+00:00"},
                "end": {"dateTime": event.end + "+00:00"},
                "attendees": [{"displaName": attendee.name, "email": attendee.email}],
            }
            self.client.events().insert(calendarId=self.user, body=googleEvent).execute()
        if self.provider == CalendarProvider.caldav:
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
