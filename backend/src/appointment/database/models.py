"""Module: models

Definitions of database tables and their relationships.
"""

import datetime
import enum
import hashlib
import os
import uuid
import zoneinfo
from functools import cached_property

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum, Boolean, JSON, Date, Time
from sqlalchemy_utils import StringEncryptedType, ChoiceType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy.orm import relationship, as_declarative, declared_attr, Mapped
from sqlalchemy.sql import func
from appointment.defines import FALLBACK_LOCALE


def secret():
    return os.getenv('DB_SECRET')


def random_slug():
    return ''.join(str(uuid.uuid4()).split('-'))


class SubscriberLevel(enum.Enum):
    basic = 1  # basic tier
    plus = 2  # advanced tier
    pro = 3  # pro tier
    admin = 99  # unlimited tier


class AppointmentStatus(enum.Enum):
    draft = 1  # appointment was created but not published yet
    opened = 2  # appointment is published and waiting for attendees
    closed = 3  # appointment is published and fulfilled or manually closed for attendees


class BookingStatus(enum.Enum):
    none = 1  # slot status doesn't matter, because the parent object holds the state
    requested = 2  # booking slot was requested
    booked = 3  # booking slot was assigned


class LocationType(enum.Enum):
    inperson = 1  # appointment is held in person
    online = 2  # appointment is held online


class CalendarProvider(enum.Enum):
    caldav = 1  # calendar provider serves via CalDAV
    google = 2  # calendar provider is Google via its own Rest API


# Use ISO 8601 format to specify day of week
class DayOfWeek(enum.Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


class ExternalConnectionType(enum.Enum):
    zoom = 1
    google = 2
    fxa = 3
    caldav = 4
    accounts = 5


class MeetingLinkProviderType(enum.StrEnum):
    none = 'none'
    zoom = 'zoom'
    google_meet = 'google_meet'


class InviteStatus(enum.Enum):
    active = 1  # The code is still valid. It may be already used or is still to be used
    revoked = 2  # The code is no longer valid and cannot be used for sign up anymore


class ColourScheme(enum.Enum):
    system = 'system'
    dark = 'dark'
    light = 'light'


class TimeMode(enum.Enum):
    h12 = 12
    h24 = 24


def calculate_encrypted_length(length: int):
    """Calculate the length of the string after it's been encrypted and encoded."""
    cipher_length = length + 16 - (length % 16)  # Fixed block size of 16 for Aes
    return int((cipher_length + 2) / 3) << 2  # Base64 with padding


def encrypted_type(column_type, length: int = 255, **kwargs) -> StringEncryptedType:
    """Helper to reduce visual noise when creating model columns"""
    return StringEncryptedType(
        column_type, secret, AesEngine, 'pkcs5', length=calculate_encrypted_length(length), **kwargs
    )


@as_declarative()
class Base:
    """Base model, contains anything we want to be on every model."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def touch(self):
        """Updates the time_updated field with the current datetime. This function does not save the model!"""
        self.time_updated = datetime.datetime.now()

    def get_columns(self) -> list:
        return list(self.__table__.columns.keys())

    time_created = Column(DateTime, server_default=func.now(), default=func.now(), index=True)
    time_updated = Column(DateTime, server_default=func.now(), default=func.now(), onupdate=func.now(), index=True)


class HasSoftDelete:
    """Mixing in a column to support deletion without removing the record"""

    time_deleted = Column(DateTime, nullable=True)

    @property
    def is_deleted(self):
        """A record is marked deleted if a delete time is set."""
        return self.time_deleted is not None


class Subscriber(HasSoftDelete, Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(encrypted_type(String), unique=True, index=True)
    # Encrypted (here) and hashed (by the associated hashing functions in routes/auth)
    password = Column(encrypted_type(String), index=False)

    # Use subscriber.preferred_email for any email, or other user-facing presence.
    email = Column(encrypted_type(String), unique=True, index=True)
    secondary_email = Column(encrypted_type(String), nullable=True, index=True)

    name = Column(encrypted_type(String), index=True)
    level = Column(Enum(SubscriberLevel), default=SubscriberLevel.basic, index=True)
    avatar_url = Column(encrypted_type(String, length=2048), index=False)
    short_link_hash = Column(encrypted_type(String), index=False)

    # General settings
    language = Column(encrypted_type(String), nullable=False, default=FALLBACK_LOCALE, index=True)
    timezone = Column(encrypted_type(String), index=True)
    colour_scheme = Column(Enum(ColourScheme), default=ColourScheme.system, nullable=False, index=True)
    time_mode = Column(Enum(TimeMode), default=TimeMode.h12, nullable=False, index=True)

    # Only accept the times greater than the one specified in the `iat` claim of the jwt token
    minimum_valid_iat_time = Column('minimum_valid_iat_time', encrypted_type(DateTime))

    ftue_level = Column(Integer, nullable=False, default=0, index=True)

    calendars = relationship('Calendar', cascade='all,delete', back_populates='owner')
    slots = relationship('Slot', cascade='all,delete', back_populates='subscriber')
    external_connections = relationship('ExternalConnections', cascade='all,delete', back_populates='owner')

    # FIXME: Invite will be deleted if either the owner or the invited subscriber is deleted.
    invite: Mapped['Invite'] = relationship(
        'Invite',
        cascade='all,delete',
        back_populates='subscriber',
        uselist=False,
        foreign_keys='Invite.subscriber_id'
    )

    owned_invites: Mapped[list['Invite']] = relationship(
        'Invite',
        cascade='all,delete',
        back_populates='owner',
        foreign_keys='[Invite.owner_id]'
    )

    def get_external_connection(self, type: ExternalConnectionType) -> 'ExternalConnections':
        """Retrieves the first found external connection by type or returns None if not found"""
        return next(filter(lambda ec: ec.type == type, self.external_connections), None)

    @property
    def preferred_email(self):
        """Returns the preferred email address."""
        return self.secondary_email if self.secondary_email is not None else self.email

    @property
    def is_setup(self) -> bool:
        """Has the user been through the First Time User Experience?"""
        return self.ftue_level > 0

    @cached_property
    def unique_hash(self):
        """Retrieve the unique hash for the subscriber"""
        fxa = self.get_external_connection(type=ExternalConnectionType.fxa)
        # If we somehow don't have a fxa connection, use id.
        if fxa is None:
            id = self.id
        else:
            id = fxa.type_id
        hash_instance = hashlib.sha256()
        hash_instance.update(str(id).encode('utf-8'))
        return hash_instance.hexdigest()

    def __str__(self):
        return f'Subscriber: {self.id}'


class Calendar(Base):
    __tablename__ = 'calendars'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('subscribers.id'))
    provider = Column(Enum(CalendarProvider), default=CalendarProvider.caldav)
    title = Column(encrypted_type(String), index=True)
    color = Column(encrypted_type(String, length=32), index=True)
    url = Column(encrypted_type(String, length=2048), index=False)
    user = Column(encrypted_type(String), index=True)
    password = Column(encrypted_type(String))
    connected = Column(Boolean, index=True, default=False)
    connected_at = Column(DateTime)

    owner: Mapped[Subscriber] = relationship('Subscriber', back_populates='calendars', lazy=False)
    appointments: Mapped[list['Appointment']] = relationship(
        'Appointment', cascade='all,delete', back_populates='calendar'
    )
    schedules: Mapped[list['Schedule']] = relationship('Schedule', cascade='all,delete', back_populates='calendar')

    def __str__(self):
        return f'Calendar: {self.id}'


class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUIDType(native=False), default=uuid.uuid4, index=True, unique=True)
    calendar_id = Column(Integer, ForeignKey('calendars.id'))
    duration = Column(Integer)
    title = Column(encrypted_type(String))
    location_type = Column(Enum(LocationType), default=LocationType.inperson)
    location_suggestions = Column(String(255))
    location_selected = Column(Integer)
    location_name = Column(encrypted_type(String))
    location_url = Column(encrypted_type(String, length=2048))
    location_phone = Column(encrypted_type(String))
    details = Column(encrypted_type(String))
    slug = Column(encrypted_type(String), unique=True, index=True)
    keep_open = Column(Boolean)
    status: AppointmentStatus = Column(Enum(AppointmentStatus), default=AppointmentStatus.draft)
    external_id = Column(encrypted_type(String), index=True, nullable=True)

    # What (if any) meeting link will we generate once the meeting is booked
    meeting_link_provider = Column(
        encrypted_type(ChoiceType(MeetingLinkProviderType)), default=MeetingLinkProviderType.none, index=False
    )

    calendar: Mapped[Calendar] = relationship('Calendar', back_populates='appointments')
    slots: Mapped[list['Slot']] = relationship(
        'Slot',
        cascade='all,delete',
        back_populates='appointment',
        lazy='joined'
    )

    def __str__(self):
        return f'Appointment: {self.id}'


class Attendee(Base):
    __tablename__ = 'attendees'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(encrypted_type(String), index=True)
    name = Column(encrypted_type(String), index=True)
    timezone = Column(String(255), index=True)

    slots: Mapped[list['Slot']] = relationship('Slot', cascade='all,delete', back_populates='attendee')


class Slot(Base):
    __tablename__ = 'slots'

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    attendee_id = Column(Integer, ForeignKey('attendees.id'))
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'))
    time_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    start = Column(DateTime)
    duration = Column(Integer)

    # provider specific id we can use to query against their service
    meeting_link_id = Column(encrypted_type(String, length=1024), index=False)
    # meeting link override for a appointment or schedule's location url
    meeting_link_url = Column(encrypted_type(String, length=2048))

    # columns for availability bookings
    booking_tkn = Column(encrypted_type(String, length=512), index=False)
    booking_expires_at = Column(DateTime)
    booking_status = Column(Enum(BookingStatus), default=BookingStatus.none)

    appointment: Mapped[Appointment] = relationship('Appointment', back_populates='slots', lazy='joined')
    schedule: Mapped['Schedule'] = relationship('Schedule', back_populates='slots')

    attendee: Mapped[Attendee] = relationship('Attendee', cascade='all,delete', back_populates='slots', lazy='joined')
    subscriber: Mapped[Subscriber] = relationship('Subscriber', back_populates='slots')

    def __str__(self):
        return f'Slot: {self.id}'


class Schedule(Base):
    """A schedule that will dynamically create bookings against a user's availability

    Note: Start and End times are stored in UTC. And since UTC does not store the current users timezone offset.
    Because daylight savings and other timezone heckery exists, we cannot use this to compare against incoming booking
    time slots even if they are in UTC.

    So we'll need convert both times to local time to get the actual intended start time. For that we have
    start_time_local and end_time_local properties, which takes the schedule's time_updated and replaces the
    time components and returns the converted time.

    This works because time_updated has the date of which the start_time and end_time fields are correct, so if we
    re-create that date we'll get the correct utc offset. Since the *_local properties return a Time object and not
    Date/DateTime we can safely ignore any unintended date matching.
    """
    __tablename__ = 'schedules'

    id: int = Column(Integer, primary_key=True, index=True)
    calendar_id: int = Column(Integer, ForeignKey('calendars.id'))
    active: bool = Column(Boolean, index=True, default=True)
    name: str = Column(encrypted_type(String), index=True)
    slug: str = Column(encrypted_type(String), index=True, unique=True)
    location_type: LocationType = Column(Enum(LocationType), default=LocationType.inperson)
    location_url: str = Column(encrypted_type(String, length=2048))
    details: str = Column(encrypted_type(String))
    start_date: datetime.date = Column(encrypted_type(Date), index=True)
    end_date: datetime.date = Column(encrypted_type(Date), index=True)
    start_time: datetime.time = Column(encrypted_type(Time), index=True)  # in utc
    end_time: datetime.time = Column(encrypted_type(Time), index=True)  # in utc
    earliest_booking: int = Column(Integer, default=1440)  # in minutes, defaults to 24 hours
    farthest_booking: int = Column(Integer, default=20160)  # in minutes, defaults to 2 weeks
    weekdays: str | dict = Column(JSON, default='[1,2,3,4,5]')  # list of ISO weekdays, Mo-Su => 1-7
    slot_duration: int = Column(Integer, default=30)  # defaults to 30 minutes
    booking_confirmation: bool = Column(Boolean, index=True, nullable=False, default=True)
    timezone: str = Column(encrypted_type(String), index=True, nullable=True)

    # What (if any) meeting link will we generate once the meeting is booked
    meeting_link_provider: MeetingLinkProviderType = Column(
        encrypted_type(ChoiceType(MeetingLinkProviderType)), default=MeetingLinkProviderType.none, index=False
    )

    calendar: Mapped[Calendar] = relationship('Calendar', back_populates='schedules', lazy=False)
    availabilities: Mapped[list['Availability']] = relationship(
        'Availability', cascade='all,delete', back_populates='schedule'
    )
    slots: Mapped[list[Slot]] = relationship('Slot', cascade='all,delete', back_populates='schedule')

    @property
    def timezone_offset(self):
        """A timedelta of the UTC offset from the time the schedule was saved in."""
        return self.time_updated.replace(tzinfo=zoneinfo.ZoneInfo(self.timezone)).utcoffset()

    @property
    def start_time_local(self) -> datetime.time:
        """Start Time in the Schedule's Calendar's Owner's timezone"""
        time_of_save = self.time_updated.replace(
            hour=self.start_time.hour, minute=self.start_time.minute, second=0, tzinfo=datetime.timezone.utc
        )
        return time_of_save.astimezone(zoneinfo.ZoneInfo(self.calendar.owner.timezone)).time()

    @property
    def end_time_local(self) -> datetime.time:
        """End Time in the Schedule's Calendar's Owner's timezone"""
        time_of_save = self.time_updated.replace(
            hour=self.end_time.hour, minute=self.end_time.minute, second=0, tzinfo=datetime.timezone.utc
        )
        return time_of_save.astimezone(zoneinfo.ZoneInfo(self.calendar.owner.timezone)).time()

    @cached_property
    def owner(self):
        if not self.calendar:
            return None
        return self.calendar.owner

    def __str__(self):
        return f'Schedule: {self.id}'


class Availability(Base):
    """This table will be used as soon as the application provides custom availability
    in addition to the general availability
    """

    __tablename__ = 'availabilities'

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    day_of_week = Column(encrypted_type(String), index=True)
    start_time = Column(encrypted_type(String), index=True)
    end_time = Column(encrypted_type(String), index=True)
    # Can't book if it's less than X minutes before start time:
    min_time_before_meeting = Column(encrypted_type(String), index=True)
    slot_duration = Column(Integer)  # Size of the Slot that can be booked.

    schedule: Mapped[Schedule] = relationship('Schedule', back_populates='availabilities')

    def __str__(self):
        return f'Availability: {self.id}'


class ExternalConnections(Base):
    """This table holds all external service connections to a subscriber."""

    __tablename__ = 'external_connections'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('subscribers.id'))
    name = Column(encrypted_type(String), index=False)
    type = Column(Enum(ExternalConnectionType), index=True)
    type_id = Column(encrypted_type(String), index=True)
    token = Column(encrypted_type(String, length=2048), index=False)
    owner: Mapped[Subscriber] = relationship('Subscriber', back_populates='external_connections')

    def __str__(self):
        return f'External Connection: {self.id}'


class Invite(Base):
    """This table holds all invite codes for code based sign-ups."""

    __tablename__ = 'invites'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('subscribers.id'), nullable=True)
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'))
    code = Column(encrypted_type(String), index=False)
    status = Column(Enum(InviteStatus), index=True)

    owner: Mapped['Subscriber'] = relationship(
        'Subscriber',
        back_populates='invite',
        single_parent=True,
        foreign_keys=[owner_id]
    )

    subscriber: Mapped['Subscriber'] = relationship(
        'Subscriber',
        back_populates='invite',
        single_parent=True,
        foreign_keys=[subscriber_id]
    )

    waiting_list: Mapped['WaitingList'] = relationship(
        'WaitingList',
        cascade='all,delete',
        back_populates='invite',
        uselist=False
    )

    @property
    def is_used(self) -> bool:
        """True if the invite code is assigned to a subscriber"""
        return self.subscriber_id is not None

    @property
    def is_revoked(self) -> bool:
        """True if the invite code is revoked"""
        return self.status == InviteStatus.revoked

    @property
    def is_available(self) -> bool:
        """True if the invite code is not assigned nor revoked"""
        return self.subscriber_id is None and self.status == InviteStatus.active

    def __str__(self):
        return f'Invite {self.id}'


class WaitingList(Base):
    """Holds a list of hopefully future-Appointment users"""

    __tablename__ = 'waiting_list'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(encrypted_type(String), unique=True, index=True, nullable=False)
    email_verified = Column(Boolean, nullable=False, index=True, default=False)
    invite_id = Column(Integer, ForeignKey('invites.id'), nullable=True, index=True)

    invite: Mapped['Invite'] = relationship('Invite', back_populates='waiting_list', single_parent=True)

    def __str__(self):
        return f'Waiting List: {self.id}'
