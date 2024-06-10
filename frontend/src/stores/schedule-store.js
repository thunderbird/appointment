import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useUserStore } from '@/stores/user-store';

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
   * @param {boolean} force Force a fetch even if we already have data
   */
  const fetch = async (call, force = false) => {
    if (isLoaded.value && !force) {
      return;
    }

    const { data, error } = await call('schedule/').get().json();

    if (error.value || data.value === null || typeof data.value === 'undefined') {
      return;
    }

    schedules.value = data.value;
    isLoaded.value = true;

    const { updateScheduleUrls } = useUserStore();
    updateScheduleUrls(data.value);
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
