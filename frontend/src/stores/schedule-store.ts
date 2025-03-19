import { i18n } from '@/composables/i18n';
import { defineStore } from 'pinia';
import {
  ref, computed, inject, Ref,
} from 'vue';
import { useUserStore } from '@/stores/user-store';
import {
  DateFormatStrings,
  MetricEvents,
  DEFAULT_SLOT_DURATION,
  EventLocationType,
  MeetingLinkProviderType,
} from '@/definitions';
import {
  Error, Fetch, Schedule, ScheduleListResponse, ScheduleResponse, Exception, ExceptionDetail,
} from '@/models';
import { dayjsKey } from '@/keys';
import { posthog, usePosthog } from '@/composables/posthog';
import { timeFormat } from '@/utils';

// eslint-disable-next-line import/prefer-default-export
export const useScheduleStore = defineStore('schedules', () => {
  const dj = inject(dayjsKey);

  const defaultSchedule = {
    active: false,
    name: '',
    calendar_id: 0,
    location_type: EventLocationType.InPerson,
    location_url: '',
    details: '',
    start_date: dj().format(DateFormatStrings.QalendarFullDay),
    end_date: null,
    start_time: '09:00',
    end_time: '17:00',
    earliest_booking: 1440,
    farthest_booking: 20160,
    weekdays: [1, 2, 3, 4, 5],
    slot_duration: DEFAULT_SLOT_DURATION,
    meeting_link_provider: MeetingLinkProviderType.None,
    booking_confirmation: true,
    calendar: {
      id: 0,
      title: '',
      color: '#000',
      connected: true,
    },
    time_updated: '1970-01-01T00:00:00',
  } as Schedule;

  // State
  const isLoaded = ref(false);

  // Data
  const schedules = ref<Schedule[]>([]);
  const firstSchedule = computed((): Schedule => (schedules.value?.length > 0 ? schedules.value[0] : null));
  const inactiveSchedules = computed((): Schedule[] => schedules.value.filter((schedule) => !schedule.active));
  const activeSchedules = computed((): Schedule[] => schedules.value.filter((schedule) => schedule.active));

  const call = ref(null);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  /**
   * Get all schedules for current user
   * @param call preconfigured API fetch function
   * @param force Force a fetch even if we already have data
   */
  const fetch = async (force: boolean = false) => {
    if (isLoaded.value && !force) {
      return;
    }

    const { data, error }: ScheduleListResponse = await call.value('schedule/').get().json();

    if (error.value || data.value === null || typeof data.value === 'undefined') {
      return;
    }

    schedules.value = data.value;
    isLoaded.value = true;
  };

  /**
   * Restore default state, empty and unload schedules
   */
  const $reset = () => {
    schedules.value = [];
    isLoaded.value = false;
  };

  const handleErrorResponse = (responseData: Ref<Exception>) => {
    const { value } = responseData;

    if ((value?.detail as ExceptionDetail)?.message) {
      return (value?.detail as ExceptionDetail)?.message;
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
        } else if (err.type === 'string_pattern_mismatch') {
          message = i18n.t('error.noSpecialCharacters');
        } else if (err.type === 'end_time_before_start_time') {
          // TODO: Re-work how we do custom pydantic errors...
          // This is extremely specific because of locale and timezone concerns...
          const timeZoned = dj(err.ctx['err_value'], 'HH:mm:ss').utc(true).tz(dj.tz.guess());
          message = err.msg.replace('{field}', i18n.t('label.endTime'));
          message = message.replace('{value}', timeZoned.format(timeFormat()));
        }

        return message;
      });

      return errorDetails.join('\n');
    }
    return i18n.t('error.unknownScheduleError');
  };

  const createSchedule = async (scheduleData: object) => {
    // save schedule data
    const { data, error }: ScheduleResponse = await call.value('schedule/').post(scheduleData).json();

    if (error.value) {
      return {
        error: true,
        message: handleErrorResponse(data as Ref<Exception>),
      } as Error;
    }

    // Update the schedule
    await fetch(true);

    if (usePosthog) {
      posthog.capture(MetricEvents.ScheduleCreated);
    }

    return data;
  };

  const updateSchedule = async (id: number, scheduleData: object) => {
    // save schedule data
    const { data, error }: ScheduleResponse = await call.value(`schedule/${id}`).put(scheduleData).json();

    if (error.value) {
      return {
        error: true,
        message: handleErrorResponse(data as Ref<Exception>),
      } as Error;
    }

    // Update the schedule
    await fetch(true);

    if (usePosthog) {
      posthog.capture(MetricEvents.ScheduleUpdated);
    }

    return data;
  };

  /**
   * Converts a time (startTime or endTime) to a timezone that the backend expects
   * @param {string} time
   */
  const timeToBackendTime = (time: string) => {
    const dateFormat = DateFormatStrings.QalendarFullDay;

    const user = useUserStore();
    return dj(`${dj().format(dateFormat)}T${time}:00`)
      .tz(user.data.settings.timezone ?? dj.tz.guess(), true)
      .utc()
      .format('HH:mm');
  };

  /**
   * Converts a time (startTime or endTime) to the user's timezone from utc
   * BaseTime is needed for daylight savings awareness. If your time is coming from the backend's schedule route
   * then ensure you pass in schedule.time_updated as the baseTime!
   */
  const timeToFrontendTime = (time: string, baseTime: string) => {
    const dateFormat = DateFormatStrings.QalendarFullDay;
    const user = useUserStore();

    return dj(`${dj(baseTime).format(dateFormat)}T${time}:00`)
      .utc(true)
      .tz(user.data.settings.timezone ?? dj.tz.guess())
      .format('HH:mm');
  };

  return {
    isLoaded,
    defaultSchedule,
    schedules,
    firstSchedule,
    inactiveSchedules,
    activeSchedules,
    init,
    fetch,
    $reset,
    createSchedule,
    updateSchedule,
    timeToBackendTime,
    timeToFrontendTime,
  };
});

export const createScheduleStore = (call: Fetch) => {
  const store = useScheduleStore();
  store.init(call);
  return store;
};
