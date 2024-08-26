import {
  expect,
  test,
  beforeEach,
  describe,
  beforeAll,
  afterAll,
  afterEach,
} from 'vitest';
import { useAppointmentStore } from '@/stores/appointment-store';
import { createPinia } from 'pinia';
import { setupServer } from 'msw/node';
import { HttpResponse, http } from 'msw';
import { createFetch } from '@vueuse/core';
import { BookingStatus } from '@/definitions';
import withSetup from '../utils/with-setup';

const API_URL = 'http://localhost';

const restHandlers = [
  http.get(`${API_URL}/me/appointments`, async () => HttpResponse.json([
    {
      calendar_id: 1,
      title: 'title',
      duration: 180,
      location_type: 2,
      slots: [
        { start: '3000-01-01T09:00:00Z', duration: 60, booking_status: BookingStatus.None },
      ],
    },
    {
      calendar_id: 1,
      title: 'title',
      duration: 180,
      location_type: 2,
      slots: [
        {
          start: '2024-01-01T09:00:00Z', duration: 60, attendee_id: 1, booking_status: BookingStatus.Requested,
        },
      ],
    },
  ])),
];

const server = setupServer(...restHandlers);
// server.events.on('request:start', ({ request }) => {
//   console.log('Outgoing:', request.method, request.url);
// });

describe('Appointment Store', () => {
  let app = null;

  // Create a pinia instance before each test
  beforeEach(() => {
    app = withSetup();
    app.use(createPinia());
  });
  // Start server before all tests
  beforeAll(() => server.listen());

  // Close server after all tests
  afterAll(() => server.close());

  // Reset handlers after each test `important for test isolation`
  afterEach(() => {
    server.resetHandlers();
    app?.unmount();
  });

  test('init', () => {
    const apmt = useAppointmentStore();
    expect(apmt.isLoaded).toBe(false);
    expect(apmt.appointments.length).toBe(0);
  });

  test('fetch', async () => {
    const apmt = useAppointmentStore();
    await apmt.fetch(createFetch({ baseUrl: API_URL }));
    console.log(apmt.appointments);
    expect(apmt.appointments.length).toBe(2);
    expect(apmt.appointments[0].slots.length).toBe(1);
  });

  test('pending', async () => {
    const apmt = useAppointmentStore();
    await apmt.fetch(createFetch({ baseUrl: API_URL }));
    expect(apmt.pendingAppointments.length).toBe(1);
  });

  test('timezone', async () => {
    const apmt = useAppointmentStore();
    await apmt.fetch(createFetch({ baseUrl: API_URL }));
    // TODO This check depends on the timzone set in the user store.
    // If no user timezone is set it defaults to UTC, which is currently the case.
    // So we might want to adjust the github workflow runner to set a timezone for testing.
    expect(apmt.appointments[0].slots[0].start.toISOString()).toBe('3000-01-01T09:00:00.000Z');
  });

  test('reset', async () => {
    const apmt = useAppointmentStore();
    await apmt.fetch(createFetch({ baseUrl: API_URL }));

    // Check if appointments exist
    expect(apmt.isLoaded).toBe(true);
    expect(apmt.appointments.length).toBe(2);

    // Reset the appointment which should null all appointment data.
    apmt.$reset();

    // Ensure our data is null/don't exist
    expect(apmt.isLoaded).toBe(false);
    expect(apmt.appointments.length).toBe(0);
  });
});
