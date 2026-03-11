from appointment.controller.calendar import Tools, GoogleConnector
from appointment.database import schemas, models
from datetime import datetime, timedelta, time, date, timezone
from unittest.mock import Mock, MagicMock, PropertyMock
from starlette_context import request_cycle_context
from appointment.middleware.l10n import L10n

import pytest
import uuid
import zoneinfo


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
                redis=None,
            )

        # Should have busy time from both calendars
        assert len(events) == 2

        # Verify get_busy_time was called twice (once for each calendar)
        assert mock_connector_instance.get_busy_time.call_count == 2

    def test_existing_events_for_schedule_excludes_declined_cancelled_slots(
        self, monkeypatch, with_db, make_pro_subscriber, make_google_calendar, make_external_connections, make_schedule
    ):
        subscriber = make_pro_subscriber()
        ec = make_external_connections(subscriber.id, type=models.ExternalConnectionType.google)
        calendar = make_google_calendar(subscriber_id=subscriber.id, connected=True, external_connection_id=ec.id)
        schedule = make_schedule(calendar_id=calendar.id)
        now = datetime.now()

        with with_db() as db:
            # Create slots with different booking statuses
            slots = [
                models.Slot(schedule=schedule, start=now, duration=30, booking_status=models.BookingStatus.declined),
                models.Slot(
                    schedule=schedule,
                    start=now + timedelta(minutes=30),
                    duration=30,
                    booking_status=models.BookingStatus.cancelled,
                ),
                models.Slot(
                    schedule=schedule,
                    start=now + timedelta(minutes=60),
                    duration=30,
                    booking_status=models.BookingStatus.requested,
                ),
                models.Slot(
                    schedule=schedule,
                    start=now + timedelta(minutes=90),
                    duration=30,
                    booking_status=models.BookingStatus.booked,
                ),
            ]

            # Add slots to the database
            for slot in slots:
                db.add(slot)
            db.commit()

            # Refresh the schedule object to bind it to this session and load relationships
            db.add(schedule)
            db.refresh(schedule)

            # Mock Google connector to return no events
            mock_connector_instance = Mock()
            mock_connector_instance.get_busy_time.return_value = []
            mock_google_client = Mock()

            from appointment.controller.calendar import GoogleConnector

            monkeypatch.setattr(GoogleConnector, '__init__', lambda self, *a, **kw: None)
            monkeypatch.setattr(
                GoogleConnector, 'get_busy_time', lambda self, *a, **kw: mock_connector_instance.get_busy_time(*a, **kw)
            )

            events = Tools.existing_events_for_schedule(
                schedule=schedule,
                calendars=[calendar],
                subscriber=subscriber,
                google_client=mock_google_client,
                db=db,
                redis=None,
            )

        # Should only include requested and booked slots
        assert len(events) == 2

        # Verify the events correspond to the requested and booked slots
        event_times = sorted([event.start for event in events])
        assert event_times == [
            now + timedelta(minutes=60),  # requested slot
            now + timedelta(minutes=90),  # booked slot
        ]


class TestVCreate:
    def test_meeting_url_in_location(
        self, with_db, make_google_calendar, make_appointment, make_appointment_slot, make_pro_subscriber
    ):
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)
        slot = appointment.slots[0]

        slot.meeting_link_url = 'https://thunderbird.net'

        ics = Tools().create_vevent(appointment, slot, subscriber)
        assert ics
        assert ':'.join(['LOCATION', slot.meeting_link_url]) in ics.decode()

    def test_prodid_is_set(self, make_google_calendar, make_appointment, make_pro_subscriber):
        """Verify that the prodid is set correctly in the calendar"""
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)
        slot = appointment.slots[0]

        ics = Tools().create_vevent(appointment, slot, subscriber)
        ics_str = ics.decode()

        assert 'PRODID:-//thunderbird.net/Thunderbird Appointment//EN' in ics_str

    def test_attendee_with_name(self, make_google_calendar, make_appointment, make_pro_subscriber):
        """Verify attendee is added with name when slot has an attendee with a name"""
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)
        slot = appointment.slots[0]
        slot.attendee = models.Attendee(email='attendee@example.com', name='John Doe', timezone='Europe/Berlin')

        ics = Tools().create_vevent(appointment, slot, subscriber)
        ics_str = ics.decode()

        # Unfold lines (remove CRLF + leading space) and drop CR to keep assertions simple
        ics_str = ics_str.replace('\r\n ', '').replace('\r', '')

        assert 'ATTENDEE' in ics_str
        assert 'MAILTO:attendee@example.com' in ics_str
        assert 'CN="John Doe"' in ics_str
        assert 'ROLE=REQ-PARTICIPANT' in ics_str
        assert 'PARTSTAT=NEEDS-ACTION' in ics_str
        assert 'RSVP=TRUE' in ics_str
        assert 'CUTYPE=INDIVIDUAL' in ics_str

    def test_attendee_without_name_uses_email(self, make_google_calendar, make_appointment, make_pro_subscriber):
        """Verify attendee is added with email as name when slot has an attendee without a name"""
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)
        slot = appointment.slots[0]
        slot.attendee = models.Attendee(email='attendee@example.com', name=None, timezone='Europe/Berlin')

        ics = Tools().create_vevent(appointment, slot, subscriber)
        ics_str = ics.decode()

        # Unfold lines (remove CRLF + leading space) and drop CR to keep assertions simple
        ics_str = ics_str.replace('\r\n ', '').replace('\r', '')

        assert 'ATTENDEE' in ics_str
        assert 'MAILTO:attendee@example.com' in ics_str
        assert 'CN=attendee@example.com' in ics_str
        assert 'ROLE=REQ-PARTICIPANT' in ics_str
        assert 'PARTSTAT=NEEDS-ACTION' in ics_str
        assert 'RSVP=TRUE' in ics_str
        assert 'CUTYPE=INDIVIDUAL' in ics_str

    def test_no_attendee(self, make_google_calendar, make_appointment, make_pro_subscriber):
        """Verify no attendee is added when slot has no attendee"""
        subscriber = make_pro_subscriber()
        calendar = make_google_calendar(subscriber_id=subscriber.id)
        appointment = make_appointment(calendar_id=calendar.id)
        slot = appointment.slots[0]
        slot.attendee = None

        ics = Tools().create_vevent(appointment, slot, subscriber)
        ics_str = ics.decode()

        # The ATTENDEE field should not be present when there's no attendee
        assert 'ATTENDEE' not in ics_str


class TestDnsCaldavLookup:
    def test_for_host(self):
        host, ttl = Tools.dns_caldav_lookup('thunderbird.net')
        assert host == 'https://apidata.googleusercontent.com:443/'
        assert ttl

    def test_for_txt_record(self):
        host, ttl = Tools.dns_caldav_lookup('thundermail.com')
        assert host == 'https://mail.thundermail.com:443/dav/cal/'
        assert ttl

    def test_no_records(self):
        host, ttl = Tools.dns_caldav_lookup('appointment.day')
        assert host is None
        assert ttl is None


class TestAvailableSlotsFromSchedule:
    """Tests for Tools.available_slots_from_schedule"""

    def _create_mock_schedule(
        self,
        start_time_local: time,
        end_time_local: time,
        slot_duration: int,
        weekdays: list[int] = None,
        timezone_str: str = 'UTC',
    ):
        """Helper to create a mock schedule with the necessary properties"""
        if weekdays is None:
            weekdays = [1, 2, 3, 4, 5]

        # Create mock subscriber with timezone
        subscriber = Mock()
        subscriber.timezone = timezone_str

        # Create mock calendar with owner
        calendar = Mock()
        calendar.owner = subscriber

        # Create mock schedule
        schedule = Mock()
        schedule.calendar = calendar
        schedule.availabilities = []
        schedule.use_custom_availabilities = False
        schedule.weekdays = weekdays
        schedule.slot_duration = slot_duration
        schedule.earliest_booking = 0  # No minimum booking time
        schedule.farthest_booking = 60 * 24 * 7  # 1 week in minutes
        schedule.start_date = date.today()
        schedule.end_date = date.today() + timedelta(days=7)

        # Mock the local time properties
        type(schedule).start_time_local = PropertyMock(return_value=start_time_local)
        type(schedule).end_time_local = PropertyMock(return_value=end_time_local)

        return schedule

    def test_slots_fit_exactly_in_availability_window(self):
        """Test when slot duration divides evenly into availability window"""
        # 9:00 AM to 10:00 AM = 60 minutes, with 30 minute slots = exactly 2 slots
        schedule = self._create_mock_schedule(
            start_time_local=time(9, 0),
            end_time_local=time(10, 0),
            slot_duration=30,
            weekdays=[1, 2, 3, 4, 5, 6, 7],  # All days
        )

        # Test for a specific day (use a Monday)
        test_day = datetime(2026, 1, 26, tzinfo=zoneinfo.ZoneInfo('UTC'))  # A Monday
        slots = Tools.available_slots_from_schedule(schedule, day=test_day)

        assert len(slots) == 2
        # First slot at 9:00, ends at 9:30
        assert slots[0].start.hour == 9
        assert slots[0].start.minute == 0
        assert slots[0].duration == 30
        # Second slot at 9:30, ends at 10:00
        assert slots[1].start.hour == 9
        assert slots[1].start.minute == 30
        assert slots[1].duration == 30

    def test_last_slot_does_not_exceed_availability_end(self):
        """Ensure last slot doesn't exceed the availability end time"""
        # 9:00 AM to 9:40 AM = 40 minutes, with 30 minute slots
        # Should only generate 1 slot at 9:00 (ends at 9:30, within 9:40)
        schedule = self._create_mock_schedule(
            start_time_local=time(9, 0),
            end_time_local=time(9, 40),
            slot_duration=30,
            weekdays=[1, 2, 3, 4, 5, 6, 7],
        )

        test_day = datetime(2026, 1, 26, tzinfo=zoneinfo.ZoneInfo('UTC'))
        slots = Tools.available_slots_from_schedule(schedule, day=test_day)

        assert len(slots) == 1
        assert slots[0].start.hour == 9
        assert slots[0].start.minute == 0
        # Verify the slot end time (start + duration) doesn't exceed 9:40
        slot_end = slots[0].start + timedelta(minutes=slots[0].duration)
        assert slot_end.hour == 9
        assert slot_end.minute == 30  # 9:30 is before 9:40

    def test_availability_too_short_for_any_slot(self):
        """Test when availability window is shorter than slot duration"""
        # 9:00 AM to 9:20 AM = 20 minutes, with 30 minute slots = no slots possible
        schedule = self._create_mock_schedule(
            start_time_local=time(9, 0),
            end_time_local=time(9, 20),
            slot_duration=30,
            weekdays=[1, 2, 3, 4, 5, 6, 7],
        )

        test_day = datetime(2026, 1, 26, tzinfo=zoneinfo.ZoneInfo('UTC'))
        slots = Tools.available_slots_from_schedule(schedule, day=test_day)

        assert len(slots) == 0

    def test_exactly_one_slot_fits(self):
        """Test when exactly one slot fits in the availability window"""
        # 9:00 AM to 9:30 AM = 30 minutes, with 30 minute slots = exactly 1 slot
        schedule = self._create_mock_schedule(
            start_time_local=time(9, 0),
            end_time_local=time(9, 30),
            slot_duration=30,
            weekdays=[1, 2, 3, 4, 5, 6, 7],
        )

        test_day = datetime(2026, 1, 26, tzinfo=zoneinfo.ZoneInfo('UTC'))
        slots = Tools.available_slots_from_schedule(schedule, day=test_day)

        assert len(slots) == 1
        assert slots[0].start.hour == 9
        assert slots[0].start.minute == 0

    def test_multiple_slots_with_remainder(self):
        """Test multiple slots when there's leftover time that doesn't fit another slot"""
        # 9:00 AM to 10:15 AM = 75 minutes, with 30 minute slots
        # Should generate 2 slots (60 minutes used), 15 minutes remainder can't fit a 30-min slot
        schedule = self._create_mock_schedule(
            start_time_local=time(9, 0),
            end_time_local=time(10, 15),
            slot_duration=30,
            weekdays=[1, 2, 3, 4, 5, 6, 7],
        )

        test_day = datetime(2026, 1, 26, tzinfo=zoneinfo.ZoneInfo('UTC'))
        slots = Tools.available_slots_from_schedule(schedule, day=test_day)

        assert len(slots) == 2

        # Verify no slot exceeds 10:15
        for slot in slots:
            slot_end = slot.start + timedelta(minutes=slot.duration)
            assert slot_end <= test_day.replace(hour=10, minute=15)

    def test_respects_weekday_filter(self):
        """Test that slots are only generated for specified weekdays"""
        schedule = self._create_mock_schedule(
            start_time_local=time(9, 0),
            end_time_local=time(10, 0),
            slot_duration=30,
            weekdays=[1],  # Monday only
        )

        # Test on a Monday (should have slots)
        monday = datetime(2026, 1, 26, tzinfo=zoneinfo.ZoneInfo('UTC'))
        slots_monday = Tools.available_slots_from_schedule(schedule, day=monday)
        assert len(slots_monday) == 2

        # Test on a Tuesday (should have no slots)
        tuesday = datetime(2026, 1, 27, tzinfo=zoneinfo.ZoneInfo('UTC'))
        slots_tuesday = Tools.available_slots_from_schedule(schedule, day=tuesday)
        assert len(slots_tuesday) == 0


class TestGoogleConnectorSaveEvent:
    """Tests for GoogleConnector.save_event with import_() and insert() paths."""

    def _make_connector(self, mock_google_client):
        connector = GoogleConnector.__new__(GoogleConnector)
        connector.google_client = mock_google_client
        connector.remote_calendar_id = 'cal@example.com'
        connector.google_token = None
        connector.subscriber_id = 1
        connector.calendar_id = 1
        connector.redis_instance = None
        return connector

    def _make_event_and_organizer(self):
        organizer = Mock(spec=['name', 'email', 'language'])
        organizer.name = 'Owner'
        organizer.email = 'owner@example.com'
        organizer.language = 'en'

        attendee = schemas.AttendeeBase(email='bookee@example.org', name='Hans', timezone='Europe/Berlin')

        event = schemas.Event(
            title='Test Appointment',
            start=datetime(2024, 4, 1, 9, 0),
            end=datetime(2024, 4, 1, 9, 30),
            description='Some details',
            location=schemas.EventLocation(url='https://meet.example.com', phone='+1234567890'),
            uuid=uuid.uuid4(),
        )

        return event, attendee, organizer

    def test_description_uses_organizer_language_not_context(self):
        """When the request context is German but the organizer speaks English,
        the 'join-online' and 'join-phone' strings in the event description
        must be in English."""

        l10n_plugin = L10n()
        l10n_fn = l10n_plugin.get_fluent_with_header('de')

        event, attendee, organizer = self._make_event_and_organizer()

        mock_google_client = Mock()
        mock_google_client.save_event.return_value = {'id': 'mock_event_id'}
        connector = self._make_connector(mock_google_client)

        with request_cycle_context({'l10n': l10n_fn}):
            connector.save_event(
                event=event,
                attendee=attendee,
                organizer=organizer,
                organizer_email='owner@example.com',
            )

        call_kwargs = mock_google_client.save_event.call_args
        body = call_kwargs.kwargs.get('body') or call_kwargs[1].get('body')
        description = body['description']

        assert 'Join online at:' in description
        assert 'Join by phone:' in description
        assert 'Online teilnehmen unter:' not in description
        assert 'Per Telefon teilnehmen:' not in description

    def test_default_uses_import(self):
        """By default (send_google_notification=False), save_event uses import_()."""
        event, attendee, organizer = self._make_event_and_organizer()

        mock_google_client = Mock()
        mock_google_client.save_event.return_value = {'id': 'import_event_id'}
        connector = self._make_connector(mock_google_client)

        with request_cycle_context({}):
            result = connector.save_event(
                event=event,
                attendee=attendee,
                organizer=organizer,
                organizer_email='owner@example.com',
            )

        mock_google_client.save_event.assert_called_once()
        mock_google_client.insert_event.assert_not_called()

        body = mock_google_client.save_event.call_args.kwargs.get('body')
        assert 'iCalUID' in body
        assert result.external_id == 'import_event_id'

    def test_google_notification_uses_insert(self):
        """When send_google_notification=True, save_event uses insert_event()."""
        event, attendee, organizer = self._make_event_and_organizer()

        mock_google_client = Mock()
        mock_google_client.insert_event.return_value = {'id': 'insert_event_id'}
        connector = self._make_connector(mock_google_client)

        with request_cycle_context({}):
            result = connector.save_event(
                event=event,
                attendee=attendee,
                organizer=organizer,
                organizer_email='owner@example.com',
                send_google_notification=True,
            )

        mock_google_client.insert_event.assert_called_once()
        mock_google_client.save_event.assert_not_called()

        body = mock_google_client.insert_event.call_args.kwargs.get('body')
        assert 'iCalUID' not in body
        assert result.external_id == 'insert_event_id'

    def test_insert_body_has_no_organizer_field(self):
        """insert() body should not include the custom organizer field."""
        event, attendee, organizer = self._make_event_and_organizer()

        mock_google_client = Mock()
        mock_google_client.insert_event.return_value = {'id': 'insert_event_id'}
        connector = self._make_connector(mock_google_client)

        with request_cycle_context({}):
            connector.save_event(
                event=event,
                attendee=attendee,
                organizer=organizer,
                organizer_email='owner@example.com',
                send_google_notification=True,
            )

        body = mock_google_client.insert_event.call_args.kwargs.get('body')
        assert 'organizer' not in body

    def test_booking_confirmation_true_creates_tentative_with_both_needsaction(self):
        """With booking_confirmation=True, event is tentative and both
        organizer and bookee are listed as needsAction."""
        event, attendee, organizer = self._make_event_and_organizer()

        mock_google_client = Mock()
        mock_google_client.insert_event.return_value = {'id': 'tentative_id'}
        connector = self._make_connector(mock_google_client)

        with request_cycle_context({}):
            connector.save_event(
                event=event,
                attendee=attendee,
                organizer=organizer,
                organizer_email='owner@example.com',
                send_google_notification=True,
                booking_confirmation=True,
            )

        body = mock_google_client.insert_event.call_args.kwargs.get('body')
        assert body['status'] == 'tentative'

        attendees = body['attendees']
        assert len(attendees) == 2
        assert attendees[0]['email'] == 'owner@example.com'
        assert attendees[0]['responseStatus'] == 'needsAction'
        assert attendees[1]['email'] == 'bookee@example.org'
        assert attendees[1]['responseStatus'] == 'needsAction'

    def test_booking_confirmation_false_creates_confirmed_with_organizer_accepted(self):
        """With booking_confirmation=False, event is confirmed and the
        organizer is accepted while the bookee is needsAction."""
        event, attendee, organizer = self._make_event_and_organizer()

        mock_google_client = Mock()
        mock_google_client.insert_event.return_value = {'id': 'confirmed_id'}
        connector = self._make_connector(mock_google_client)

        with request_cycle_context({}):
            connector.save_event(
                event=event,
                attendee=attendee,
                organizer=organizer,
                organizer_email='owner@example.com',
                send_google_notification=True,
                booking_confirmation=False,
            )

        body = mock_google_client.insert_event.call_args.kwargs.get('body')
        assert body['status'] == 'confirmed'

        attendees = body['attendees']
        assert len(attendees) == 2
        assert attendees[0]['email'] == 'owner@example.com'
        assert attendees[0]['responseStatus'] == 'accepted'
        assert attendees[1]['email'] == 'bookee@example.org'
        assert attendees[1]['responseStatus'] == 'needsAction'


class TestVEventTimezoneFallback:
    """Tests that send_*_vevent methods fall back to UTC for invalid timezones."""

    def _make_tools(self):
        tools = Tools.__new__(Tools)
        return tools

    def _make_slot(self):
        return schemas.SlotBase(
            start=datetime(2026, 3, 15, 14, 0, 0),
            duration=30,
            booking_status=models.BookingStatus.requested,
        )

    def _make_organizer(self):
        organizer = Mock()
        organizer.name = 'Test Organizer'
        organizer.email = 'organizer@example.com'
        return organizer

    def _make_appointment(self):
        return Mock()

    def _make_attendee(self, tz='America/New_York'):
        return schemas.AttendeeBase(email='attendee@example.com', name='Attendee', timezone=tz)

    @pytest.mark.parametrize('method_name,email_func_path', [
        ('send_invitation_vevent', 'appointment.controller.mailer.send_invite_email'),
        ('send_hold_vevent', 'appointment.controller.mailer.send_pending_email'),
        ('send_reject_vevent', 'appointment.controller.mailer.send_rejection_email'),
        ('send_cancel_vevent', 'appointment.controller.mailer.send_cancel_email'),
    ])
    def test_valid_timezone_is_applied(self, method_name, email_func_path):
        tools = self._make_tools()
        tools.create_vevent = Mock(return_value=b'VCALENDAR')
        bg = MagicMock()
        slot = self._make_slot()
        attendee = self._make_attendee('America/New_York')

        method = getattr(tools, method_name)
        method(bg, self._make_appointment(), slot, self._make_organizer(), attendee)

        bg.add_task.assert_called_once()
        call_kwargs = bg.add_task.call_args
        date_arg = call_kwargs.kwargs.get('date') or call_kwargs[1].get('date')
        expected = slot.start.replace(tzinfo=timezone.utc).astimezone(zoneinfo.ZoneInfo('America/New_York'))
        assert date_arg == expected

    @pytest.mark.parametrize('method_name,email_func_path', [
        ('send_invitation_vevent', 'appointment.controller.mailer.send_invite_email'),
        ('send_hold_vevent', 'appointment.controller.mailer.send_pending_email'),
        ('send_reject_vevent', 'appointment.controller.mailer.send_rejection_email'),
        ('send_cancel_vevent', 'appointment.controller.mailer.send_cancel_email'),
    ])
    @pytest.mark.parametrize('bad_tz', ['Invalid/Timezone', 'Not_A_Zone', ''])
    def test_invalid_timezone_falls_back_to_utc(self, method_name, email_func_path, bad_tz):
        tools = self._make_tools()
        tools.create_vevent = Mock(return_value=b'VCALENDAR')
        bg = MagicMock()
        slot = self._make_slot()
        attendee = self._make_attendee(bad_tz)

        method = getattr(tools, method_name)
        method(bg, self._make_appointment(), slot, self._make_organizer(), attendee)

        bg.add_task.assert_called_once()
        call_kwargs = bg.add_task.call_args
        date_arg = call_kwargs.kwargs.get('date') or call_kwargs[1].get('date')
        expected = slot.start.replace(tzinfo=timezone.utc)
        assert date_arg == expected
        assert date_arg.tzinfo == timezone.utc

    @pytest.mark.parametrize('method_name', [
        'send_invitation_vevent',
        'send_hold_vevent',
        'send_reject_vevent',
        'send_cancel_vevent',
    ])
    def test_none_timezone_defaults_to_utc(self, method_name):
        tools = self._make_tools()
        tools.create_vevent = Mock(return_value=b'VCALENDAR')
        bg = MagicMock()
        slot = self._make_slot()
        attendee = self._make_attendee(tz=None)

        method = getattr(tools, method_name)
        method(bg, self._make_appointment(), slot, self._make_organizer(), attendee)

        bg.add_task.assert_called_once()
        call_kwargs = bg.add_task.call_args
        date_arg = call_kwargs.kwargs.get('date') or call_kwargs[1].get('date')
        assert date_arg.tzinfo is not None

