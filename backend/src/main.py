from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# database
from sqlalchemy.orm import Session
from .database import repo, models, schemas
from .database.database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

# authentication
from .controller.auth import verify_subscriber
me = verify_subscriber()

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

@app.get("/")
def home():
  return me

# run database
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


@app.post("/subscribers/", response_model=schemas.Subscriber)
def create_subscriber(subscriber: schemas.SubscriberCreate, db: Session = Depends(get_db)):
  db_subscriber = repo.get_subscriber_by_email(db, email=subscriber.email)
  if db_subscriber:
    raise HTTPException(status_code=400, detail="Email already registered")
  return repo.create_subscriber(db=db, subscriber=subscriber)


@app.get("/subscribers/{subscriber_id}", response_model=schemas.Subscriber)
def read_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
  db_subscriber = repo.get_subscriber(db, subscriber_id=subscriber_id)
  if db_subscriber is None:
    raise HTTPException(status_code=404, detail="Subscriber not found")
  return db_subscriber


@app.post("/subscribers/{subscriber_id}/calendars/", response_model=schemas.Calendar)
def create_calendar_for_subscriber(
  subscriber_id: int, calendar: schemas.CalendarCreate, db: Session = Depends(get_db)
):
  return repo.create_subscriber_calendar(db=db, calendar=calendar, subscriber_id=subscriber_id)


@app.get("/me/calendars/", response_model=list[schemas.Calendar])
def read_subscriber_calendars(db: Session = Depends(get_db)):
  calendars = repo.get_calendar_by_subscriber(db, subscriber_id=me)
  return calendars
