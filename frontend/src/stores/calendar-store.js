import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

const initialData = {
  calendars: [],
  isInit: false,
};

// eslint-disable-next-line import/prefer-default-export
export const useCalendarStore = defineStore('calendars', () => {
  const data = ref(structuredClone(initialData));

  const isLoaded = computed(() => data.value.isInit);
  const unconnectedCalendars = computed(() => data.value.calendars.filter((cal) => !cal.connected));
  const connectedCalendars = computed(() => data.value.calendars.filter((cal) => cal.connected));
  const allCalendars = computed(() => data.value.calendars);

  const fetch = async (call) => {
    if (isLoaded.value) {
      return;
    }

    const { data: calData, error } = await call('me/calendars?only_connected=false').get().json();
    if (!error.value) {
      if (calData.value === null || typeof calData.value === 'undefined') return;
      data.value.calendars = calData.value;
      data.value.isInit = true;
    }
  };

  const reset = () => data.value = structuredClone(initialData);
  
  return { data, isLoaded, unconnectedCalendars, connectedCalendars, allCalendars, fetch, reset };
});
