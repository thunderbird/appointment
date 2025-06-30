from appointment.controller.calendar import Tools
from appointment.database import schemas, models
from datetime import datetime, timedelta
from unittest.mock import Mock


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
                title='Extra Busy Time',
                start=start,
                end=start + timedelta(minutes=duration),
            ),
            schemas.Event(
                title='After meeting nap',
                start=start + timedelta(minutes=duration),
                end=start + timedelta(minutes=duration * 2),
            ),
            schemas.Event(
                title='Some other appointment',
                start=start + timedelta(minutes=duration * 3),
                end=start + timedelta(minutes=duration * 4),
            ),
        ]

        rolled_up_slots = Tools.events_roll_up_difference(appointment_slots, event_slots)

        assert rolled_up_slots[0].booking_status == models.BookingStatus.booked
        assert rolled_up_slots[1].booking_status == models.BookingStatus.requested
        assert rolled_up_slots[2].booking_status == models.BookingStatus.booked

    def test_existing_events_for_schedule_multiple_google_calendars(
        self, monkeypatch, with_db, make_pro_subscriber, make_google_calendar, make_external_connections, make_schedule
    ):
        subscriber = make_pro_subscriber()
        ec1 = make_external_connections(subscriber.id, type=models.ExternalConnectionType.google)
        ec2 = make_external_connections(subscriber.id, type=models.ExternalConnectionType.google)
        calendar1 = make_google_calendar(subscriber_id=subscriber.id, connected=True, external_connection_id=ec1.id)
        calendar2 = make_google_calendar(subscriber_id=subscriber.id, connected=True, external_connection_id=ec2.id)
        schedule = make_schedule(calendar_id=calendar1.id)

        with with_db() as db:
            # Refresh the schedule object to bind it to this session
            db.add(schedule)
            db.refresh(schedule)

            # Mock Google connector
            mock_connector_instance = Mock()
            mock_connector_instance.get_busy_time.return_value = [
                {'start': datetime.now(), 'end': datetime.now() + timedelta(hours=1)}
            ]
            mock_google_client = Mock()

            from appointment.controller.calendar import GoogleConnector
            monkeypatch.setattr(GoogleConnector, '__init__', lambda self, *a, **kw: None)
            monkeypatch.setattr(
                GoogleConnector, 'get_busy_time', lambda self, *a, **kw: mock_connector_instance.get_busy_time(*a, **kw)
            )

            events = Tools.existing_events_for_schedule(
                schedule=schedule,
                calendars=[calendar1, calendar2],
                subscriber=subscriber,
                google_client=mock_google_client,
                db=db,
                redis=None
            )

        # Should have busy time from both calendars
        assert len(events) == 2

        # Verify get_busy_time was called twice (once for each calendar)
        assert mock_connector_instance.get_busy_time.call_count == 2


class TestVCreate:
    def test_meeting_url_in_location(
        self,
        with_db,
        make_google_calendar,
        make_appointment,
        make_appointment_slot,
        make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)
        slot = appointment.slots[0]

        slot.meeting_link_url = 'https://thunderbird.net'

        ics = Tools().create_vevent(appointment, slot, subscriber)
        assert ics
        assert ':'.join(['LOCATION', slot.meeting_link_url]) in ics.decode()


class TestDnsCaldavLookup:
    def test_for_host(self):
        host, ttl = Tools.dns_caldav_lookup('thunderbird.net')
        assert host == 'https://apidata.googleusercontent.com:443/'
        assert ttl

    def test_for_txt_record(self):
        """This domain is used with permission from the owner (me, melissa autumn!)"""
        host, ttl = Tools.dns_caldav_lookup('melissaautumn.com')
        assert host == 'https://caldav.fastmail.com:443/dav/'
        assert ttl

    def test_no_records(self):
        host, ttl = Tools.dns_caldav_lookup('appointment.day')
        assert host is None
        assert ttl is None
