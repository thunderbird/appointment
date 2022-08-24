"""Module: schemas

Definitions of valid data shapes for database models.
"""
from pydantic import BaseModel


""" CALENDAR model schemas
"""
class CalendarBase(BaseModel):
  url: str
  user: str
  password: str


class CalendarCreate(CalendarBase):
  pass


class Calendar(CalendarBase):
  id: int
  owner_id: int

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


class SubscriberCreate(SubscriberBase):
  pass


class Subscriber(SubscriberBase):
  id: int
  calendars: list[Calendar] = []

  class Config:
    orm_mode = True
