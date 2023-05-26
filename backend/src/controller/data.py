import csv
from io import StringIO, BytesIO
from zipfile import ZipFile

from ..database import repo
from ..database.schemas import Subscriber
from ..download_readme import get_download_readme
from ..exceptions.account_api import AccountDeletionPartialFail, AccountDeletionSubscriberFail


def model_to_csv_buffer(models):
    """Dumps a DeclarationBase model to csv and returns an in-memory buffer"""
    if len(models) == 0:
        return None

    string_buffer = StringIO()

    writer = csv.writer(string_buffer)
    columns = models[0].__table__.c

    writer.writerow(columns)
    for model in models:
        row = []
        for column in columns:
            row.append(getattr(model, column.name))
        writer.writerow(row)

    # Reset position
    string_buffer.seek(0)

    return string_buffer


def download(db, subscriber: Subscriber):
    """Generate a zip file of csvs that contain a copy of the subscriber's information."""
    attendees = repo.get_attendees_by_subscriber(db, subscriber_id=subscriber.id)
    appointments = repo.get_appointments_by_subscriber(db, subscriber_id=subscriber.id)
    calendars = repo.get_calendars_by_subscriber(db, subscriber_id=subscriber.id)
    subscribers = [subscriber]
    slots = repo.get_slots_by_subscriber(db, subscriber_id=subscriber.id)

    # Clear out the google token (?)
    subscribers[0].google_tkn = None

    # Convert models to csv
    attendee_buffer = model_to_csv_buffer(attendees)
    appointment_buffer = model_to_csv_buffer(appointments)
    calendar_buffer = model_to_csv_buffer(calendars)
    subscriber_buffer = model_to_csv_buffer(subscribers)
    slot_buffer = model_to_csv_buffer(slots)

    # Create an in-memory zip and append our csvs
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as data_zip:
        data_zip.writestr("attendees.csv", attendee_buffer.getvalue())
        data_zip.writestr("appointments.csv", appointment_buffer.getvalue())
        data_zip.writestr("calendar.csv", calendar_buffer.getvalue())
        data_zip.writestr("subscriber.csv", subscriber_buffer.getvalue())
        data_zip.writestr("slot.csv", slot_buffer.getvalue())
        data_zip.writestr("readme.txt", get_download_readme())

    # Return our zip buffer
    return zip_buffer


def delete_account(db, subscriber: Subscriber):
    # Ok nuke everything
    repo.delete_attendees_by_subscriber(db, subscriber.id)
    repo.delete_appointment_slots_by_subscriber_id(db, subscriber.id)
    repo.delete_calendar_appointments_by_subscriber_id(db, subscriber.id)
    repo.delete_subscriber_calendar_by_subscriber_id(db, subscriber.id)

    empty_check = [
        len(repo.get_attendees_by_subscriber(db, subscriber.id)),
        len(repo.get_slots_by_subscriber(db, subscriber.id)),
        len(repo.get_appointments_by_subscriber(db, subscriber.id)),
        len(repo.get_calendars_by_subscriber(db, subscriber.id)),
    ]

    # Check if we have any left-over subscriber data before we nuke the subscriber
    if any(empty_check) > 0:
        raise AccountDeletionPartialFail(
            subscriber.id,
            "There was a problem deleting your data. This incident has been logged and your data will manually be removed.",
        )

    repo.delete_subscriber(db, subscriber)

    # Make sure we actually nuked the subscriber
    if repo.get_subscriber(db, subscriber.id) is not None:
        raise AccountDeletionSubscriberFail(
            subscriber.id,
            "There was a problem deleting your data. This incident has been logged and your data will manually be removed.",
        )

    return True
