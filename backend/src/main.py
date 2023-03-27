"""Module: main

Boot application, authenticate user and provide all API endpoints.
"""
import os
import validators

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi_auth0 import Auth0User
from datetime import timedelta, datetime
from tempfile import NamedTemporaryFile

# load any available .env into env
load_dotenv()

# database
from sqlalchemy.orm import Session
from .database import repo, models, schemas
from .database.database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

# authentication
from .controller.auth import Auth
from .controller.calendar import CalDavConnector, Tools
auth = Auth()

# init app
app = FastAPI()

# allow requests from own frontend running on a different port
app.add_middleware(
  CORSMiddleware,
  # Work around for now :)
  allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:8080')],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

def get_db():
  """run database session"""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


@app.get("/")
def health():
  """Small route with no processing that will be used for health checks"""
  return {}


@app.get("/login", dependencies=[Depends(auth.auth0.implicit_scheme)])
def login(db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to check frontend authed user and create user if not existing yet"""
  persisted_user = auth.persist_user(db, user)
  if not persisted_user or not auth.subscriber:
    raise HTTPException(status_code=403, detail="User credentials mismatch")
  return persisted_user


@app.get("/me/calendars", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=list[schemas.CalendarOut])
def read_my_calendars(db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """get all calendar connections of authenticated subscriber"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  calendars = repo.get_calendars_by_subscriber(db, subscriber_id=auth.subscriber.id)
  return [schemas.CalendarOut(id=c.id, title=c.title, color=c.color) for c in calendars]


@app.get("/me/appointments", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=list[schemas.Appointment])
def read_my_appointments(db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """get all appointments of authenticated subscriber"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  appointments = repo.get_appointments_by_subscriber(db, subscriber_id=auth.subscriber.id)
  return appointments


@app.post("/cal", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.CalendarOut)
def create_my_calendar(calendar: schemas.CalendarConnection, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to add a new calendar connection for authenticated subscriber"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  calendars = repo.get_calendars_by_subscriber(db, subscriber_id=auth.subscriber.id)
  limit = repo.get_connections_limit(db=db, subscriber_id=auth.subscriber.id)
  # check for connection limit
  if limit > 0 and len(calendars) >= limit:
    raise HTTPException(status_code=403, detail="Maximum number of calendar connections reached")
  cal = repo.create_subscriber_calendar(db=db, calendar=calendar, subscriber_id=auth.subscriber.id)
  return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color)


@app.get("/cal/{id}", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.CalendarConnectionOut)
def read_my_calendar(id: int, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to get a calendar from db"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  cal = repo.get_calendar(db, calendar_id=id)
  if cal is None:
    raise HTTPException(status_code=404, detail="Calendar not found")
  if not repo.calendar_is_owned(db, calendar_id=id, subscriber_id=auth.subscriber.id):
    raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
  return schemas.CalendarConnectionOut(id=cal.id, title=cal.title, color=cal.color, url=cal.url, user=cal.user)


@app.put("/cal/{id}", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.CalendarOut)
def update_my_calendar(id: int, calendar: schemas.CalendarConnection, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to update an existing calendar connection for authenticated subscriber"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  if not repo.calendar_exists(db, calendar_id=id):
    raise HTTPException(status_code=404, detail="Calendar not found")
  if not repo.calendar_is_owned(db, calendar_id=id, subscriber_id=auth.subscriber.id):
    raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
  cal = repo.update_subscriber_calendar(db=db, calendar=calendar, calendar_id=id)
  return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color)


@app.delete("/cal/{id}", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.CalendarOut)
def delete_my_calendar(id: int, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to remove a calendar from db"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  if not repo.calendar_exists(db, calendar_id=id):
    raise HTTPException(status_code=404, detail="Calendar not found")
  if not repo.calendar_is_owned(db, calendar_id=id, subscriber_id=auth.subscriber.id):
    raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
  cal = repo.delete_subscriber_calendar(db=db, calendar_id=id)
  return schemas.CalendarOut(id=cal.id, title=cal.title, color=cal.color)


@app.post("/rmt/calendars", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=list[schemas.CalendarConnectionOut])
def read_caldav_calendars(connection: schemas.CalendarConnection, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to get calendars from a remote CalDAV server"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  con = CalDavConnector(connection.url, connection.user, connection.password)
  return con.list_calendars()


@app.get("/rmt/cal/{id}/{start}/{end}", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=list[schemas.Event])
def read_caldav_events(id: int, start: str, end: str, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to get events in a given date range from a remote calendar"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  db_calendar = repo.get_calendar(db, calendar_id=id)
  if db_calendar is None:
    raise HTTPException(status_code=404, detail="Calendar not found")
  con = CalDavConnector(db_calendar.url, db_calendar.user, db_calendar.password)
  events = con.list_events(start, end)
  for e in events:
    e.calendar_title = db_calendar.title
    e.calendar_color = db_calendar.color
  return events


@app.post("/apmt", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.Appointment)
def create_my_calendar_appointment(a_s: schemas.AppointmentSlots, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to add a new appointment with slots for a given calendar"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  if not repo.calendar_exists(db, calendar_id=a_s.appointment.calendar_id):
    raise HTTPException(status_code=404, detail="Calendar not found")
  if not repo.calendar_is_owned(db, calendar_id=a_s.appointment.calendar_id, subscriber_id=auth.subscriber.id):
    raise HTTPException(status_code=403, detail="Calendar not owned by subscriber")
  return repo.create_calendar_appointment(db=db, appointment=a_s.appointment, slots=a_s.slots)


@app.get("/apmt/{id}", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.Appointment)
def read_my_appointment(id: str, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to get an appointment from db by id"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  db_appointment = repo.get_appointment(db, appointment_id=id)
  if db_appointment is None:
    raise HTTPException(status_code=404, detail="Appointment not found")
  if not repo.appointment_is_owned(db, appointment_id=id, subscriber_id=auth.subscriber.id):
    raise HTTPException(status_code=403, detail="Appointment not owned by subscriber")
  return db_appointment


@app.put("/apmt/{id}", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.Appointment)
def update_my_appointment(id: int, a_s: schemas.AppointmentSlots, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to update an existing appointment with slots"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  db_appointment = repo.get_appointment(db, appointment_id=id)
  if db_appointment is None:
    raise HTTPException(status_code=404, detail="Appointment not found")
  if not repo.appointment_is_owned(db, appointment_id=id, subscriber_id=auth.subscriber.id):
    raise HTTPException(status_code=403, detail="Appointment not owned by subscriber")
  return repo.update_calendar_appointment(db=db, appointment=a_s.appointment, slots=a_s.slots, appointment_id=id)


@app.delete("/apmt/{id}", dependencies=[Depends(auth.auth0.implicit_scheme)], response_model=schemas.Appointment)
def delete_my_appointment(id: int, db: Session = Depends(get_db), user: Auth0User = Security(auth.auth0.get_user)):
  """endpoint to remove an appointment from db"""
  if not auth.subscriber:
    raise HTTPException(status_code=401, detail="No valid authentication credentials provided")
  db_appointment = repo.get_appointment(db, appointment_id=id)
  if db_appointment is None:
    raise HTTPException(status_code=404, detail="Appointment not found")
  if not repo.appointment_is_owned(db, appointment_id=id, subscriber_id=auth.subscriber.id):
    raise HTTPException(status_code=403, detail="Appointment not owned by subscriber")
  return repo.delete_calendar_appointment(db=db, appointment_id=id)


@app.get("/apmt/public/{slug}", response_model=schemas.AppointmentOut)
def read_public_appointment(slug: str, db: Session = Depends(get_db)):
  """endpoint to retrieve an appointment from db via public link and only expose necessary data"""
  a = repo.get_public_appointment(db, slug=slug)
  s = repo.get_subscriber_by_appointment(db=db, appointment_id=a.id)
  if a is None or s is None:
    raise HTTPException(status_code=404, detail="Appointment not found")
  slots = [schemas.SlotOut(id=sl.id, start=sl.start, duration=sl.duration, attendee_id=sl.attendee_id) for sl in a.slots]
  return schemas.AppointmentOut(id=a.id, title=a.title, details=a.details, slug=a.slug, owner_name=s.name, slots=slots)


@app.put("/apmt/public/{slug}", response_model=schemas.SlotAttendee)
def update_public_appointment_slot(slug: str, s_a: schemas.SlotAttendee, db: Session = Depends(get_db)):
  """endpoint to update a time slot for an appointment via public link and create an event in remote calendar"""
  db_appointment = repo.get_public_appointment(db, slug=slug)
  if db_appointment is None:
    raise HTTPException(status_code=404, detail="Appointment not found")
  db_calendar = repo.get_calendar(db, calendar_id=db_appointment.calendar_id)
  if db_calendar is None:
    raise HTTPException(status_code=404, detail="Calendar not found")
  if not repo.appointment_has_slot(db, appointment_id=db_appointment.id, slot_id=s_a.slot_id):
    raise HTTPException(status_code=404, detail="Time slot not found for Appointment")
  if not repo.slot_is_available(db, slot_id=s_a.slot_id):
    raise HTTPException(status_code=403, detail="Time slot not available anymore")
  if not validators.email(s_a.attendee.email):
    raise HTTPException(status_code=400, detail="No valid email required")
  slot = repo.get_slot(db=db, slot_id=s_a.slot_id)
  event = schemas.Event(
    title=db_appointment.title,
    start=slot.start.isoformat(),
    end=(slot.start + timedelta(minutes=slot.duration)).isoformat(),
    description=db_appointment.details
  )
  # create remote event
  con = CalDavConnector(db_calendar.url, db_calendar.user, db_calendar.password)
  con.create_event(event=event, attendee=s_a.attendee)
  # update appointment slot data
  repo.update_slot(db=db, slot_id=s_a.slot_id, attendee=s_a.attendee)
  # send mail with .ics attachment to attendee
  organizer = repo.get_subscriber_by_appointment(db=db, appointment_id=db_appointment.id)
  Tools().send_vevent(db_appointment, slot, organizer, s_a.attendee)
  return schemas.SlotAttendee(slot_id=s_a.slot_id, attendee=s_a.attendee)


@app.get("/serve/ics/{slug}/{slot_id}", response_model=schemas.FileDownload)
def serve_ics(slug: str, slot_id: int, db: Session = Depends(get_db)):
  """endpoint to serve ICS file for time slot to download"""
  db_appointment = repo.get_public_appointment(db, slug=slug)
  if db_appointment is None:
    raise HTTPException(status_code=404, detail="Appointment not found")
  if not repo.appointment_has_slot(db, appointment_id=db_appointment.id, slot_id=slot_id):
    raise HTTPException(status_code=404, detail="Time slot not found for Appointment")
  slot = repo.get_slot(db=db, slot_id=slot_id)
  if slot is None:
    raise HTTPException(status_code=404, detail="Time slot not found")
  organizer = repo.get_subscriber_by_appointment(db=db, appointment_id=db_appointment.id)
  return schemas.FileDownload(
    name="invite",
    content_type="text/calendar",
    data=Tools().create_vevent(appointment=db_appointment, slot=slot, organizer=organizer).decode("utf-8")
  )
