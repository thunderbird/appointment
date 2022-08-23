from pydantic import BaseModel


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


class SubscriberBase(BaseModel):
  username: str
  email: str
  name: str | None = None
  level: int
  timezone: int | None = None


class SubscriberCreate(SubscriberBase):
  pass


class Subscriber(SubscriberBase):
  id: int
  calendars: list[Calendar] = []

  class Config:
    orm_mode = True
