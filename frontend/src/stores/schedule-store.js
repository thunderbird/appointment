import { i18n } from '@/composables/i18n';
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

  const handleErrorResponse = (responseData) => {
    const { value } = responseData;

    if (value?.detail?.message) {
      return value?.detail?.message;
    }

    if (value?.detail instanceof Array) {
      // TODO: Move logic to backend (https://github.com/thunderbird/appointment/issues/270)

      // List of fields to units
      const fieldUnits = {
        slot_duration: 'units.minutes',
        unknown: 'units.none',
      };

      // Create a list of localized error messages, this is temp code because it shouldn't live here.
      // We do a look-up on field, and the field's unit (if any) along with the error type.
      const errorDetails = value.detail.map((err) => {
        const field = err.loc[1] ?? 'unknown';
        const fieldLocalized = i18n.t(`fields.${field}`);
        let message = i18n.t('error.unknownScheduleError');

        if (err.type === 'greater_than_equal') {
          const contextValue = err.ctx.ge;
          const valueLocalized = i18n.t(fieldUnits[field] ?? 'units.none', { value: contextValue });

          message = i18n.t('error.minimumValue', {
            field: fieldLocalized,
            value: valueLocalized,
          });
        }

        return message;
      });

      return errorDetails.join('\n');
    }
    return i18n.t('error.unknownScheduleError');
  };

  const createSchedule = async (call, scheduleData) => {
    // save schedule data
    const { data, error } = await call('schedule/').post(scheduleData).json();

    if (error.value) {
      return {
        error: true,
        message: handleErrorResponse(data),
      };
    }

    // Update the schedule
    await fetch(call, true);

    return data;
  };

  const updateSchedule = async (call, id, scheduleData) => {
    // save schedule data
    const { data, error } = await call(`schedule/${id}`).put(scheduleData).json();

    if (error.value) {
      return {
        error: true,
        message: handleErrorResponse(data),
      };
    }

    // Update the schedule
    await fetch(call, true);

    return data;
  };

  return {
    isLoaded, schedules, inactiveSchedules, activeSchedules, fetch, $reset, createSchedule, updateSchedule,
  };
});
