from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# database
from sqlalchemy.orm import Session
from .database import repo, models, schemas
from .database.database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

# authentication
from .controller.auth import Auth

# init app
app = FastAPI()

# allow requests from own frontend running on a different port
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:8080"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

def get_db():
  """run database session"""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

me = None

@app.get("/")
def main(db: Session = Depends(get_db)):
  me = Auth(db).subscriber
  """endpoint to get authentication status of current user"""
  return me


@app.post("/me/", response_model=schemas.Subscriber)
def create_me(subscriber: schemas.SubscriberCreate, db: Session = Depends(get_db)):
  """endpoint to add an authenticated subscriber to db, if they doesn't exist yet"""
  db_subscriber = repo.get_subscriber_by_email(db=db, email=subscriber.email)
  if db_subscriber:
    raise HTTPException(status_code=400, detail="Email already registered")
  return repo.create_subscriber(db=db, subscriber=subscriber)


@app.get("/me/", response_model=schemas.Subscriber)
def read_me(db: Session = Depends(get_db)):
  """endpoint to get data of authenticated subscriber from db"""
  db_subscriber = repo.get_subscriber(db=db, subscriber_id=me.id)
  if db_subscriber is None:
    raise HTTPException(status_code=404, detail="Subscriber not found")
  return db_subscriber


@app.get("/me/calendars/", response_model=list[schemas.Calendar])
def read_my_calendars(db: Session = Depends(get_db)):
  """get all calendar connections of authenticated subscriber"""
  calendars = repo.get_calendar_by_subscriber(db, subscriber_id=me.id)
  return calendars


@app.post("/calendar/", response_model=schemas.Calendar)
def create_my_calendar(calendar: schemas.CalendarCreate, db: Session = Depends(get_db)):
  """endpoint to add a new calender connection for authenticated subscriber"""
  return repo.create_subscriber_calendar(db=db, calendar=calendar, subscriber_id=me.id)


@app.get("/calendar/{id}", response_model=schemas.Calendar)
def read_calendar(id: int, db: Session = Depends(get_db)):
  """endpoint to get a calendar from db"""
  db_calendar = repo.get_calendar(db, calendar_id=id)
  if db_calendar is None:
    raise HTTPException(status_code=404, detail="Calendar not found")
  return db_calendar
