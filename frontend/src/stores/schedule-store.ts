import { i18n } from '@/composables/i18n';
import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { useUserStore } from '@/stores/user-store';
import { DateFormatStrings, MetricEvents } from '@/definitions';
import { Error, Fetch, Schedule, ScheduleListResponse,ScheduleResponse } from '@/models';
import { dayjsKey } from '@/keys';
import { posthog, usePosthog } from '@/composables/posthog';

// eslint-disable-next-line import/prefer-default-export
export const useScheduleStore = defineStore('schedules', () => {
  const dj = inject(dayjsKey);

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
        } else if (err.type === 'too_short' && field === 'weekdays') {
          message = i18n.t('error.selectOneDay');
        }

        return message;
      });

      return errorDetails.join('\n');
    }
    return i18n.t('error.unknownScheduleError');
  };

  const createSchedule = async (call: Fetch, scheduleData: object) => {
    // save schedule data
    const { data, error }: ScheduleResponse = await call('schedule/').post(scheduleData).json();

    if (error.value) {
      return {
        error: true,
        message: handleErrorResponse(data),
      } as Error;
    }

    // Update the schedule
    await fetch(call, true);

    if (usePosthog) {
      posthog.capture(MetricEvents.ScheduleCreated);
    }

    return data;
  };

  const updateSchedule = async (call: Fetch, id: number, scheduleData: object) => {
    // save schedule data
    const { data, error }: ScheduleResponse = await call(`schedule/${id}`).put(scheduleData).json();

    if (error.value) {
      return {
        error: true,
        message: handleErrorResponse(data),
      } as Error;
    }

    // Update the schedule
    await fetch(call, true);

    if (usePosthog) {
      posthog.capture(MetricEvents.ScheduleUpdated);
    }

    return data;
  };

  /**
   * Converts a time (startTime or endTime) to a timezone that the backend expects
   * @param {string} time
   */
  const timeToBackendTime = (time) => {
    const dateFormat = DateFormatStrings.QalendarFullDay;

    const user = useUserStore();
    return dj(`${dj().format(dateFormat)}T${time}:00`)
      .tz(user.data.timezone ?? dj.tz.guess(), true)
      .utc()
      .format('HH:mm');
  };

  /**
   * Converts a time (startTime or endTime) to the user's timezone from utc
   * @param {string} time
   */
  const timeToFrontendTime = (time) => {
    const dateFormat = DateFormatStrings.QalendarFullDay;
    const user = useUserStore();

    return dj(`${dj().format(dateFormat)}T${time}:00`)
      .utc(true)
      .tz(user.data.timezone ?? dj.tz.guess())
      .format('HH:mm');
  };

  return {
    isLoaded, schedules, inactiveSchedules, activeSchedules, fetch, $reset, createSchedule, updateSchedule, timeToBackendTime, timeToFrontendTime,
  };
});
