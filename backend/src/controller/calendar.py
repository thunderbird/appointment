"""Module: caldav

Handle connection to a CalDAV server.
"""
import enum
from caldav import DAVClient
from gcsa.google_calendar import GoogleCalendar
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, date, timedelta, timezone
from ..database import schemas
from ..controller.mailer import Attachment, InvitationMail


class CalDavProvider(enum.Enum):
  general = 1
  google  = 2


class CalDavConnector:
  def __init__(self, url: str, user: str, password: str):
    # store credentials of remote location
    self.url = url
    self.user = user
    self.password = password
    provider = CalDavProvider.google if user.endswith('gmail.com') else CalDavProvider.general
    self.provider = provider
    # connect to CalDAV server
    if provider == CalDavProvider.google:
      # https://google-calendar-simple-api.readthedocs.io/en/latest/authentication.html
      self.client = GoogleCalendar(credentials_path='./google_credentials.json', save_token=False) # TODO handle tokens
    else:
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
    if self.provider == CalDavProvider.google:
      result = self.client.get_events(
        datetime.strptime(start, '%Y-%m-%d'),
        datetime.strptime(end, '%Y-%m-%d'),
        order_by='startTime'
      )
      for e in result:
        print(e) # TODO
    else:
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
