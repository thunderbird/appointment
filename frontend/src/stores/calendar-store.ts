import { Calendar, CalendarListResponse, Fetch } from '@/models';
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const useCalendarStore = defineStore('calendars', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const calendars = ref<Calendar[]>([]);
  const unconnectedCalendars = computed((): Calendar[] => calendars.value.filter((cal) => !cal.connected));
  const connectedCalendars = computed((): Calendar[] => calendars.value.filter((cal) => cal.connected));

  const hasConnectedCalendars = computed(() => connectedCalendars.value.length > 0);

  const connectGoogleCalendar = async (call: Fetch, email: string) => {
    const urlFriendlyEmail = encodeURIComponent(email);
    const googleUrl = await call(`google/auth?email=${urlFriendlyEmail}`).get();
    window.location.href = googleUrl.data.value.slice(1, -1);
  };

  /**
   * Retrieve the calendar object by id
   * @param id
   */
  const calendarById = (id: number) => calendars.value.filter((calendar) => calendar.id === id)?.at(0) ?? null;

  /**
   * Get all calendars for current user
   * @param call preconfigured API fetch function
   * @param force force a refetch
   */
  const fetch = async (call: Fetch, force = false) => {
    if (isLoaded.value && !force) {
      return;
    }

    const { data, error }: CalendarListResponse = await call('me/calendars?only_connected=false').get().json();
    if (!error.value) {
      if (data.value === null || typeof data.value === 'undefined') return;
      calendars.value = data.value;
      isLoaded.value = true;
    }
  };

  /**
   * Restore default state, empty and unload calendars
   */
  const $reset = () => {
    calendars.value = [];
    isLoaded.value = false;
  };

  const connectCalendar = async (call: Fetch, id: number) => {
    await call(`cal/${id}/connect`).post();
  };
  const disconnectCalendar = async (call: Fetch, id: number) => {
    await call(`cal/${id}/disconnect`).post();
  };
  const syncCalendars = async (call: Fetch) => {
    await call('rmt/sync').post();
  };

  return {
    isLoaded,
    hasConnectedCalendars,
    calendars,
    unconnectedCalendars,
    connectedCalendars,
    fetch,
    $reset,
    connectGoogleCalendar,
    connectCalendar,
    disconnectCalendar,
    syncCalendars,
    calendarById,
  };
});
