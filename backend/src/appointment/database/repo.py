"""Module: repo

Repository providing CRUD functions for all database models. 
"""
import os
import re
import uuid

from datetime import timedelta, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .schemas import ExternalConnection
from ..controller.auth import sign_url


"""ATTENDEES repository functions
"""


def get_attendees_by_subscriber(db: Session, subscriber_id: int):
    """For use with the data download. Get attendees by subscriber id."""
    # We need to walk through Calendars to attach Appointments, and Appointments to get Slots
    slots = (
        db.query(models.Slot)
        .join(models.Appointment)
        .join(models.Calendar)
        .filter(models.Calendar.owner_id == subscriber_id)
        .filter(models.Appointment.calendar_id == models.Calendar.id)
        .filter(models.Slot.appointment_id == models.Appointment.id)
        .all()
    )

    attendee_ids = list(map(lambda slot: slot.attendee_id if slot.attendee_id is not None else None, slots))
    attendee_ids = filter(lambda attendee: attendee is not None, attendee_ids)
    return db.query(models.Attendee).filter(models.Attendee.id.in_(attendee_ids)).all()


def delete_attendees_by_subscriber(db: Session, subscriber_id: int):
    """Delete all attendees by subscriber"""
    attendees = get_attendees_by_subscriber(db, subscriber_id)

    for attendee in attendees:
        db.delete(attendee)
    db.commit()

    return True


""" SUBSCRIBERS repository functions
"""


def get_subscriber(db: Session, subscriber_id: int) -> models.Subscriber | None:
    """retrieve subscriber by id"""
    return db.get(models.Subscriber, subscriber_id)


def get_subscriber_by_email(db: Session, email: str):
    """retrieve subscriber by email"""
    return db.query(models.Subscriber).filter(models.Subscriber.email == email).first()


def get_subscriber_by_username(db: Session, username: str):
    """retrieve subscriber by username"""
    return db.query(models.Subscriber).filter(models.Subscriber.username == username).first()


def get_subscriber_by_appointment(db: Session, appointment_id: int):
    """retrieve appointment by subscriber username and appointment slug (public)"""
    if appointment_id:
        return (
            db.query(models.Subscriber)
            .join(models.Calendar)
            .join(models.Appointment)
            .filter(models.Appointment.id == appointment_id)
            .first()
        )
    return None


def get_subscriber_by_google_state(db: Session, state: str):
    """retrieve subscriber by google state, you'll have to manually check the google_state_expire_at!"""
    if state is None:
        return None
    return db.query(models.Subscriber).filter(models.Subscriber.google_state == state).first()


def create_subscriber(db: Session, subscriber: schemas.SubscriberBase):
    """create new subscriber"""
    db_subscriber = models.Subscriber(**subscriber.dict())
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def update_subscriber(db: Session, data: schemas.SubscriberIn, subscriber_id: int):
    """update all subscriber attributes, they can edit themselves"""
    db_subscriber = get_subscriber(db, subscriber_id)
    for key, value in data:
        if value is not None:
            setattr(db_subscriber, key, value)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def delete_subscriber(db: Session, subscriber: models.Subscriber):
    """Delete a subscriber by subscriber id"""
    db.delete(subscriber)
    db.commit()
    return True


def get_connections_limit(db: Session, subscriber_id: int):
    """return the number of allowed connections for given subscriber or -1 for unlimited connections"""
    # db_subscriber = get_subscriber(db, subscriber_id)
    # mapping = {
    #     models.SubscriberLevel.basic: int(os.getenv("TIER_BASIC_CALENDAR_LIMIT")),
    #     models.SubscriberLevel.plus: int(os.getenv("TIER_PLUS_CALENDAR_LIMIT")),
    #     models.SubscriberLevel.pro: int(os.getenv("TIER_PRO_CALENDAR_LIMIT")),
    #     models.SubscriberLevel.admin: -1,
    # }
    # return mapping[db_subscriber.level]

    # No limit right now!
    return -1


def verify_subscriber_link(db: Session, url: str):
    """Check if a given url is a valid signed subscriber profile link
    Return subscriber if valid.
    """
    # Look for a <username> followed by an optional signature that ends the string
    pattern = r"[\/]([\w\d\-_\.\@]+)[\/]?([\w\d]*)[\/]?$"
    match = re.findall(pattern, url)

    if match is None or len(match) == 0:
        return False

    # Flatten
    match = match[0]
    clean_url = url

    username = match[0]
    signature = None
    if len(match) > 1:
        signature = match[1]
        clean_url = clean_url.replace(signature, "")

    subscriber = get_subscriber_by_username(db, username)
    if not subscriber:
        return False

    clean_url_with_short_link = clean_url + f"{subscriber.short_link_hash}"
    signed_signature = sign_url(clean_url_with_short_link)

    # Verify the signature matches the incoming one
    if signed_signature == signature:
        return subscriber
    return False


""" CALENDAR repository functions
"""


def calendar_exists(db: Session, calendar_id: int):
    """true if calendar of given id exists"""
    return True if db.get(models.Calendar, calendar_id) is not None else False


def calendar_is_owned(db: Session, calendar_id: int, subscriber_id: int):
    """check if calendar belongs to subscriber"""
    return (
        db.query(models.Calendar)
        .filter(models.Calendar.id == calendar_id, models.Calendar.owner_id == subscriber_id)
        .first()
        is not None
    )


def get_calendar(db: Session, calendar_id: int):
    """retrieve calendar by id"""
    return db.get(models.Calendar, calendar_id)


def calendar_is_connected(db: Session, calendar_id: int):
    """true if calendar of given id exists"""
    return get_calendar(db, calendar_id).connected


def get_calendar_by_url(db: Session, url: str):
    """retrieve calendar by calendar url"""
    return db.query(models.Calendar).filter(models.Calendar.url == url).first()


def get_calendars_by_subscriber(db: Session, subscriber_id: int, include_unconnected: bool = True):
    """retrieve list of calendars by owner id"""
    query = db.query(models.Calendar).filter(models.Calendar.owner_id == subscriber_id)

    if not include_unconnected:
        query = query.filter(models.Calendar.connected == 1)

    return query.all()


def create_subscriber_calendar(db: Session, calendar: schemas.CalendarConnection, subscriber_id: int):
    """create new calendar for owner, if not already existing"""
    db_calendar = models.Calendar(**calendar.dict(), owner_id=subscriber_id)
    subscriber_calendars = get_calendars_by_subscriber(db, subscriber_id)
    subscriber_calendar_urls = [c.url for c in subscriber_calendars]
    # check if subscriber already holds this calendar by url
    if db_calendar.url in subscriber_calendar_urls:
        raise HTTPException(status_code=403, detail="Calendar already exists")
    # add new calendar
    db.add(db_calendar)
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update_subscriber_calendar(db: Session, calendar: schemas.CalendarConnection, calendar_id: int):
    """update existing calendar by id"""
    db_calendar = get_calendar(db, calendar_id)

    # list of all attributes that must never be updated
    # # because they have dedicated update functions for security reasons
    ignore = ["connected", "connected_at"]
    # list of all attributes that will keep their current value if None is passed
    keep_if_none = ["password"]

    for key, value in calendar:
        # skip update, if attribute is ignored or current value should be kept if given value is falsey/empty
        if key in ignore or (key in keep_if_none and (not value or len(str(value)) == 0)):
            continue

        setattr(db_calendar, key, value)

    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update_subscriber_calendar_connection(db: Session, is_connected: bool, calendar_id: int):
    """Updates the connected status of a calendar"""
    db_calendar = get_calendar(db, calendar_id)
    # check subscription limitation on connecting
    if is_connected:
        subscriber_calendars = get_calendars_by_subscriber(db, db_calendar.owner_id)
        connected_calendars = [calendar for calendar in subscriber_calendars if calendar.connected]
        limit = get_connections_limit(db=db, subscriber_id=db_calendar.owner_id)
        if limit > 0 and len(connected_calendars) >= limit:
            raise HTTPException(
                status_code=403, detail="Allowed number of connected calendars has been reached for this subscription"
            )
    if not db_calendar.connected:
        db_calendar.connected_at = datetime.now()
    elif db_calendar.connected and is_connected is False:
        db_calendar.connected_at = None
    db_calendar.connected = is_connected
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


def update_or_create_subscriber_calendar(
    db: Session, calendar: schemas.CalendarConnection, calendar_url: str, subscriber_id: int
):
    """update or create a subscriber calendar"""
    subscriber_calendar = get_calendar_by_url(db, calendar_url)

    if subscriber_calendar is None:
        return create_subscriber_calendar(db, calendar, subscriber_id)

    return update_subscriber_calendar(db, calendar, subscriber_calendar.id)


def delete_subscriber_calendar(db: Session, calendar_id: int):
    """remove existing calendar by id"""
    db_calendar = get_calendar(db, calendar_id)
    db.delete(db_calendar)
    db.commit()
    return db_calendar


def delete_subscriber_calendar_by_subscriber_id(db: Session, subscriber_id: int):
    """Delete all calendars by subscriber"""
    calendars = get_calendars_by_subscriber(db, subscriber_id=subscriber_id)
    for calendar in calendars:
        delete_subscriber_calendar(db, calendar_id=calendar.id)
    return True


""" APPOINTMENT repository functions
"""


def create_calendar_appointment(db: Session, appointment: schemas.AppointmentFull, slots: list[schemas.SlotBase] = []):
    """create new appointment with slots for calendar"""
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    if len(slots) > 0:
        add_appointment_slots(db, slots, db_appointment.id)
    return db_appointment


def get_appointment(db: Session, appointment_id: int) -> models.Appointment|None:
    """retrieve appointment by id (private)"""
    if appointment_id:
        return db.get(models.Appointment, appointment_id)
    return None


def get_public_appointment(db: Session, slug: str):
    """retrieve appointment by appointment slug (public)"""
    if slug:
        return db.query(models.Appointment).filter(models.Appointment.slug == slug).first()
    return None


def get_appointments_by_subscriber(db: Session, subscriber_id: int):
    """retrieve list of appointments by owner id"""
    return db.query(models.Appointment).join(models.Calendar).filter(models.Calendar.owner_id == subscriber_id).all()


def appointment_is_owned(db: Session, appointment_id: int, subscriber_id: int):
    """check if appointment belongs to subscriber"""
    db_appointment = get_appointment(db, appointment_id)
    return calendar_is_owned(db, db_appointment.calendar_id, subscriber_id)


def appointment_has_slot(db: Session, appointment_id: int, slot_id: int):
    """check if appointment belongs to subscriber"""
    db_slot = get_slot(db, slot_id)
    return db_slot and db_slot.appointment_id == appointment_id


def update_calendar_appointment(
    db: Session,
    appointment: schemas.AppointmentFull,
    slots: list[schemas.SlotBase],
    appointment_id: int,
):
    """update existing appointment by id"""
    db_appointment = get_appointment(db, appointment_id)
    for key, value in appointment:
        setattr(db_appointment, key, value)
    db.commit()
    db.refresh(db_appointment)
    delete_appointment_slots(db, appointment_id)
    add_appointment_slots(db, slots, appointment_id)
    return db_appointment


def delete_calendar_appointment(db: Session, appointment_id: int):
    """remove existing appointment by id"""
    db_appointment = get_appointment(db, appointment_id)
    db.delete(db_appointment)
    db.commit()
    return db_appointment


def delete_calendar_appointments_by_subscriber_id(db: Session, subscriber_id: int):
    """Delete all appointments by subscriber"""
    appointments = get_appointments_by_subscriber(db, subscriber_id=subscriber_id)
    for appointment in appointments:
        delete_calendar_appointment(db, appointment_id=appointment.id)
    return True


def update_appointment_status(db: Session, appointment_id: int, status: models.AppointmentStatus):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        return False

    appointment.status = status
    db.commit()


""" SLOT repository functions
"""


def get_slot(db: Session, slot_id: int) -> models.Slot | None:
    """retrieve slot by id"""
    if slot_id:
        return db.get(models.Slot, slot_id)
    return None


def get_slots_by_subscriber(db: Session, subscriber_id: int):
    """retrieve slot by subscriber id"""

    # We need to walk through Calendars to attach Appointments, and Appointments to get Slots
    return (
        db.query(models.Slot)
        .join(models.Appointment)
        .join(models.Calendar)
        .filter(models.Calendar.owner_id == subscriber_id)
        .filter(models.Appointment.calendar_id == models.Calendar.id)
        .filter(models.Slot.appointment_id == models.Appointment.id)
        .all()
    )


def add_appointment_slots(db: Session, slots: list[schemas.SlotBase], appointment_id: int):
    """create new slots for appointment of given id"""
    for slot in slots:
        db_slot = models.Slot(**slot.dict())
        db_slot.appointment_id = appointment_id
        db.add(db_slot)
    db.commit()
    return slots


def add_schedule_slot(db: Session, slot: schemas.SlotBase, schedule_id: int):
    """create new slot for schedule of given id"""
    db_slot = models.Slot(**slot.dict())
    db_slot.schedule_id = schedule_id
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot


def schedule_slot_exists(db: Session, slot: schemas.SlotBase, schedule_id: int):
    """check if given slot already exists for schedule of given id"""
    db_slot = (
        db.query(models.Slot)
            .filter(models.Slot.schedule_id == schedule_id)
            .filter(models.Slot.start == slot.start)
            .filter(models.Slot.duration == slot.duration)
            .filter(models.Slot.booking_status != models.BookingStatus.none)
            .first()
    )
    return db_slot is not None


def book_slot(db: Session, slot_id: int) -> models.Slot | None:
    """update booking status for slot of given id"""
    db_slot = get_slot(db, slot_id)
    db_slot.booking_status = models.BookingStatus.booked
    db.commit()
    db.refresh(db_slot)
    return db_slot


def delete_appointment_slots(db: Session, appointment_id: int):
    """delete all slots for appointment of given id"""
    return db.query(models.Slot).filter(models.Slot.appointment_id == appointment_id).delete()


def delete_appointment_slots_by_subscriber_id(db: Session, subscriber_id: int):
    """Delete all slots by subscriber"""
    slots = get_slots_by_subscriber(db, subscriber_id)

    for slot in slots:
        db.delete(slot)
    db.commit()

    return True


def update_slot(db: Session, slot_id: int, attendee: schemas.Attendee):
    """update existing slot by id and create corresponding attendee"""
    # create attendee
    db_attendee = models.Attendee(**attendee.dict())
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    # update slot
    db_slot = get_slot(db, slot_id)
    # TODO: additionally handle subscriber_id here for already logged in users
    setattr(db_slot, "attendee_id", db_attendee.id)
    db.commit()
    return db_attendee


def delete_slot(db: Session, slot_id: int):
    """remove existing slot by id"""
    db_slot = get_slot(db, slot_id)
    db.delete(db_slot)
    db.commit()
    return db_slot


def slot_is_available(db: Session, slot_id: int):
    """check if slot is still available for booking"""
    slot = get_slot(db, slot_id)
    if slot.schedule:
        return slot and slot.booking_status == models.BookingStatus.requested
    return False


"""SCHEDULES repository functions
"""


def create_calendar_schedule(db: Session, schedule: schemas.ScheduleBase):
    """create new schedule with slots for calendar"""
    db_schedule = models.Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_schedules_by_subscriber(db: Session, subscriber_id: int):
    """Get schedules by subscriber id"""
    return (
        db.query(models.Schedule)
        .join(models.Calendar, models.Schedule.calendar_id == models.Calendar.id)
        .filter(models.Calendar.owner_id == subscriber_id)
        .all()
    )


def get_schedule(db: Session, schedule_id: int):
    """retrieve schedule by id"""
    if schedule_id:
        return db.get(models.Schedule, schedule_id)
    return None


def schedule_is_owned(db: Session, schedule_id: int, subscriber_id: int):
    """check if the given schedule belongs to subscriber"""
    schedules = get_schedules_by_subscriber(db, subscriber_id)
    return any(s.id == schedule_id for s in schedules)


def schedule_exists(db: Session, schedule_id: int):
    """true if schedule of given id exists"""
    return True if get_schedule(db, schedule_id) is not None else False


def update_calendar_schedule(db: Session, schedule: schemas.ScheduleBase, schedule_id: int):
    """update existing schedule by id"""
    db_schedule = get_schedule(db, schedule_id)
    for key, value in schedule:
        setattr(db_schedule, key, value)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_availability_by_schedule(db: Session, schedule_id: int):
    """retrieve availability by schedule id"""
    return db.query(models.Availability).filter(models.Availability.schedule_id == schedule_id).all()


def schedule_has_slot(db: Session, schedule_id: int, slot_id: int):
    """check if slot belongs to schedule"""
    db_slot = get_slot(db, slot_id)
    return db_slot and db_slot.schedule_id == schedule_id


"""INVITES repository functions
"""


def get_invite_by_code(db: Session, code: str):
    """retrieve invite by code"""
    return db.query(models.Invite).filter(models.Invite.code == code).first()


def generate_invite_codes(db: Session, n: int):
    """generate n invite codes and return the list of created invite objects"""
    codes = [str(uuid.uuid4()) for _ in range(n)]
    db_invites = []
    for code in codes:
        invite = schemas.Invite(code=code)
        db_invite = models.Invite(**invite.dict())
        db.add(db_invite)
        db.commit()
        db_invites.append(db_invite)
    return db_invites


def invite_code_exists(db: Session, code: str):
    """true if invite code exists"""
    return True if get_invite_by_code(db, code) is not None else False


def invite_code_is_used(db: Session, code: str):
    """true if invite code is assigned to a user"""
    db_invite = get_invite_by_code(db, code)
    return db_invite.is_used


def invite_code_is_revoked(db: Session, code: str):
    """true if invite code is revoked"""
    db_invite = get_invite_by_code(db, code)
    return db_invite.is_revoked


def invite_code_is_available(db: Session, code: str):
    """true if invite code exists and can still be used"""
    db_invite = get_invite_by_code(db, code)
    return db_invite and db_invite.is_available


def use_invite_code(db: Session, code: str, subscriber_id: int):
    """assign given subscriber to an invite"""
    db_invite = get_invite_by_code(db, code)
    if db_invite and db_invite.is_available:
        db_invite.subscriber_id = subscriber_id
        db.commit()
        db.refresh(db_invite)
        return True
    else:
        return False


def revoke_invite_code(db: Session, code: str):
    """set existing invite code status to revoked"""
    db_invite = get_invite_by_code(db, code)
    db_invite.status = models.InviteStatus.revoked
    db.commit()
    db.refresh(db_invite)
    return True


"""External Connections repository functions
"""


def create_subscriber_external_connection(db: Session, external_connection: ExternalConnection):
    db_external_connection = models.ExternalConnections(
        **external_connection.dict()
    )
    db.add(db_external_connection)
    db.commit()
    db.refresh(db_external_connection)
    return db_external_connection


def update_subscriber_external_connection_token(db: Session, token: str, subscriber_id: int, type: models.ExternalConnectionType, type_id: str | None = None):
    db_results = get_external_connections_by_type(db, subscriber_id, type, type_id)
    if db_results is None or len(db_results) == 0:
        return None

    db_external_connection = db_results[0]
    db_external_connection.token = token
    db.commit()
    db.refresh(db_external_connection)
    return db_external_connection


def delete_external_connections_by_type_id(db: Session, subscriber_id: int, type: models.ExternalConnectionType, type_id: str):
    connections = get_external_connections_by_type(db, subscriber_id, type, type_id)

    # There should be one by type id, but just in case..
    for connection in connections:
        db.delete(connection)
    db.commit()

    return True


def get_external_connections_by_type(db: Session, subscriber_id: int, type: models.ExternalConnectionType, type_id: str | None = None) -> list[models.ExternalConnections] | None:
    """Return a subscribers external connections by type, and optionally type id"""
    query = (
        db.query(models.ExternalConnections)
        .filter(models.ExternalConnections.owner_id == subscriber_id)
        .filter(models.ExternalConnections.type == type)
    )

    if type_id is not None:
        query = query.filter(models.ExternalConnections.type_id == type_id)

    result = query.all()

    return result


def get_subscriber_by_fxa_uid(db: Session, type_id: str):
    """Return a subscriber from a fxa profile uid"""
    query = (
        db.query(models.ExternalConnections)
        .filter(models.ExternalConnections.type == models.ExternalConnectionType.fxa)
        .filter(models.ExternalConnections.type_id == type_id)
    )

    result = query.first()

    if result is not None:
        return result.owner

    return None
