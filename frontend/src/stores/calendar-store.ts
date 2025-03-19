import { Calendar, CalendarListResponse, Fetch, RemoteEvent, RemoteEventListResponse } from '@/models';
import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { dayjsKey } from '@/keys';
import { Dayjs } from 'dayjs';
import { DateFormatStrings } from '@/definitions';

// eslint-disable-next-line import/prefer-default-export
export const useCalendarStore = defineStore('calendars', () => {
  const dj = inject(dayjsKey);
  const call = ref(null);

  // State
  const isLoaded = ref(false);

  // Data
  const calendars = ref<Calendar[]>([]);
  const unconnectedCalendars = computed((): Calendar[] => calendars.value.filter((cal) => !cal.connected));
  const connectedCalendars = computed((): Calendar[] => calendars.value.filter((cal) => cal.connected));
  const hasConnectedCalendars = computed(() => connectedCalendars.value.length > 0);

  // List of remote events. Retrieved in batches per month.
  const remoteEvents = ref<RemoteEvent[]>([]);
  // List of month batches already called.
  const remoteMonthsRetrieved = ref<string[]>([]);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  const connectGoogleCalendar = async (email: string) => {
    const urlFriendlyEmail = encodeURIComponent(email);
    const googleUrl = await call.value(`google/auth?email=${urlFriendlyEmail}`).get();
    window.location.href = googleUrl.data.value.slice(1, -1);
  };

  /**
   * Retrieve the calendar object by id
   * @param id
   */
  const calendarById = (id: number) => calendars.value.filter((calendar) => calendar.id === id)?.at(0) ?? null;

  /**
   * Get all calendars for current user
   * @param force force a refetch
   */
  const fetch = async (force = false) => {
    if (isLoaded.value && !force) {
      return;
    }

    const { data, error }: CalendarListResponse = await call.value('me/calendars?only_connected=false').get().json();
    if (!error.value) {
      if (data.value === null || typeof data.value === 'undefined') return;
      calendars.value = data.value;
      isLoaded.value = true;
    }
  };

  /**
   * Get all cremote events from connected calendars for given time span
   * @param activeDate Dayjs object defining the current month
   * @param force force a refetch
   */
  const getRemoteEvents = async (activeDate: Dayjs, force = false) => {
    // Get month identifier to remember this month's events are already retrieved
    const month = activeDate.format(DateFormatStrings.UniqueMonth);

    // Most calendar impl are non-inclusive of the last day, so just add one day to the end.
    const from = activeDate.startOf('month').format(DateFormatStrings.QalendarFullDay);
    const to = activeDate.endOf('month').add(1, 'day').format(DateFormatStrings.QalendarFullDay);

    // If retrieval is forced, delete cache and start with zero events again
    if (force) {
      remoteMonthsRetrieved.value = [];
    }

    // If month is already cached, there's nothing more to do
    if (remoteMonthsRetrieved.value.includes(month)) {
      return;
    }

    const calendarEvents = force ? [] : [...remoteEvents.value];

    // Only retrieve remote events if we don't have this month already cached
    await Promise.all(connectedCalendars.value.map(async (calendar) => {
      const { data }: RemoteEventListResponse = await call.value(`rmt/cal/${calendar.id}/${from}/${to}`).get().json();
      if (Array.isArray(data.value)) {
        calendarEvents.push(
          ...data.value.map((event) => ({
            ...event,
            duration: dj(event.end).diff(dj(event.start), 'minutes'),
          })),
        );
      }
    }));

    // Remember month
    remoteMonthsRetrieved.value.push(month);

    // Update remote event list
    remoteEvents.value = calendarEvents;
  };

  /**
   * Restore default state, empty and unload calendars
   */
  const $reset = () => {
    calendars.value = [];
    isLoaded.value = false;
  };

  const connectCalendar = async (id: number) => {
    await call.value(`cal/${id}/connect`).post();
  };

  const disconnectCalendar = async (id: number) => {
    await call.value(`cal/${id}/disconnect`).post();
  };

  const syncCalendars = async () => {
    await call.value('rmt/sync').post();
  };

  return {
    isLoaded,
    hasConnectedCalendars,
    calendars,
    unconnectedCalendars,
    connectedCalendars,
    remoteEvents,
    init,
    fetch,
    $reset,
    connectGoogleCalendar,
    connectCalendar,
    disconnectCalendar,
    syncCalendars,
    calendarById,
    getRemoteEvents,
  };
});

export const createCalendarStore = (call: Fetch) => {
  const store = useCalendarStore();
  store.init(call);
  return store;
};
