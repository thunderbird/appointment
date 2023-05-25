import csv
from io import StringIO, BytesIO
from zipfile import ZipFile

from ..database import repo
from ..database.schemas import Subscriber

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
    appointments = repo.get_appointments_by_subscriber(db, subscriber_id=subscriber.id)
    appointment_buffer = model_to_csv_buffer(appointments)

    print("Downloading:")

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, 'w') as data_zip:
        data_zip.writestr("appointments.csv", appointment_buffer.getvalue())

    print(appointment_buffer.read())

    return zip_buffer
