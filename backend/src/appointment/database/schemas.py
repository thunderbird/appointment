"""Module: schemas

Definitions of valid data shapes for database and query models.
"""

import json
import zoneinfo
from uuid import UUID
from datetime import datetime, date, time, timezone, timedelta
from typing import Annotated, Optional, Self

from pydantic import BaseModel, ConfigDict, Field, EmailStr, model_validator
from pydantic_core import PydanticCustomError

from ..defines import DEFAULT_CALENDAR_COLOUR, FALLBACK_LOCALE
from ..l10n import l10n


from .models import (
    AppointmentStatus,
    BookingStatus,
    CalendarProvider,
    LocationType,
    random_slug,
    SubscriberLevel,
    ExternalConnectionType,
    MeetingLinkProviderType,
    InviteStatus,
    ColourScheme,
    TimeMode,
    IsoWeekday
)
from .. import utils, defines

""" ATTENDEE model schemas
"""


class AttendeeBase(BaseModel):
    email: str
    name: str | None = None
    timezone: str | None = None


class Attendee(AttendeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    subscriber_id: int | None = None
    time_updated: datetime | None = None
    attendee: Attendee | None = None


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    time_created: datetime | None = None
    time_updated: datetime | None = None
    slots: list[Slot] = []


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
    model_config = ConfigDict(json_encoders={time: lambda t: t.strftime('%H:%M')})

    schedule_id: int
    day_of_week: IsoWeekday
    start_time: time | None = None
    end_time: time | None = None
    min_time_before_meeting: int | None = None
    slot_duration: int | None = None


class Availability(AvailabilityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    time_created: datetime | None = None
    time_updated: datetime | None = None


class AvailabilityValidationIn(AvailabilityBase):
    # Require these fields
    start_time: time
    end_time: time


class ScheduleBase(BaseModel):
    model_config = ConfigDict(json_encoders={time: lambda t: t.strftime('%H:%M')})

    active: bool | None = True
    name: str = Field(min_length=1, max_length=128)
    slug: Optional[str] = None
    calendar_id: int
    location_type: LocationType | None = LocationType.inperson
    location_url: Annotated[str | None, Field(max_length=2048)] = None
    details: Annotated[str | None, Field(max_length=250)] = None
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
    timezone: Optional[str] = None
    use_custom_availabilities: bool = False


class Schedule(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    time_created: datetime | None = None
    time_updated: datetime | None = None
    availabilities: list[Availability] = []
    calendar: 'CalendarBase'


class ScheduleValidationIn(ScheduleBase):
    """ScheduleBase but with specific fields overridden to add validation."""

    # Regex to exclude any character can be mess with a url
    slug: Annotated[Optional[str], Field(max_length=16, pattern=r'^[^\;\/\?\:\@\&\=\+\$\,\#]*$')] = None
    slot_duration: Annotated[int, Field(ge=10, default=30)]
    availabilities: list[AvailabilityValidationIn] = []
    # Require these fields
    start_date: date
    start_time: time
    end_time: time

    @model_validator(mode='after')
    def start_time_should_be_before_end_time(self) -> Self:
        # Can't have the end time before the start time!
        # (Well you can, it will roll over to the next day, but the ux is poor!)
        # Note we have to convert to the local timezone for this to work...

        # Fallback to utc...
        tz = self.timezone or 'UTC'

        start_time = datetime.combine(self.start_date, self.start_time, tzinfo=timezone.utc).astimezone(
            zoneinfo.ZoneInfo(tz)
        )

        end_time = datetime.combine(self.start_date, self.end_time, tzinfo=timezone.utc).astimezone(
            zoneinfo.ZoneInfo(tz)
        )

        start_time = start_time + timedelta(minutes=self.slot_duration)
        end_time = end_time
        # Compare time objects!
        if start_time.time() > end_time.time():
            msg = l10n('error-minimum-value')

            # These can't be field or value because that will auto-format the msg? Weird feature but okay.
            raise PydanticCustomError(
                defines.END_TIME_BEFORE_START_TIME_ERR,
                msg,
                {'err_field': 'end_time', 'err_value': start_time.astimezone(timezone.utc).time()},
            )

        return self


class ScheduleSlug(BaseModel):
    slug: str


""" CALENDAR model schemas
"""


class CalendarBase(BaseModel):
    title: str | None = None
    color: str | None = DEFAULT_CALENDAR_COLOUR
    connected: bool | None = None


class CalendarConnectionOut(CalendarBase):
    provider: CalendarProvider | None = CalendarProvider.caldav
    url: str
    user: str


class CalendarConnection(CalendarConnectionOut):
    password: str


class CalendarConnectionIn(CalendarConnection):
    url: str = Field(min_length=1)
    user: str = Field(min_length=1)
    password: Optional[str]


class Calendar(CalendarConnection):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    appointments: list[Appointment] = []
    schedules: list[Schedule] = []


class CalendarOut(CalendarBase):
    id: int


""" INVITE model schemas
"""


class Invite(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subscriber_id: int | None = None
    owner_id: Optional[int] = None
    code: str
    status: InviteStatus = InviteStatus.active
    time_created: datetime | None = None
    time_updated: datetime | None = None


class InviteOut(BaseModel):
    code: str
    status: InviteStatus = InviteStatus.active


""" SUBSCRIBER model schemas
"""


class SubscriberIn(BaseModel):
    timezone: str | None = None
    username: str = Field(min_length=1, max_length=128)
    name: Optional[str] = Field(min_length=1, max_length=128, default=None)
    avatar_url: str | None = None
    secondary_email: str | None = None
    language: str | None = FALLBACK_LOCALE
    colour_scheme: ColourScheme = ColourScheme.system
    time_mode: TimeMode = TimeMode.h12
    start_of_week: IsoWeekday = IsoWeekday.sunday


class SubscriberBase(SubscriberIn):
    email: str = Field(min_length=1, max_length=200)
    preferred_email: str | None = None
    is_setup: bool | None = None
    level: SubscriberLevel | None = SubscriberLevel.basic


class SubscriberAuth(SubscriberBase):
    short_link_hash: str | None = None


class Subscriber(SubscriberAuth):
    model_config = ConfigDict(from_attributes=True)

    id: int
    calendars: list[Calendar] = []
    slots: list[Slot] = []
    ftue_level: Optional[int] = Field(json_schema_extra={'gte': 0})


class SubscriberMeOut(SubscriberBase):
    unique_hash: Optional[str] = None
    user_link: Optional[str] = None
    schedule_slugs: dict = {}


class SubscriberAdminItem(SubscriberAuth):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invite: Invite | None = None
    time_created: datetime
    time_deleted: datetime | None
    ftue_level: Optional[int] = Field(json_schema_extra={'gte': 0})


class Paginator(BaseModel):
    page: int
    total_pages: int
    count: int
    per_page: int


class ListResponse(BaseModel):
    items: list
    page_meta: Paginator


class SubscriberAdminOut(ListResponse):
    items: list[SubscriberAdminItem]


class ListResponseIn(BaseModel):
    page: int = 1
    per_page: int = 50


class InviteAdminOut(ListResponse):
    items: list[Invite]

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
    external_id: str | None = None

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
    email: EmailStr = Field(title='Email', min_length=1)


class JoinTheWaitingList(BaseModel):
    email: EmailStr = Field(title='Email', min_length=1)


class TokenForWaitingList(BaseModel):
    token: str = Field(title='Token')


class CheckEmail(BaseModel):
    email: EmailStr = Field(title='Email', min_length=1)


class WaitingListInviteAdminIn(BaseModel):
    id_list: list[int]


class WaitingListInviteAdminOut(BaseModel):
    accepted: list[int]
    errors: list[str]


class WaitingListAdminOutItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    email_verified: bool
    invite_id: int | None = None
    time_created: datetime
    time_updated: datetime

    invite: Invite | None = None


class WaitingListAdminOut(ListResponse):
    items: list[WaitingListAdminOutItem]


class PageLoadIn(BaseModel):
    browser: Optional[str] = None
    browser_version: Optional[str] = None
    os: Optional[str] = None
    os_version: Optional[str] = None
    device: Optional[str] = None
    device_model: Optional[str] = None
    resolution: Optional[str] = None
    effective_resolution: Optional[str] = None
    user_agent: Optional[str] = None
    locale: Optional[str] = None
    theme: Optional[str] = None


class FTUEStepIn(BaseModel):
    step_level: int
    step_name: str
