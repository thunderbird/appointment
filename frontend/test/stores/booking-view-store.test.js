import {
  expect,
  test,
  beforeEach,
  describe,
  beforeAll,
  afterAll,
  afterEach,
} from 'vitest';
import { setupServer } from 'msw/node';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { createPinia } from 'pinia';
import { BookingCalendarView } from '@/definitions';
import withSetup from '../utils/with-setup';

const server = setupServer();

describe('Booking view Store', () => {
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
    const store = useBookingViewStore();
    expect(store.activeView).toBe(BookingCalendarView.Loading);
    expect(store.selectedEvent).toBeNull();
    expect(store.appointment).toBeNull();
    expect(store.attendee).toBeNull();
  });
  test('reset', () => {
    const store = useBookingViewStore();
    store.activeView = BookingCalendarView.Month;
    store.$reset();
    expect(store.activeView).toBe(BookingCalendarView.Loading);
  });
});
