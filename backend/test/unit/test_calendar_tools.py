from appointment.controller.calendar import Tools
from appointment.database import schemas, models
from datetime import datetime, timedelta


class TestTools:
    def test_events_roll_up_difference(self):
        start = datetime.now()
        duration = 30

        # 4x 30 minute slots, starting from now.
        appointment_slots = [
            schemas.SlotBase(
                start=start,
                duration=duration,
                booking_status=models.BookingStatus.requested,
            ),
            schemas.SlotBase(
                start=start + timedelta(minutes=duration),
                duration=duration,
                booking_status=models.BookingStatus.requested,
            ),
            schemas.SlotBase(
                start=start + timedelta(minutes=duration * 2),
                duration=duration,
                booking_status=models.BookingStatus.requested,
            ),
            schemas.SlotBase(
                start=start + timedelta(minutes=duration * 3),
                duration=duration,
                booking_status=models.BookingStatus.requested,
            ),
        ]

        # 3x 30 minute booked slots, two of the slots should combine to one hour busy slot
        event_slots = [
            schemas.Event(
                title="Extra Busy Time",
                start=start,
                end=start + timedelta(minutes=duration),
            ),
            schemas.Event(
                title="After meeting nap",
                start=start + timedelta(minutes=duration),
                end=start + timedelta(minutes=duration * 2),
            ),
            schemas.Event(
                title="Some other appointment",
                start=start + timedelta(minutes=duration * 3),
                end=start + timedelta(minutes=duration * 4),
            ),
        ]

        rolled_up_slots = Tools.events_roll_up_difference(appointment_slots, event_slots)

        assert rolled_up_slots[0].booking_status == models.BookingStatus.booked
        assert rolled_up_slots[1].booking_status == models.BookingStatus.requested
        assert rolled_up_slots[2].booking_status == models.BookingStatus.booked
