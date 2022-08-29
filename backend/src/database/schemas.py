"""Module: schemas

Definitions of valid data shapes for database models.
"""
from pydantic import BaseModel
from .models import AppointmentStatus


""" SLOT model schemas
"""
class SlotBase(BaseModel):
  start: str
  is_available: bool | None = True


class Slot(SlotBase):
  id: int
  appointment_id: int

  class Config:
    orm_mode = True


""" APPOINTMENT model schemas
"""
class AppointmentBase(BaseModel):
  time_created: str | None = None
  time_updated: str | None = None
  duration: int
  title: str
  location_suggestions: str | None = None
  location_selected: str | None = None
  location_name: str | None = None
  location_url: str | None = None
  location_phone: str | None = None
  details: str | None = None
  attendees: str | None = None
  slug: str
  status: AppointmentStatus | None = AppointmentStatus.draft


class Appointment(AppointmentBase):
  id: int
  calendar_id: int
  slots: list[Slot] = []

  class Config:
    orm_mode = True


""" CALENDAR model schemas
"""
class CalendarBase(BaseModel):
  url: str
  user: str
  password: str


class Calendar(CalendarBase):
  id: int
  owner_id: int
  appointments: list[Appointment] = []

  class Config:
    orm_mode = True


""" SUBSCRIBER model schemas
"""
class SubscriberBase(BaseModel):
  username: str
  email: str
  name: str | None = None
  level: int | None = 1
  timezone: int | None = None


class Subscriber(SubscriberBase):
  id: int
  calendars: list[Calendar] = []

  class Config:
    orm_mode = True
