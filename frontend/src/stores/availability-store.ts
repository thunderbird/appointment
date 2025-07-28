import { Calendar, CalendarListResponse, Fetch } from '@/models';
import { defineStore } from 'pinia';
import { ref } from 'vue';


export const useAvailabilityStore = defineStore('availability', () => {
  const call = ref(null);

  // State
  const isLoaded = ref(false);

  // Data
  const calendars = ref<Calendar[]>([]);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

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
   * Restore default state
   */
  const $reset = () => {
    calendars.value = [];
    isLoaded.value = false;
  };

  return {
    isLoaded,
    init,
    fetch,
    $reset,
  };
});

export const createAvailabilityStore = (call: Fetch) => {
  const store = useAvailabilityStore();
  store.init(call);
  return store;
};
