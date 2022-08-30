"""Module: models

Definitions of database tables and their relationships.
"""
import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

def secret():
  return '4pp01n+m3n+' # TODO: get from env

class AppointmentStatus(enum.Enum):
  draft  = 1
  ready  = 2
  closed = 3


class Subscriber(Base):
  __tablename__ = "subscribers"

  id        = Column(Integer, primary_key=True, index=True)
  username  = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), unique=True, index=True)
  email     = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), unique=True, index=True)
  name      = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  level     = Column(Integer, index=True)
  timezone  = Column(Integer, index=True)

  calendars = relationship("Calendar", cascade="all,delete", back_populates="owner")


class Calendar(Base):
  __tablename__ = "calendars"

  id           = Column(Integer, primary_key=True, index=True)
  owner_id     = Column(Integer, ForeignKey("subscribers.id"))
  url          = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  user         = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  password     = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'))

  owner        = relationship("Subscriber", back_populates="calendars")
  appointments = relationship("Appointment", cascade="all,delete", back_populates="calendar")


class Appointment(Base):
  __tablename__ = "appointments"

  id                   = Column(Integer, primary_key=True, index=True)
  time_created         = Column(DateTime(timezone=True), server_default=func.now())
  time_updated         = Column(DateTime(timezone=True), onupdate=func.now())
  calendar_id          = Column(Integer, ForeignKey("calendars.id"))
  duration             = Column(Integer)
  title                = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'))
  location_suggestions = Column(String)
  location_selected    = Column(Integer)
  location_name        = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'))
  location_url         = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'))
  location_phone       = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'))
  details              = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'))
  attendees            = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  slug                 = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  status               = Column(Enum(AppointmentStatus))

  calendar             = relationship("Calendar", back_populates="appointments")
  slots                = relationship("Slot", cascade="all,delete", back_populates="appointment")


class Slot(Base):
  __tablename__ = "slots"

  id             = Column(Integer, primary_key=True, index=True)
  appointment_id = Column(Integer, ForeignKey("appointments.id"))
  start          = Column(DateTime(timezone=True))
  is_available   = Column(Boolean, default=True)

  appointment    = relationship("Appointment", back_populates="slots")
