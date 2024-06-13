from appointment.database import models, repo, schemas


class TestAppointment:
    def test_appointment_uuids_are_unique(self, with_db, make_caldav_calendar):
        calendar = make_caldav_calendar()
        with with_db() as db:

            def get_data():
                return schemas.AppointmentFull(
                    title='test',
                    details='my appointment!',
                    calendar_id=calendar.id,
                )

            assert len(db.query(models.Appointment).all()) == 0

            appointments = [
                repo.appointment.create(db, get_data()),
                repo.appointment.create(db, get_data()),
                repo.appointment.create(db, get_data()),
                repo.appointment.create(db, get_data()),
            ]

            assert len(db.query(models.Appointment).all()) == len(appointments)

            for appointment in appointments:
                assert len(db.query(models.Appointment).filter(models.Appointment.uuid == appointment.uuid).all()) == 1
