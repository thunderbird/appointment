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
import { createPinia, setActivePinia } from 'pinia';
import { setupServer } from 'msw/node';
import { HttpResponse, http } from 'msw';
import { createFetch } from '@vueuse/core';

const API_URL = 'http://localhost';

const restHandlers = [
  http.get(`${API_URL}/me/appointments`, async (request) => {
    return HttpResponse.json([
      {
        calendar_id: 1,
        title: "title",
        duration: 180,
        location_type: 2,
        slots: [
          { start: "3000-01-01T09:00:00Z", duration: 60 },
          { start: "3000-01-01T11:00:00Z", duration: 15 },
          { start: "3000-01-01T15:00:00Z", duration: 275 },
        ],
      },
      {
        calendar_id: 1,
        title: "title",
        duration: 180,
        location_type: 2,
        slots: [
          { start: "2024-01-01T09:00:00Z", duration: 60 },
          { start: "2024-01-01T11:00:00Z", duration: 15, attendee_id: 1 },
          { start: "2024-01-01T15:00:00Z", duration: 275 },
        ],
      },
    ]);
  }),
];

const server = setupServer(...restHandlers);
server.events.on('request:start', ({ request }) => {
  // console.log('Outgoing:', request.method, request.url);
});

describe('Appointment Store', () => {
  // Create a pinia instance before each test
  beforeEach(() => {
    setActivePinia(createPinia());
  });
  // Start server before all tests
  beforeAll(() => server.listen());

  // Close server after all tests
  afterAll(() => server.close());

  // Reset handlers after each test `important for test isolation`
  afterEach(() => server.resetHandlers());


  test('init', () => {
    const apmt = useAppointmentStore();
    expect(apmt.isLoaded === false);
    expect(apmt.appointments.length === 0);
  });

  test('fetch', async () => {
    const apmt = useAppointmentStore();
    await apmt.fetch(createFetch({ baseUrl: API_URL }));
    expect(apmt.appointments.length === 2);
    expect(apmt.appointments[0].slots.length === 3);
  });

  test('pending', async () => {
    const apmt = useAppointmentStore();
    await apmt.fetch(createFetch({ baseUrl: API_URL }));
    expect(apmt.pendingAppointments.length === 1);
  });

  test('reset', async () => {
    const apmt = useAppointmentStore();
    await apmt.fetch(createFetch({ baseUrl: API_URL }));

    // Check if appointments exist
    expect(apmt.isLoaded === true);
    expect(apmt.appointments.length === 2);

    // Reset the user which should null all user data.
    apmt.reset();

    // Ensure our data is null/don't exist
    expect(apmt.isLoaded === false);
    expect(apmt.appointments.length === 0);
  });
});
