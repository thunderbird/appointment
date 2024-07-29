"""Module: schemas

Definitions of valid data shapes for database and query models.
"""

import json
from uuid import UUID
from datetime import datetime, date, time
from typing import Annotated, Optional

from pydantic import BaseModel, Field, EmailStr

from .models import (
    AppointmentStatus,
    BookingStatus,
    CalendarProvider,
    DayOfWeek,
    LocationType,
    random_slug,
    SubscriberLevel,
    ExternalConnectionType,
    MeetingLinkProviderType,
    InviteStatus,
)
from .. import utils

""" ATTENDEE model schemas
"""


class AttendeeBase(BaseModel):
    email: str
    name: str | None = None
    timezone: str | None = None


class Attendee(AttendeeBase):
    id: int

    class Config:
        from_attributes = True


""" SLOT model schemas
"""


class SlotBase(BaseModel):
    start: datetime
    duration: int | None = None
    attendee_id: int | None = None
    booking_tkn: str | None = None
    booking_expires_at: datetime | None = None
    booking_status: BookingStatus | None = BookingStatus.none
    meeting_link_id: str | None = None
    meeting_link_url: str | None = None


class Slot(SlotBase):
    id: int
    appointment_id: int
    subscriber_id: int | None = None
    time_updated: datetime | None = None
    attendee: Attendee | None = None

    class Config:
        from_attributes = True


class SlotOut(SlotBase):
    id: int | None = None


class SlotAttendee(BaseModel):
    slot_id: int
    attendee: AttendeeBase


class AvailabilitySlotAttendee(BaseModel):
    slot: SlotBase
    attendee: AttendeeBase


""" APPOINTMENT model schemas
"""


class AppointmentBase(BaseModel):
    title: str
    details: str | None = None
    slug: str | None = Field(default_factory=random_slug)
    # Needed for ical creation
    location_url: str | None = None


class AppointmentFull(AppointmentBase):
    calendar_id: int
    duration: int | None = None
    location_type: LocationType | None = LocationType.inperson
    location_suggestions: str | None = None
    location_selected: str | None = None
    location_name: str | None = None
    location_phone: str | None = None
    keep_open: bool | None = True
    status: AppointmentStatus | None = AppointmentStatus.draft
    meeting_link_provider: MeetingLinkProviderType | None = MeetingLinkProviderType.none


class Appointment(AppointmentFull):
    id: int
    uuid: UUID
    time_created: datetime | None = None
    time_updated: datetime | None = None
    slots: list[Slot] = []

    class Config:
        from_attributes = True


class AppointmentWithCalendarOut(Appointment):
    """For /me/appointments"""

    calendar_title: str
    calendar_color: str


class AppointmentOut(AppointmentBase):
    id: int | None = None
    owner_name: str | None = None
    slots: list[SlotBase | SlotOut] = []
    slot_duration: int
    booking_confirmation: bool


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
        from_attributes = True


class ScheduleBase(BaseModel):
    active: bool | None = True
    name: str = Field(min_length=1, max_length=128)
    slug: Optional[str] = None
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
    weekdays: list[int] | None = Field(min_length=1, default=[1, 2, 3, 4, 5])
    slot_duration: int | None = None
    meeting_link_provider: MeetingLinkProviderType | None = MeetingLinkProviderType.none
    booking_confirmation: bool = True

    class Config:
        json_encoders = {
            time: lambda t: t.strftime('%H:%M'),
        }


class Schedule(ScheduleBase):
    id: int
    time_created: datetime | None = None
    time_updated: datetime | None = None
    availabilities: list[Availability] = []
    calendar: 'CalendarBase'

    class Config:
        from_attributes = True


class ScheduleValidationIn(ScheduleBase):
    """ScheduleBase but with specific fields overridden to add validation."""

    slot_duration: Annotated[int, Field(ge=10, default=30)]


class ScheduleSlug(BaseModel):
    slug: str


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
        from_attributes = True


class CalendarOut(CalendarBase):
    id: int


""" INVITE model schemas
"""


class Invite(BaseModel):
    subscriber_id: int | None = None
    code: str
    status: InviteStatus = InviteStatus.active
    time_created: datetime | None = None
    time_updated: datetime | None = None


""" SUBSCRIBER model schemas
"""


class SubscriberIn(BaseModel):
    timezone: str | None = None
    username: str = Field(min_length=1, max_length=128)
    name: Optional[str] = Field(min_length=1, max_length=128, default=None)
    avatar_url: str | None = None
    secondary_email: str | None = None


class SubscriberBase(SubscriberIn):
    email: str = Field(min_length=1, max_length=200)
    preferred_email: str | None = None
    is_setup: bool | None = None
    level: SubscriberLevel | None = SubscriberLevel.basic


class SubscriberAuth(SubscriberBase):
    short_link_hash: str | None = None


class Subscriber(SubscriberAuth):
    id: int
    calendars: list[Calendar] = []
    slots: list[Slot] = []
    ftue_level: Optional[int] = Field(gte=0)

    class Config:
        from_attributes = True


class SubscriberMeOut(SubscriberBase):
    unique_hash: Optional[str] = None
    schedule_links: list[str] = []


class SubscriberAdminOut(Subscriber):
    invite: Invite | None = None
    time_created: datetime
    time_deleted: datetime | None

    class Config:
        from_attributes = True


""" other schemas used for requests or data migration
"""


class AppointmentSlots(BaseModel):
    appointment: AppointmentFull
    slots: list[SlotBase] = []


class AvailabilitySlotConfirmation(BaseModel):
    slot_id: int
    slot_token: str
    owner_url: str
    confirmed: bool | None = False


class EventLocation(BaseModel):
    type: LocationType | None = LocationType.inperson
    suggestions: str | None = None
    selected: str | None = None
    name: str | None = None
    url: str | None = None
    phone: str | None = None


class Event(BaseModel):
    title: str
    start: datetime
    end: datetime
    all_day: bool | None = False
    tentative: bool | None = False
    description: str | None = None
    calendar_title: str | None = None
    calendar_color: str | None = None
    location: EventLocation | None = None
    uuid: UUID | None = None

    """Ideally this would just be a mixin, but I'm having issues figuring out a good
    static constructor that will work for anything."""

    def model_dump_redis(self):
        """Dumps our event into an encrypted json blob for redis"""
        values_json = self.model_dump_json()

        return utils.setup_encryption_engine().encrypt(values_json)

    @staticmethod
    def model_load_redis(encrypted_blob):
        """Loads and decrypts our encrypted json blob from redis"""

        values_json = utils.setup_encryption_engine().decrypt(encrypted_blob)
        values = json.loads(values_json)

        return Event(**values)


class FileDownload(BaseModel):
    name: str
    content_type: str
    data: str


class ExternalConnection(BaseModel):
    owner_id: int
    name: str
    type: ExternalConnectionType
    type_id: str
    token: str


class ExternalConnectionOut(BaseModel):
    owner_id: int
    name: str
    type: str
    type_id: str


class SupportRequest(BaseModel):
    topic: str
    details: str


"""Auth"""


class Login(BaseModel):
    username: str
    password: str | None = None
    timezone: str | None = None


class TokenData(BaseModel):
    username: str


"""Invite"""


class SendInviteEmailIn(BaseModel):
    email: str = Field(title='Email', min_length=1)


class JoinTheWaitingList(BaseModel):
    email: str = Field(title='Email', min_length=1)


class TokenForWaitingList(BaseModel):
    token: str = Field(title='Token')


class CheckEmail(BaseModel):
    email: EmailStr = Field(title='Email', min_length=1)


class WaitingListAdminOut(BaseModel):
    id: int
    email: str
    email_verified: bool
    invite_id: int | None = None
    time_created: datetime
    time_updated: datetime

    invite: Invite | None = None

    class Config:
        from_attributes = True


class PageLoadIn(BaseModel):
    browser: Optional[str]
    browser_version: Optional[str]
    os: Optional[str]
    os_version: Optional[str]
    device: Optional[str]
    device_model: Optional[str]
    resolution: Optional[str]
    effective_resolution: Optional[str]
    user_agent: Optional[str]
    locale: Optional[str]
    theme: Optional[str]


class FTUEStepIn(BaseModel):
    step_level: int
    step_name: str

