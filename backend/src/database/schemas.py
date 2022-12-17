"""Module: schemas

Definitions of valid data shapes for database and query models.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from .models import SubscriberLevel, AppointmentStatus, LocationType, random_slug


""" SLOT model schemas
"""
class SlotBase(BaseModel):
  start: datetime
  duration: int | None = None


class Slot(SlotBase):
  id: int
  appointment_id: int
  attendee_id: int | None = None
  subscriber_id: int | None = None
  time_updated: datetime | None = None

  class Config:
    orm_mode = True


""" ATTENDEE model schemas
"""
class AttendeeBase(BaseModel):
  email: str
  name: str | None = None


class Attendee(AttendeeBase):
  id: int
  slots: list[Slot] = []

  class Config:
    orm_mode = True


class SlotAttendee(BaseModel):
  slot_id: int
  attendee: AttendeeBase


""" APPOINTMENT model schemas
"""
class AppointmentBase(BaseModel):
  calendar_id: int
  title: str
  duration: int | None = None
  location_type: LocationType | None = LocationType.inperson
  location_suggestions: str | None = None
  location_selected: str | None = None
  location_name: str | None = None
  location_url: str | None = None
  location_phone: str | None = None
  details: str | None = None
  slug: str | None = Field(default_factory=random_slug)
  keep_open: bool | None = True
  status: AppointmentStatus | None = AppointmentStatus.draft


class Appointment(AppointmentBase):
  id: int
  time_created: datetime | None = None
  time_updated: datetime | None = None
  slots: list[Slot] = []

  class Config:
    orm_mode = True


""" CALENDAR model schemas
"""
class CalendarBase(BaseModel):
  title: str | None = None
  color: str | None = None

  
class CalendarConnection(CalendarBase):
  url: str
  user: str
  password: str


class Calendar(CalendarConnection):
  id: int
  owner_id: int
  appointments: list[Appointment] = []

  class Config:
    orm_mode = True


class CalendarOut(CalendarBase):
  id: int


""" SUBSCRIBER model schemas
"""
class SubscriberBase(BaseModel):
  username: str
  email: str
  name: str | None = None
  level: SubscriberLevel | None = SubscriberLevel.basic
  timezone: int | None = None


class Subscriber(SubscriberBase):
  id: int
  calendars: list[Calendar] = []
  slots: list[Slot] = []

  class Config:
    orm_mode = True


""" other schemas used for requests or data migration
"""
class AppointmentSlots(BaseModel):
  appointment: AppointmentBase
  slots: list[SlotBase] = []


class Event(BaseModel):
  title: str
  start: str
  end: str
  calendar_title: str | None = None
  calendar_color: str | None = None
