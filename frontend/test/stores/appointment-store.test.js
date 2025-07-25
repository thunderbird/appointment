import {
  expect,
  test,
  beforeEach,
  describe,
  beforeAll,
  afterAll,
  afterEach,
  vi,
} from 'vitest';
import { useAppointmentStore, createAppointmentStore } from '@/stores/appointment-store';
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
      id: 1,
      calendar_id: 1,
      title: 'title',
      duration: 180,
      location_type: 2,
      slots: [
        { start: '3000-01-01T09:00:00Z', duration: 60, booking_status: BookingStatus.None },
      ],
    },
    {
      id: 2,
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
  http.post(`${API_URL}/apmt/:id/cancel`, async () => {}),
  http.put(`${API_URL}/schedule/public/availability/booking`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      data: { confirmed: body.confirmed },
      error: { value: false },
    });
  }),
  http.put(`${API_URL}/apmt/:id/modify`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      error: { value: false },
      data: { ...body },
    });
  }),
  http.get(`${API_URL}/schedule/availability_for_day`, async ({ request }) => {
    const url = new URL(request.url);
    const date = url.searchParams.get('date');
    return HttpResponse.json({
      data: [{ slot: '09:00', date }],
      error: { value: false },
    });
  }),
];

const server = setupServer(...restHandlers);

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
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    await apmt.fetch();
    expect(apmt.appointments.length).toBe(2);
    expect(apmt.appointments[0].slots.length).toBe(1);
  });

  test('pending', async () => {
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    await apmt.fetch();
    expect(apmt.pendingAppointments.length).toBe(1);
  });

  test('timezone', async () => {
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    await apmt.fetch();
    expect(apmt.appointments[0].slots[0].start.toISOString()).toBe('3000-01-01T01:00:00.000Z');
  });

  test('reset', async () => {
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    await apmt.fetch();

    // Check if appointments exist
    expect(apmt.isLoaded).toBe(true);
    expect(apmt.appointments.length).toBe(2);

    // Reset the appointment which should null all appointment data.
    apmt.$reset();

    // Ensure our data is null/don't exist
    expect(apmt.isLoaded).toBe(false);
    expect(apmt.appointments.length).toBe(0);
  });

  test('cancel', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch');

    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    await apmt.fetch();

    // Cancel the first appointment
    await apmt.cancelAppointment(apmt.appointments[0].id);

    // Assert fetch was called with the correct endpoint
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining(`/apmt/${apmt.appointments[0].id}/cancel`),
      expect.objectContaining({
        method: 'POST',
      })
    );

    fetchSpy.mockRestore();
  });

  test('confirmOrDenyBooking', async () => {
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    await apmt.fetch();
    const result = await apmt.confirmOrDenyBooking({
      slotId: 123,
      slotToken: 'token',
      ownerUrl: 'owner-url',
      confirmed: true,
    });

    expect(result.error?.value ?? false).toBe(false);
    expect(result.data.value.data.confirmed).toBe(true);
  });

  test('modifyBookingAppointment', async () => {
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    await apmt.fetch();
    const result = await apmt.modifyBookingAppointment({
      appointmentId: 1,
      title: 'New Title',
      start: '2024-01-01T10:00:00Z',
      slotId: 456,
      notes: 'Some notes',
    });
    expect(result.error?.value ?? false).toBe(false);
    expect(result).toHaveProperty('error');
  });

  test('fetchAvailabilityForDay', async () => {
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));
    const { data, error } = await apmt.fetchAvailabilityForDay('2024-01-01');

    expect(error?.value ?? false).toBe(false);
    expect(Array.isArray(data.value.data)).toBe(true);
    expect(data.value.data[0]).toHaveProperty('slot', '09:00');
    expect(data.value.data[0]).toHaveProperty('date', '2024-01-01');
  });

  test('selectedAppointment is updated after fetch', async () => {
    const apmt = createAppointmentStore(createFetch({ baseUrl: API_URL }));

    apmt.selectedAppointment = { id: 1, title: 'old title', slots: [{}] };
    await apmt.fetch();

    // After fetch, selectedAppointment should be updated to the new appointment object with id 1
    expect(apmt.selectedAppointment).toBeDefined();
    expect(apmt.selectedAppointment.id).toBe(1);
    expect(apmt.selectedAppointment.title).toBe('title');

    // Should be the same object as in appointments array
    expect(apmt.selectedAppointment).toBe(apmt.appointments[0]);
  });
});
