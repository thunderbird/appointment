import csv
import datetime
from io import StringIO, BytesIO
from zipfile import ZipFile

from ..database import repo, models
from ..database.schemas import Subscriber
from ..exceptions.account_api import AccountDeletionPartialFail, AccountDeletionSubscriberFail
from ..l10n import l10n


def model_to_csv_buffer(models):
    """Dumps a DeclarationBase model to csv and returns an in-memory buffer"""
    if len(models) == 0:
        return StringIO()

    # Don't write out these columns
    scrub_columns = ['password', 'google_tkn', 'google_state', 'google_state_expires_at', 'token']

    string_buffer = StringIO()

    writer = csv.writer(string_buffer)
    columns = list(filter(lambda c: c.name not in scrub_columns, models[0].__table__.c))

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
    attendees = repo.attendee.get_by_subscriber(db, subscriber_id=subscriber.id)
    appointments = repo.appointment.get_by_subscriber(db, subscriber_id=subscriber.id)
    calendars = repo.calendar.get_by_subscriber(db, subscriber_id=subscriber.id)
    subscribers = [subscriber]
    slots = repo.slot.get_by_subscriber(db, subscriber_id=subscriber.id)
    external_connections = subscriber.external_connections
    schedules = repo.schedule.get_by_subscriber(db, subscriber.id)
    availability = [repo.schedule.get_availability(db, schedule.id) for schedule in schedules]
    invite = repo.invite.get_by_subscriber(db, subscriber.id)
    invite_bucket = invite.invite_bucket

    # Convert models to csv
    attendee_buffer = model_to_csv_buffer(attendees)
    appointment_buffer = model_to_csv_buffer(appointments)
    calendar_buffer = model_to_csv_buffer(calendars)
    subscriber_buffer = model_to_csv_buffer(subscribers)
    slot_buffer = model_to_csv_buffer(slots)
    external_connections_buffer = model_to_csv_buffer(external_connections)
    schedules_buffer = model_to_csv_buffer(schedules)
    invite_buffer = model_to_csv_buffer([invite])
    invite_bucket_buffer = model_to_csv_buffer([invite_bucket])

    # Unique behaviour because we can have lists of lists..too annoying to not do it this way.
    availability_buffer = ''
    for avail in availability:
        availability_buffer += model_to_csv_buffer(avail).getvalue()

    # Create an in-memory zip and append our csvs
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as data_zip:
        data_zip.writestr('attendees.csv', attendee_buffer.getvalue())
        data_zip.writestr('appointments.csv', appointment_buffer.getvalue())
        data_zip.writestr('calendar.csv', calendar_buffer.getvalue())
        data_zip.writestr('subscriber.csv', subscriber_buffer.getvalue())
        data_zip.writestr('slot.csv', slot_buffer.getvalue())
        data_zip.writestr('external_connection.csv', external_connections_buffer.getvalue())
        data_zip.writestr('schedules.csv', schedules_buffer.getvalue())
        data_zip.writestr('availability.csv', availability_buffer)
        data_zip.writestr('invite.csv', invite_buffer.getvalue())
        data_zip.writestr('invite_bucket.csv', invite_bucket_buffer.getvalue())
        data_zip.writestr(
            'readme.txt', l10n('account-data-readme', {'download_time': datetime.datetime.now(datetime.UTC)})
        )

    # Return our zip buffer
    return zip_buffer


def delete_account(db, subscriber: Subscriber):
    # Ok nuke everything (thanks cascade=all,delete)
    repo.subscriber.hard_delete(db, subscriber)

    # Make sure we actually nuked the subscriber
    if repo.subscriber.get(db, subscriber.id) is not None:
        raise AccountDeletionSubscriberFail(
            subscriber.id,
            l10n('account-delete-fail'),
        )

    # A list of connected account data, if any value is True then we've failed
    empty_check = [
        len(repo.attendee.get_by_subscriber(db, subscriber.id)),
        len(repo.slot.get_by_subscriber(db, subscriber.id)),
        len(repo.appointment.get_by_subscriber(db, subscriber.id)),
        len(repo.calendar.get_by_subscriber(db, subscriber.id)),
        len(repo.schedule.get_by_subscriber(db, subscriber.id)),
        len(repo.external_connection.get_by_type(db, subscriber.id, models.ExternalConnectionType.fxa)),
        len(repo.external_connection.get_by_type(db, subscriber.id, models.ExternalConnectionType.google)),
        len(repo.external_connection.get_by_type(db, subscriber.id, models.ExternalConnectionType.zoom)),
        repo.invite.get_by_subscriber(db, subscriber.id),
        repo.invite.get_bucket_by_email(db, subscriber.email)
    ]

    # Check if we have any left-over subscriber data
    if any(empty_check) > 0:
        raise AccountDeletionPartialFail(
            subscriber.id,
            l10n('account-delete-fail'),
        )

    return True
