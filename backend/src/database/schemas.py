"""Module: schemas

Definitions of valid data shapes for database and query models.
"""
from datetime import datetime, date, time
from pydantic import BaseModel, Field
from .models import (
    SubscriberLevel,
    AppointmentStatus,
    LocationType,
    CalendarProvider,
    DayOfWeek,
    random_slug,
)


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
    attendee_id: int | None = None


class Slot(SlotBase):
    id: int
    appointment_id: int
    subscriber_id: int | None = None
    time_updated: datetime | None = None
    attendee: Attendee | None = None

    class Config:
        orm_mode = True


class SlotOut(SlotBase):
    id: int | None = None


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
    id: int | None = None
    owner_name: str | None = None
    slots: list[SlotOut] = []


""" SCHEDULE model schemas
"""


class AvailabilityBase(BaseModel):
    schedule_id: int
    day_of_week: DayOfWeek
    start_time: datetime | None = None
    end_time: datetime | None = None
    min_time_before_meeting: int
    slot_duration: int | None = None


class Availability(AvailabilityBase):
    id: int
    time_created: datetime | None = None
    time_updated: datetime | None = None

    class Config:
        orm_mode = True


class ScheduleBase(BaseModel):
    name: str
    calendar_id: int
    location_type: LocationType | None = LocationType.inperson
    location_url: str | None = None
    details: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    earliest_booking: int | None = None
    farthest_booking: int | None = None
    weekdays: list[int] | None = [1,2,3,4,5]
    slot_duration: int | None = None

    class Config:
        json_encoders = {
            time: lambda t: t.strftime("%H:%M"),
        }


class Schedule(ScheduleBase):
    id: int
    time_created: datetime | None = None
    time_updated: datetime | None = None
    availabilities: list[Availability] = []

    class Config:
        orm_mode = True


""" CALENDAR model schemas
"""


class CalendarBase(BaseModel):
    title: str | None = None
    color: str | None = None
    connected: bool | None = None


class CalendarConnectionOut(CalendarBase):
    provider: CalendarProvider | None = CalendarProvider.caldav
    url: str
    user: str


class CalendarConnection(CalendarConnectionOut):
    password: str


class Calendar(CalendarConnection):
    id: int
    owner_id: int
    appointments: list[Appointment] = []
    schedules: list[Schedule] = []

    class Config:
        orm_mode = True


class CalendarOut(CalendarBase):
    id: int


""" SUBSCRIBER model schemas
"""


class SubscriberIn(BaseModel):
    timezone: str | None = None
    username: str
    name: str | None = None


class SubscriberBase(SubscriberIn):
    email: str
    level: SubscriberLevel | None = SubscriberLevel.basic


class SubscriberAuth(SubscriberBase):
    google_tkn: str | None = None
    google_state: str | None = None
    google_state_expires_at: datetime | None = None
    short_link_hash: str | None = None


class Subscriber(SubscriberAuth):
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


class EventLocation(BaseModel):
    type: LocationType | None = LocationType.inperson
    suggestions: str | None = None
    selected: str | None = None
    name: str | None = None
    url: str | None = None
    phone: str | None = None


class Event(BaseModel):
    title: str
    start: str
    end: str
    all_day: bool | None = False
    tentative: bool | None = False
    description: str | None = None
    calendar_title: str | None = None
    calendar_color: str | None = None
    location: EventLocation | None = None


class FileDownload(BaseModel):
    name: str
    content_type: str
    data: str
