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
  
  return { isLoaded, calendars, unconnectedCalendars, connectedCalendars, fetch, $reset };
});
