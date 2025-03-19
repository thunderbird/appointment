import {
  expect,
  test,
  beforeEach,
  describe,
  beforeAll,
  afterAll,
  afterEach,
} from 'vitest';
import { useScheduleStore, createScheduleStore } from '@/stores/schedule-store';
import { createPinia } from 'pinia';
import { setupServer } from 'msw/node';
import { HttpResponse, http } from 'msw';
import { createFetch } from '@vueuse/core';
import { EventLocationType, DEFAULT_SLOT_DURATION, MeetingLinkProviderType } from '@/definitions';
import withSetup from '../utils/with-setup';

const API_URL = 'http://localhost';

const restHandlers = [
  http.get(`${API_URL}/schedule`, async () => HttpResponse.json([
    {
      active: false,
      name: '',
      calendar_id: 0,
      location_type: EventLocationType.InPerson,
      location_url: '',
      details: '',
      start_date: '2022-02-02',
      end_date: null,
      start_time: '09:00',
      end_time: '17:00',
      earliest_booking: 1440,
      farthest_booking: 20160,
      weekdays: [1, 2, 3, 4, 5],
      slot_duration: DEFAULT_SLOT_DURATION,
      meeting_link_provider: MeetingLinkProviderType.None,
      booking_confirmation: true,
      calendar: {
        id: 1,
        title: 'Cal',
        color: '#000',
        connected: true,
      },
      time_updated: '1970-01-01T00:00:00',
    },
  ])),
];

const server = setupServer(...restHandlers);

describe('Schedule Store', () => {
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
    const store = useScheduleStore();
    expect(store.isLoaded).toBe(false);
    expect(store.schedules.length).toBe(0);
  });

  test('fetch', async () => {
    const store = createScheduleStore(createFetch({ baseUrl: API_URL }));
    await store.fetch();
    expect(store.schedules.length).toBe(1);
    expect(store.schedules[0].calendar.id).toBe(1);
  });

  test('first', async () => {
    const store = createScheduleStore(createFetch({ baseUrl: API_URL }));
    expect(store.firstSchedule).toBeNull();
    await store.fetch();
    expect(store.firstSchedule.earliest_booking).toBe(1440);
  });

  test('inactive', async () => {
    const store = createScheduleStore(createFetch({ baseUrl: API_URL }));
    await store.fetch();
    expect(store.inactiveSchedules.length).toBe(1);
  });

  test('active', async () => {
    const store = createScheduleStore(createFetch({ baseUrl: API_URL }));
    await store.fetch();
    expect(store.activeSchedules.length).toBe(0);
  });

  test('reset', async () => {
    const store = createScheduleStore(createFetch({ baseUrl: API_URL }));
    await store.fetch();

    // Check if schedules exist
    expect(store.isLoaded).toBe(true);
    expect(store.schedules.length).toBe(1);

    // Reset the schedule which should null all schedule data.
    store.$reset();

    // Ensure our data is null/don't exist
    expect(store.isLoaded).toBe(false);
    expect(store.schedules.length).toBe(0);
  });
});
