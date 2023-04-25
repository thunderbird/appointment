"""Module: caldav

Handle connection to a CalDAV server.
"""
import enum
import os.path
from caldav import DAVClient
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, date, timedelta, timezone
from ..database import schemas
from ..database.models import CalendarProvider
from ..controller.mailer import Attachment, InvitationMail

SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalDavConnector:
  def __init__(self, provider: int, url: str, user: str, password: str):
    # store credentials of remote location
    self.provider = provider
    self.url = url
    self.user = user
    self.password = password
    # connect to CalDAV server
    if provider == CalendarProvider.google:
      # https://developers.google.com/calendar/api/quickstart/python
      TOKEN_PATH = './src/tmp/test.json' # TODO
      creds = None
      # The file token.json stores the user's access and refresh tokens, and is
      # created automatically when the authorization flow completes for the first time.
      if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
      # If there are no (valid) credentials available, let the user log in.
      if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
        # else:
        #   flow = InstalledAppFlow.from_client_secrets_file('./google_credentials.json', SCOPES)
        #   creds = flow.run_local_server(port=0)
        # # Save the credentials for the next run
        # with open(TOKEN_PATH, 'w') as token:
        #   token.write(creds.to_json())
      try:
        self.client = build('calendar', 'v3', credentials=creds)
      except HttpError as error:
        print('An error occurred: %s' % error)

    if provider == CalendarProvider.caldav:
      # https://github.com/python-caldav/caldav/blob/master/examples/basic_usage_examples.py
      self.client = DAVClient(url=url, username=user, password=password)


  def list_calendars(self):
    """find all calendars on the remote server"""
    calendars = []
    principal = self.client.principal()
    for c in principal.calendars():
      calendars.append(schemas.CalendarConnectionOut(
        title=c.name,
        url=str(c.url),
        user=self.user,
      ))
    return calendars


  def list_events(self, start, end):
    """find all events in given date range on the remote server"""
    events = []
    if self.provider == CalendarProvider.google:
      result = self.client.events().list(
        calendarId=self.user,
        timeMin=datetime.strptime(start, '%Y-%m-%d').isoformat() + 'Z',
        timeMax=datetime.strptime(end, '%Y-%m-%d').isoformat() + 'Z',
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
      ).execute()
      for e in result.get('items', []):
        events.append(schemas.Event(
          title=e['summary'],
          start=e['start']['date'] if 'date' in e['start'] else e['start']['dateTime'],
          end=e['end']['date'] if 'date' in e['end'] else e['end']['dateTime'],
          all_day='date' in e['start'],
          description=e['description'] if 'description' in e else ''
        ))
    if self.provider == CalendarProvider.caldav:
      calendar = self.client.calendar(url=self.url)
      result = calendar.search(
        start=datetime.strptime(start, '%Y-%m-%d'),
        end=datetime.strptime(end, '%Y-%m-%d'),
        event=True,
        expand=True
      )
      for e in result:
        events.append(schemas.Event(
          title=str(e.vobject_instance.vevent.summary.value),
          start=str(e.vobject_instance.vevent.dtstart.value),
          end=str(e.vobject_instance.vevent.dtend.value),
          all_day=not isinstance(e.vobject_instance.vevent.dtstart.value, datetime),
          description=e.icalendar_component['description'] if 'description' in e.icalendar_component else ''
        ))
    return events


  def create_event(self, event: schemas.Event, attendee: schemas.AttendeeBase):
    """add a new event to the connected calendar"""
    calendar = self.client.calendar(url=self.url)
    # save event
    caldavEvent = calendar.save_event(
      dtstart=datetime.fromisoformat(event.start),
      dtend=datetime.fromisoformat(event.end),
      summary=event.title,
      description=event.description
    )
    # TODO: add organizer data
    # save attendee data
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
  def create_vevent(self, appointment: schemas.Appointment, slot: schemas.Slot, organizer: schemas.Subscriber):
    """create an event in ical format for .ics file creation"""
    cal = Calendar()
    cal.add('prodid', '-//Thunderbird Appointment//tba.dk//')
    cal.add('version', '2.0')
    org = vCalAddress('MAILTO:' + organizer.email)
    org.params['cn'] = vText(organizer.name)
    org.params['role'] = vText('CHAIR')
    event = Event()
    event.add('summary', appointment.title)
    event.add('dtstart', slot.start.replace(tzinfo=timezone.utc))
    event.add('dtend', slot.start.replace(tzinfo=timezone.utc) + timedelta(minutes=slot.duration))
    event.add('dtstamp', datetime.utcnow())
    event['description'] = appointment.details
    event['organizer'] = org
    cal.add_component(event)
    return cal.to_ical()


  def send_vevent(self, appointment: schemas.Appointment, slot: schemas.Slot, organizer: schemas.Subscriber, attendee: schemas.AttendeeBase):
    """send a booking confirmation email to attendee with .ics file attached"""
    invite = Attachment(
      mime=('text', 'calendar'),
      filename='invite.ics',
      data=self.create_vevent(appointment, slot, organizer)
    )
    mail = InvitationMail(sender=organizer.email, to=attendee.email, attachments=[invite])
    mail.send()
