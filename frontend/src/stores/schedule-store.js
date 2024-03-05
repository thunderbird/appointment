import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// eslint-disable-next-line import/prefer-default-export
export const useScheduleStore = defineStore('schedules', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const schedules = ref([]);
  const inactiveSchedules = computed(() => schedules.value.filter((schedule) => !schedule.active));
  const activeSchedules = computed(() => schedules.value.filter((schedule) => schedule.active));

  /**
   * Get all calendars for current user
   * @param {function} call preconfigured API fetch function
   */
  const fetch = async (call) => {
    if (isLoaded.value) {
      return;
    }

    const { data, error } = await call('schedule').get().json();
    if (!error.value) {
      if (data.value === null || typeof data.value === 'undefined') return;
      schedules.value = data.value;
      isLoaded.value = true;
    }
  };

  /**
   * Restore default state, empty and unload calendars
   */
  const $reset = () => {
    schedules.value = [];
    isLoaded.value = false;
  };

  return {
    isLoaded, schedules, inactiveSchedules, activeSchedules, fetch, $reset,
  };
});
