"""Module: models

Definitions of database tables and their relationships.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy.orm import relationship
from .database import Base

def secret():
  return '4pp01n+m3n+' # TODO: get from env

class Subscriber(Base):
  __tablename__ = "subscribers"

  id        = Column(Integer, primary_key=True, index=True)
  username  = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), unique=True, index=True)
  email     = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), unique=True, index=True)
  name      = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  level     = Column(Integer, index=True)
  timezone  = Column(Integer, index=True)

  calendars = relationship("Calendar", back_populates="owner")


class Calendar(Base):
  __tablename__ = "calendars"

  id        = Column(Integer, primary_key=True, index=True)
  owner_id  = Column(Integer, ForeignKey("subscribers.id"))
  url       = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  user      = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'), index=True)
  password  = Column(StringEncryptedType(String, secret, AesEngine, 'pkcs5'))

  owner     = relationship("Subscriber", back_populates="calendars")
