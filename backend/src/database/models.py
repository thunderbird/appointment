from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Subscriber(Base):
  __tablename__ = "subscribers"

  id        = Column(Integer, primary_key=True, index=True)
  username  = Column(String, unique=True, index=True)
  email     = Column(String, unique=True, index=True)
  name      = Column(String, index=True)
  level     = Column(Integer, index=True)
  timezone  = Column(Integer, index=True)

  calendars = relationship("Calendar", back_populates="owner")


class Calendar(Base):
  __tablename__ = "calendars"

  id        = Column(Integer, primary_key=True, index=True)
  owner_id  = Column(Integer, ForeignKey("subscribers.id"))
  url       = Column(String, index=True)
  user      = Column(String, index=True)
  password  = Column(String)

  owner     = relationship("Subscriber", back_populates="calendars")
