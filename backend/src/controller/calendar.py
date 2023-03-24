"""Module: caldav

Handle connection to a CalDAV server.
"""
import os
import smtplib, ssl

from caldav import DAVClient
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, date, timedelta
from ..database import schemas
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class CalDavConnector:
  def __init__(self, url: str, user: str, password: str):
    # store credentials of remote location
    self.url = url
    self.user = user
    self.password = password
    # connect to CalDAV server
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
    calendar = self.client.calendar(url=self.url)
    result = calendar.search(
      start=datetime.strptime(start, '%Y-%m-%d'),
      end=datetime.strptime(end, '%Y-%m-%d'),
      event=True,
      expand=True
    )
    events = []
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
    event.add('dtstart', slot.start)
    event.add('dtend', slot.start + timedelta(minutes=slot.duration))
    event.add('dtstamp', datetime.now())
    event['description'] = appointment.details
    event['organizer'] = org
    cal.add_component(event)
    return cal.to_ical()

  def send_vevent(self, appointment: schemas.Appointment, slot: schemas.Slot, organizer: schemas.Subscriber, attendee: schemas.AttendeeBase):
    """send a booking confirmation email to attendee with .ics file attached"""
    # create mail header
    message = MIMEMultipart()
    message['Subject'] = 'multipart test'
    message['From'] = organizer.email
    message['To'] = attendee.email
    # add content as text and html
    message.attach(MIMEText('This message is sent from Appointment.', 'plain'))
    message.attach(MIMEText('<html><body><p>This message is sent from <b>Appointment</b>.</p></body></html>', 'html'))
    # create attachment
    part = MIMEBase('text', 'calendar')
    filename = 'invite.ics'

    part.set_payload(self.create_vevent(appointment, slot, organizer))
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    message.attach(part)

    # get smtp configuration
    SMTP_SECURITY = os.getenv('SMTP_SECURITY', 'NONE')
    SMTP_URL      = os.getenv('SMTP_URL', 'localhost')
    SMTP_PORT     = os.getenv('SMTP_PORT', 25)
    SMTP_USER     = os.getenv('SMTP_USER')
    SMTP_PASS     = os.getenv('SMTP_PASS')

    try:
      # if configured, create a secure SSL context
      if SMTP_SECURITY == 'SSL':
        server = smtplib.SMTP_SSL(SMTP_URL, SMTP_PORT, context=ssl.create_default_context())
        server.login(SMTP_USER, STMP_PASS)
      elif SMTP_SECURITY == 'STARTTLS':
        server = smtplib.SMTP(SMTP_URL, SMTP_PORT)
        server.starttls(context=ssl.create_default_context())
        server.login(SMTP_USER, STMP_PASS)
      # fall back to non-secure
      else:
        server = smtplib.SMTP(SMTP_URL, SMTP_PORT)
      # now send email
      server.sendmail(organizer.email, attendee.email, message.as_string())
    except Exception as e:
      print(e)
    finally:
      server.quit() 
