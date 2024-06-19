import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const useCalendarStore = defineStore('calendars', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const calendars = ref([]);
  const unconnectedCalendars = computed(() => calendars.value.filter((cal) => !cal.connected));
  const connectedCalendars = computed(() => calendars.value.filter((cal) => cal.connected));

  const hasConnectedCalendars = computed(() => connectedCalendars.value.length > 0);

  const connectGoogleCalendar = async (call, email) => {
    const urlFriendlyEmail = encodeURIComponent(email);
    const googleUrl = await call(`google/auth?email=${urlFriendlyEmail}`).get();
    window.location.href = googleUrl.data.value.slice(1, -1);
  };

  /**
   * Get all calendars for current user
   * @param {function} call preconfigured API fetch function
   */
  const fetch = async (call) => {
    if (isLoaded.value) {
      return;
    }

    const { data, error } = await call('me/calendars?only_connected=false').get().json();
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
    isLoaded, hasConnectedCalendars, calendars, unconnectedCalendars, connectedCalendars, fetch, $reset, connectGoogleCalendar,
  };
});
