import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// const initialData = {
//   calendars: [],
//   isInit: false,
// };

// eslint-disable-next-line import/prefer-default-export
export const useCalendarStore = defineStore('calendars', () => {
  // const data = ref(structuredClone(initialData));

  // State
  const isLoaded = ref(false);

  // Data
  const calendars = ref([]);
  const unconnectedCalendars = computed(() => calendars.value.filter((cal) => !cal.connected));
  const connectedCalendars = computed(() => calendars.value.filter((cal) => cal.connected));

  // Get all calendars for current user
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

  const reset = () => {
    calendars.value = [];
    isLoaded.value = false;
  };
  
  return { isLoaded, calendars, unconnectedCalendars, connectedCalendars, fetch, reset };
});
