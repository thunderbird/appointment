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

  /**
   * Get all calendars for current user
   * @param call preconfigured API fetch function
   */
  const fetch = async (call: Fetch) => {
    if (isLoaded.value) {
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

  return {
    isLoaded, hasConnectedCalendars, calendars, unconnectedCalendars, connectedCalendars, fetch, $reset,
  };
});
