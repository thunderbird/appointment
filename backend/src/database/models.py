"""Module: models

Definitions of database tables and their relationships.
"""
import enum
import json
import os
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum, Boolean
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


def secret():
    return os.getenv("DB_SECRET")


def random_slug():
    return "".join(str(uuid.uuid4()).split("-"))


class SubscriberLevel(enum.Enum):
    basic = 1  # basic tier
    plus = 2  # advanced tier
    pro = 3  # pro tier
    admin = 99  # unlimited tier


class AppointmentStatus(enum.Enum):
    draft = 1  # appointment was created but not published yet
    opened = 2  # appointment is published and waiting for attendees
    closed = 3  # appointment is published and fulfilled or manually closed for attendees


class LocationType(enum.Enum):
    inperson = 1  # appointment is held in person
    online = 2  # appointment is held online


class CalendarProvider(enum.Enum):
    caldav = 1  # calendar provider serves via CalDAV
    google = 2  # calendar provider is Google via its own Rest API


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255),
        unique=True,
        index=True,
    )
    email = Column(
        StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255),
        unique=True,
        index=True,
    )
    name = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255), index=True)
    level = Column(Enum(SubscriberLevel), default=SubscriberLevel.basic, index=True)
    timezone = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255), index=True)
    google_tkn = Column(
        StringEncryptedType(String, secret, AesEngine, "pkcs5", length=2048),
        index=False,
    )
    # Temp storage for verifying google state tokens between authentication
    google_state = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=512), index=False)
    google_state_expires_at = Column(DateTime)

    calendars = relationship("Calendar", cascade="all,delete", back_populates="owner")
    slots = relationship("Slot", cascade="all,delete", back_populates="subscriber")


class Calendar(Base):
    __tablename__ = "calendars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("subscribers.id"))
    provider = Column(Enum(CalendarProvider), default=CalendarProvider.caldav)
    title = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255), index=True)
    color = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=32), index=True)
    url = Column(
        StringEncryptedType(String, secret, AesEngine, "pkcs5", length=2048),
        index=False,
    )
    user = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255), index=True)
    password = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255))

    owner = relationship("Subscriber", back_populates="calendars")
    appointments = relationship("Appointment", cascade="all,delete", back_populates="calendar")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    calendar_id = Column(Integer, ForeignKey("calendars.id"))
    time_created = Column(DateTime, server_default=func.now())
    time_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    duration = Column(Integer)
    title = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255))
    location_type = Column(Enum(LocationType), default=LocationType.inperson)
    location_suggestions = Column(String(255))
    location_selected = Column(Integer)
    location_name = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255))
    location_url = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=2048))
    location_phone = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255))
    details = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255))
    slug = Column(
        StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255),
        unique=True,
        index=True,
    )
    keep_open = Column(Boolean)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.draft)

    calendar = relationship("Calendar", back_populates="appointments")
    slots = relationship("Slot", cascade="all,delete", back_populates="appointment")


class Attendee(Base):
    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255), index=True)
    name = Column(StringEncryptedType(String, secret, AesEngine, "pkcs5", length=255), index=True)

    slots = relationship("Slot", cascade="all,delete", back_populates="attendee")


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    attendee_id = Column(Integer, ForeignKey("attendees.id"))
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))
    time_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    start = Column(DateTime)
    duration = Column(Integer)

    appointment = relationship("Appointment", back_populates="slots")
    attendee = relationship("Attendee", back_populates="slots")
    subscriber = relationship("Subscriber", back_populates="slots")
