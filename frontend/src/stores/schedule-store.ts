import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useUserStore } from '@/stores/user-store';
import { Fetch, Schedule, ScheduleListResponse } from '@/models';

// eslint-disable-next-line import/prefer-default-export
export const useScheduleStore = defineStore('schedules', () => {
  // State
  const isLoaded = ref(false);

  // Data
  const schedules = ref<Schedule[]>([]);
  const inactiveSchedules = computed((): Schedule[] => schedules.value.filter((schedule) => !schedule.active));
  const activeSchedules = computed((): Schedule[] => schedules.value.filter((schedule) => schedule.active));

  /**
   * Get all calendars for current user
   * @param call preconfigured API fetch function
   * @param force Force a fetch even if we already have data
   */
  const fetch = async (call: Fetch, force: boolean = false) => {
    if (isLoaded.value && !force) {
      return;
    }

    const { data, error }: ScheduleListResponse = await call('schedule/').get().json();

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
