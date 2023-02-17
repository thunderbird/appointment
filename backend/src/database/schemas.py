"""Module: schemas

Definitions of valid data shapes for database and query models.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from .models import SubscriberLevel, AppointmentStatus, LocationType, random_slug


""" ATTENDEE model schemas
"""
class AttendeeBase(BaseModel):
  email: str
  name: str | None = None


class Attendee(AttendeeBase):
  id: int

  class Config:
    orm_mode = True


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
  attendee: Attendee | None = None

  class Config:
    orm_mode = True


class SlotAttendee(BaseModel):
  slot_id: int
  attendee: AttendeeBase


""" APPOINTMENT model schemas
"""
class AppointmentBase(BaseModel):
  title: str
  details: str | None = None
  slug: str | None = Field(default_factory=random_slug)


class AppointmentFull(AppointmentBase):
  calendar_id: int
  duration: int | None = None
  location_type: LocationType | None = LocationType.inperson
  location_suggestions: str | None = None
  location_selected: str | None = None
  location_name: str | None = None
  location_url: str | None = None
  location_phone: str | None = None
  keep_open: bool | None = True
  status: AppointmentStatus | None = AppointmentStatus.draft


class Appointment(AppointmentFull):
  id: int
  time_created: datetime | None = None
  time_updated: datetime | None = None
  slots: list[Slot] = []

  class Config:
    orm_mode = True


class AppointmentOut(AppointmentBase):
  id: int
  owner_name: str | None = None
  slots: list[SlotBase] = []


""" CALENDAR model schemas
"""
class CalendarBase(BaseModel):
  title: str | None = None
  color: str | None = None


class CalendarConnectionOut(CalendarBase):
  url: str
  user: str


class CalendarConnection(CalendarConnectionOut):
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
  appointment: AppointmentFull
  slots: list[SlotBase] = []


class Event(BaseModel):
  title: str
  start: str
  end: str
  all_day: bool | None = False
  description: str | None = None
  calendar_title: str | None = None
  calendar_color: str | None = None
