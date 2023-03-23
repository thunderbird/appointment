import json
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', "sqlite:///src/appointment.db")
connect_args = {}

if 'sqlite://' in SQLALCHEMY_DATABASE_URL:
  connect_args = {"check_same_thread": False}

engine = create_engine(
  SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
