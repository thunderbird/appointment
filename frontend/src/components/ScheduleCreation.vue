<script setup lang="ts">
import {
  DEFAULT_SLOT_DURATION, SLOT_DURATION_OPTIONS,
  DateFormatStrings, EventLocationType, MeetingLinkProviderType, ScheduleCreationState,
} from '@/definitions';
import {
  Calendar, Schedule, Slot, ScheduleAppointment, Error, SelectOption, Alert,
} from '@/models';
import {
  ref, reactive, computed, inject, watch, onMounted, Ref,
} from 'vue';
import { Dayjs } from 'dayjs';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import {
  dayjsKey, callKey, isoWeekdaysKey,
} from '@/keys';

import AppointmentCreatedModal from '@/components/AppointmentCreatedModal.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import AlertBox from '@/elements/AlertBox.vue';
import ToolTip from '@/elements/ToolTip.vue';
import SnackishBar from '@/elements/SnackishBar.vue';
import SwitchToggle from '@/tbpro/elements/SwitchToggle.vue';
import BubbleSelect from '@/tbpro/elements/BubbleSelect.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import CheckboxInput from '@/tbpro/elements/CheckboxInput.vue';
import SelectInput from '@/tbpro/elements/SelectInput.vue';
import LinkButton from '@/tbpro/elements/LinkButton.vue';
import RefreshIcon from '@/tbpro/icons/RefreshIcon.vue';
import CopyIcon from '@/tbpro/icons/CopyIcon.vue';

// icons
import { IconChevronDown, IconInfoCircle } from '@tabler/icons-vue';

// stores
import { useCalendarStore } from '@/stores/calendar-store';
import { createExternalConnectionsStore } from '@/stores/external-connections-store';
import { createScheduleStore } from '@/stores/schedule-store';
import router from '@/router';

// component constants
const call = inject(callKey);
const user = useUserStore();
const calendarStore = useCalendarStore();
const externalConnectionStore = createExternalConnectionsStore(call);
const scheduleStore = createScheduleStore(call);
const { t } = useI18n();
const dj = inject(dayjsKey);
const isoWeekdays = inject(isoWeekdaysKey);
const dateFormat = DateFormatStrings.QalendarFullDay;
const firstStep = ScheduleCreationState.Availability;

// component emits
const emit = defineEmits(['created', 'updated']);

const hasZoomAccount = computed(() => externalConnectionStore.zoom[0]);

// component properties
interface Props {
  calendars: Calendar[], // list of user defined calendars
  schedule: Schedule, // existing schedule to update or null
  activeDate: Dayjs, // dayjs object indicating the currently active calendar view date
}
const props = defineProps<Props>();

// check if existing schedule is given
const existing = computed(() => Boolean(props.schedule) && Boolean(props.schedule.calendar.connected));

// schedule creation state indicating the current step
const state = ref(firstStep);

// calculate the current visible step by given status
// first step are the general details
// second step is the availability configuration
// third step are the booking settings
const activeStep1 = computed(() => state.value === firstStep);
const activeStep2 = computed(() => state.value === ScheduleCreationState.Settings);
const activeStep3 = computed(() => state.value === ScheduleCreationState.Details);
const activeStep4 = computed(() => state.value === ScheduleCreationState.Booking);
const visitedStep1 = ref(false);

// calculate calendar titles
const calendarTitles = computed(() => {
  const calendarsById = {};
  props.calendars?.forEach((c) => {
    calendarsById[c.id] = c.title;
  });
  return calendarsById;
});

// default schedule object (for start and reset) and schedule form data
const defaultSchedule: Schedule = {
  active: calendarStore.hasConnectedCalendars,
  name: `${user.data.name}'s Availability`,
  calendar_id: props.calendars[0]?.id,
  location_type: EventLocationType.InPerson,
  location_url: '',
  details: '',
  start_date: dj().format(dateFormat),
  end_date: null,
  start_time: '09:00',
  end_time: '17:00',
  earliest_booking: 1440,
  farthest_booking: 20160,
  weekdays: [1, 2, 3, 4, 5],
  slot_duration: DEFAULT_SLOT_DURATION,
  meeting_link_provider: MeetingLinkProviderType.None,
  slug: user.mySlug,
  booking_confirmation: true,
};
const scheduleInput = ref({ ...defaultSchedule });
// For comparing changes, and resetting to default.
const referenceSchedule = ref({ ...defaultSchedule });
const generateZoomLink = ref(scheduleInput.value.meeting_link_provider === MeetingLinkProviderType.Zoom);

onMounted(() => {
  // Retrieve the current external connections
  externalConnectionStore.fetch();

  if (props.schedule) {
    scheduleInput.value = { ...props.schedule };
    // calculate utc back to user timezone
    scheduleInput.value.start_time = scheduleStore.timeToFrontendTime(scheduleInput.value.start_time, scheduleInput.value.time_updated);
    scheduleInput.value.end_time = scheduleStore.timeToFrontendTime(scheduleInput.value.end_time, scheduleInput.value.time_updated);

    // Adjust the default calendar if the one attached is not connected.
    const { calendar_id: calendarId } = scheduleInput.value;

    const calendar = props.calendars.find((cal) => cal.id === calendarId);
    if (!calendar || !calendar.connected) {
      scheduleInput.value.calendar_id = props.calendars[0]?.id;
    }
  } else {
    scheduleInput.value = { ...defaultSchedule };
  }

  generateZoomLink.value = scheduleInput.value.meeting_link_provider === MeetingLinkProviderType.Zoom;

  // Set a new reference
  referenceSchedule.value = { ...scheduleInput.value };
});

const scheduleCreationError = ref<Alert>(null);
const scheduledRangeMinutes = computed(() => {
  const start = dj(`${dj().format(dateFormat)}T${scheduleInput.value.start_time}:00`);
  const end = dj(`${dj().format(dateFormat)}T${scheduleInput.value.end_time}:00`);
  return end.diff(start, 'minutes');
});

// generate time slots from current schedule configuration for the displayed month
const getSlotPreviews = () => {
  const slots: Slot[] = [];
  // Add 1 week to the end of month here to display slots in displayed next month days too
  const end = scheduleInput.value.end_date
    ? dj.min(dj(scheduleInput.value.end_date), dj(props.activeDate).endOf('month').add(1, 'week'))
    : dj(props.activeDate).endOf('month').add(1, 'week');
  // Substract one week from the start to display slots in displayed previous month days too
  let pointerDate = dj.max(dj(scheduleInput.value.start_date), dj(props.activeDate).startOf('month').subtract(1, 'week'));
  while (pointerDate <= end) {
    if (scheduleInput.value.weekdays?.includes(pointerDate.isoWeekday())) {
      slots.push({
        start: `${pointerDate.format(dateFormat)}T${scheduleInput.value.start_time}:00`,
        duration: scheduledRangeMinutes.value ?? 30,
        attendee_id: null,
        id: null,
      });
    }
    pointerDate = pointerDate.add(1, 'day');
  }
  return slots;
};
// generate an appointment object with slots from current schedule data
const getScheduleAppointment = (): ScheduleAppointment => ({
  title: scheduleInput.value.name,
  calendar_id: scheduleInput.value.calendar_id,
  calendar_title: calendarTitles.value[scheduleInput.value.calendar_id],
  location_type: scheduleInput.value.location_type,
  location_url: scheduleInput.value.location_url,
  details: scheduleInput.value.details,
  status: 2,
  slots: getSlotPreviews(),
  type: 'schedule',
});

const isFormDirty = computed(
  () => JSON.stringify(scheduleInput.value) !== JSON.stringify(referenceSchedule.value),
);
const isSlugDirty = computed(
  () => scheduleInput.value.slug !== referenceSchedule.value.slug,
);

// handle notes char limit
const charLimit = 250;
const charCount = computed(() => scheduleInput.value.details.length);

// Weekday options
const scheduleDayOptions: SelectOption[] = isoWeekdays.map((day) => ({
  label: day.min[0],
  value: day.iso,
}));

// Connected calendar options
const calendarOptions = computed<SelectOption[]>(() => props.calendars.map((calendar) => ({
  label: calendar.title,
  value: calendar.id,
})));

// Earliest booking options
const earliestOptions: SelectOption[] = [0, 0.5, 1, 2, 3, 4, 5].map((d) => {
  // Special case to avoid "in a few seconds"
  if (d === 0) {
    return {
      label: t('label.immediately'),
      value: 0,
    };
  }
  return {
    label: dj.duration(d, 'days').humanize(),
    value: d * 60 * 24,
  };
});

// Farthest booking options
const farthestOptions: SelectOption[] = [1, 2, 3, 4].map((d) => ({
  label: dj.duration(d, 'weeks').humanize(),
  value: d * 60 * 24 * 7,
}));

// Appointment duration options
const durationOptions: SelectOption[] = SLOT_DURATION_OPTIONS.map((duration) => ({
  label: t('units.minutes', { value: duration }),
  value: duration,
}));

// humanize selected durations
const earliest = computed(() => (scheduleInput.value.earliest_booking === 0
  ? t('label.now')
  : dj.duration(scheduleInput.value.earliest_booking, 'minutes').humanize()));
const farthest = computed(() => dj.duration(scheduleInput.value.farthest_booking, 'minutes').humanize());
const duration = computed(() => t('units.minutes', { value: scheduleInput.value.slot_duration }));

// show confirmation dialog
const savedConfirmation = reactive({
  show: false,
  title: '',
});

// Revert the Schedule creation form to its initial values
const revertForm = (resetData = true) => {
  scheduleCreationError.value = null;
  if (resetData) {
    scheduleInput.value = { ...referenceSchedule.value };
  }
};

// Form validation
const scheduleValidationError = (schedule: Schedule): string|null => {
  // Schedule name is empty
  if (schedule.name === '') {
    return t('error.fieldIsRequired', { field: t('ftue.scheduleName') });
  }
  // All good
  return null;
};

// Update slug with a random 8 character string
const refreshSlugModalOpen = ref(false);
const showRefreshSlugConfirmation = async () => {
  refreshSlugModalOpen.value = true;
};

const closeModals = () => {
  savedConfirmation.show = false;
  refreshSlugModalOpen.value = false;
};

// handle actual schedule creation/update
const savingInProgress = ref(false);
const saveSchedule = async (withConfirmation = true) => {
  savingInProgress.value = true;
  // build data object for post request
  const obj = { ...scheduleInput.value, timezone: user.data.settings.timezone };
  // convert local input times to utc times

  obj.start_time = dj(`${dj().format('YYYY-MM-DD')}T${obj.start_time}:00`)
    .tz(user.data.settings.timezone ?? dj.tz.guess(), true)
    .utc()
    .format('HH:mm');
  obj.end_time = dj(`${dj().format('YYYY-MM-DD')}T${obj.end_time}:00`)
    .tz(user.data.settings.timezone ?? dj.tz.guess(), true)
    .utc()
    .format('HH:mm');
  // Update the start_date with the current date
  obj.start_date = dj().format(dateFormat);
  // remove unwanted properties
  delete obj.availabilities;
  delete obj.time_created;
  delete obj.time_updated;
  delete obj.id;

  // validate schedule data
  const validationError = scheduleValidationError(obj);
  if (validationError) {
    scheduleCreationError.value = { title: validationError };
    savingInProgress.value = false;
    window.scrollTo(0, 0);
    return;
  }

  // save schedule data
  const response = props.schedule
    ? await scheduleStore.updateSchedule(props.schedule.id, obj)
    : await scheduleStore.createSchedule(obj);

  // eslint-disable-next-line no-prototype-builtins
  if (response.hasOwnProperty('error')) {
    // error message is in data
    scheduleCreationError.value = { title: (response as Error).message };
    // go back to the start
    savingInProgress.value = false;
    window.scrollTo(0, 0);
    return;
  }

  // Otherwise it's just data!
  const data = response as Ref<Schedule>;

  if (withConfirmation) {
    // show confirmation
    savedConfirmation.title = data.value.name;
    savedConfirmation.show = true;
  }

  // We retrieve the slugs from the user store
  // ...we should adjust this, but for now just refresh the profile.
  await user.profile();

  savingInProgress.value = false;
  emit('created');
  // Update our reference schedule!
  referenceSchedule.value = { ...scheduleInput.value };
  revertForm(false);
  closeModals();
};

const refreshSlug = () => {
  scheduleInput.value.slug = window.crypto.randomUUID().substring(0, 8);
  closeModals();
};

// handle schedule activation / deactivation
const toggleActive = async (newValue: boolean) => {
  scheduleInput.value.active = newValue;
  await saveSchedule(false);
};

// Work-around for v-model and value not working for some reason...
const toggleZoomLinkCreation = () => {
  if (generateZoomLink.value) {
    scheduleInput.value.meeting_link_provider = MeetingLinkProviderType.Zoom;
    return;
  }

  scheduleInput.value.meeting_link_provider = MeetingLinkProviderType.None;
};

// handle schedule booking confirmation activation / deactivation
const toggleBookingConfirmation = (newValue: boolean) => {
  scheduleInput.value.booking_confirmation = newValue;
};

// Link copy
const myLinkTooltip = ref(t('label.copyLink'));
const myLinkShow = ref(false);
const copyLink = async () => {
  await navigator.clipboard.writeText(user.myLink);

  myLinkShow.value = true;
  myLinkTooltip.value = t('info.copiedToClipboard');

  // Fade out after a bit
  setTimeout(() => {
    myLinkShow.value = false;

    // After the animation fades...
    setTimeout(() => {
      myLinkTooltip.value = t('label.copyLink');
    }, 500);
  }, 4000);
};

// track if steps were already visited
watch(
  () => scheduleInput.value.active,
  (newValue) => {
    emit('updated', newValue ? getScheduleAppointment() : null);
  },
);

// track if steps were already visited
watch(
  () => state.value,
  (_, oldValue) => {
    if (scheduleInput.value.active) {
      if (oldValue === ScheduleCreationState.Availability) visitedStep1.value = true;
      emit('updated', getScheduleAppointment());
    }
  },
);

// track changes and send schedule updates
watch(
  () => [
    scheduleInput.value.active,
    scheduleInput.value.name,
    scheduleInput.value.calendar_id,
    scheduleInput.value.start_date,
    scheduleInput.value.end_date,
    scheduleInput.value.start_time,
    scheduleInput.value.end_time,
    scheduleInput.value.weekdays,
    scheduleInput.value.booking_confirmation,
    props.activeDate,
  ],
  () => {
    // if an existing schedule was given update anyway
    // if a new schedule gets created, only update on step 2
    if ((props.schedule && props.schedule.active) || (!props.schedule && visitedStep1.value)) {
      emit('updated', getScheduleAppointment());
    }
  },
);
</script>

<template>
  <div class="schedule-creation-container">
    <div class="flex flex-col gap-2 py-4">
      <div class="flex items-center justify-between text-center text-lg text-teal-600">
        <span class="pl-3">{{ t("heading.generalAvailability") }}</span>
        <switch-toggle
          v-if="existing"
          class="mt-0.5 pr-3"
          name="active"
          :active="schedule.active"
          no-legend
          @changed="toggleActive"
          :title="t(schedule.active ? 'label.deactivateSchedule' : 'label.activateSchedule')"
          data-testid="dashboard-set-availability-toggle"
        />
      </div>
      <alert-box
        v-if="scheduleCreationError"
        :alert="scheduleCreationError"
        @close="scheduleCreationError = null"
      />

      <div class="mb-1 px-4">
        <label for="scheduleName" class="flex-column flex">
          <input
            id="scheduleName"
            type="text"
            v-model="scheduleInput.name"
            :placeholder="t('placeholder.mySchedule')"
            :disabled="!scheduleInput.active"
            class="schedule-name place-holder w-full rounded-none border-0 border-b bg-transparent p-1 dark:bg-transparent"
            required
          />
          <div v-if="!scheduleInput.name" class="content-center text-red-500">*</div>
        </label>
      </div>

      <!-- step 1 -->
      <div id="schedule-availability" class="schedule-creation-step" :class="{ 'active': activeStep1 }">
        <div
          @click="state = ScheduleCreationState.Availability"
          class="btn-step-1 flex cursor-pointer items-center justify-between" data-testid="dashboard-availability-panel-btn"
        >
          <div class="flex flex-col">
            <h2>
              {{ t("label.chooseYourAvailability") }}
            </h2>
            <h3 class="text-xs">
              {{ t('label.scheduleSettings.availabilitySubHeading') }}
            </h3>
          </div>
          <icon-chevron-down
            class="size-6 -rotate-90 fill-transparent stroke-gray-800 stroke-1 transition-transform dark:stroke-gray-100"
            :class="{ '!rotate-0': activeStep1 }"
          />
        </div>
        <div v-show="activeStep1" class="flex flex-col gap-3">
          <hr/>
          <div class="flex w-full gap-2 lg:gap-4">
            <text-input
              type="time"
              name="start_time"
              class="w-full"
              v-model="scheduleInput.start_time"
              :disabled="!scheduleInput.active"
            >
              {{ t("label.startTime") }}
            </text-input>
            <text-input
              type="time"
              name="end_time"
              class="w-full"
              v-model="scheduleInput.end_time"
              :disabled="!scheduleInput.active"
            >
              {{ t("label.endTime") }}
            </text-input>
          </div>
          <div>
            <div class="input-label">
              {{ t("label.availableDays") }}
            </div>
            <bubble-select
              :options="scheduleDayOptions"
              v-model="scheduleInput.weekdays"
              :required="true"
              :disabled="!scheduleInput.active"
            />
          </div>
          <div>
            <div class="input-label">
              {{ t("label.timeZone") }}
            </div>
            <div class="flex justify-between">
              <div class="text-gray-600 dark:text-gray-200">{{ user.data.settings.timezone ?? dj.tz.guess() }}</div>
              <link-button class="edit-link-btn" @click="router.push({ name: 'settings' })" :tooltip="t('label.editInSettings')" data-testid="dashboard-availability-edit-link-btn">
                {{ t('label.edit') }}
              </link-button>
            </div>
          </div>
        </div>
      </div>

      <!-- step 2 -->
      <div id="schedule-settings" class="schedule-creation-step" :class="{ 'active': activeStep2 }">
        <div
          @click="state = ScheduleCreationState.Settings"
          class="btn-step-2 flex cursor-pointer items-center justify-between" data-testid="dashboard-scheduling-details-panel-btn"
        >
          <div class="flex flex-col">
            <h2>
              {{ t("label.scheduleDetails") }}
            </h2>
            <h3 class="text-xs">
              {{ t('label.scheduleSettings.schedulingDetailsSubHeading') }}
            </h3>
          </div>
          <icon-chevron-down
            class="size-6 -rotate-90 fill-transparent stroke-gray-800 stroke-1 transition-transform dark:stroke-gray-100"
            :class="{ '!rotate-0': activeStep2 }"
          />
        </div>
        <div v-show="activeStep2" class="flex flex-col gap-3">
          <hr/>
          <select-input
            name="calendar"
            v-model="scheduleInput.calendar_id"
            class="w-full"
            :options="calendarOptions"
            :disabled="!scheduleInput.active"
          >
            {{ t("label.selectCalendar") }}
          </select-input>
          <div class="grid grid-cols-2 gap-x-4 gap-y-2">
            <select-input
              name="earliest_booking"
              v-model="scheduleInput.earliest_booking"
              class="w-full"
              data-testid="dashboard-scheduling-details-earliest-booking-input"
              :options="earliestOptions"
              :disabled="!scheduleInput.active"
            >
              {{ t("label.earliestBooking") }}
            </select-input>
            <select-input
              name="farthest_booking"
              v-model="scheduleInput.farthest_booking"
              class="w-full"
              data-testid="dashboard-scheduling-details-farthest-booking-input"
              :options="farthestOptions"
              :disabled="!scheduleInput.active"
            >
              {{ t("label.farthestBooking") }}
            </select-input>
          </div>
          <select-input
            name="slot_duration"
            v-model="scheduleInput.slot_duration"
            data-testid="dashboard-scheduling-details-booking-duration-input"
            :options="durationOptions"
            :disabled="!scheduleInput.active"
            class="w-full"
          >
            {{ t("label.slotLength") }}
          </select-input>
          <div class="flex-center rounded-lg bg-white px-4 py-6 text-center text-sm dark:bg-gray-800">
            <div>{{
                t('text.recipientsCanScheduleBetween', {
                  duration: duration,
                  earliest: earliest,
                  farthest: farthest
                })
              }}
            </div>
          </div>
        </div>
      </div>

      <!-- step 3 -->
      <div
        id="schedule-details"
        class="schedule-creation-step"
        :class="{ 'active':  activeStep3 }"
        @click="state = ScheduleCreationState.Details"
      >
        <div class="flex cursor-pointer items-center justify-between" data-testid="dashboard-meeting-details-panel-btn">
          <div class="flex flex-col">
            <h2>
              {{ t("label.meetingDetails") }}
            </h2>
            <h3 class="text-xs">
              {{ t('label.scheduleSettings.meetingDetailsSubHeading') }}
            </h3>
          </div>
          <icon-chevron-down
            class="size-6 -rotate-90 fill-transparent stroke-gray-800 stroke-1 transition-transform dark:stroke-gray-100"
            :class="{ '!rotate-0': activeStep3 }"
          />
        </div>
        <div v-show="activeStep3" class="flex flex-col gap-2">
          <hr/>
          <text-input
            v-if="scheduleInput.meeting_link_provider === MeetingLinkProviderType.None"
            type="text"
            name="location_url"
            v-model="scheduleInput.location_url"
            class="w-full"
            :placeholder="t('placeholder.zoomCom')"
            :disabled="!scheduleInput.active || scheduleInput.meeting_link_provider !== MeetingLinkProviderType.None"
          >
            <div class="tooltip-label relative flex flex-row items-center gap-2">
              {{ t("label.videoLink") }}
              <span class="relative cursor-help" role="tooltip" aria-labelledby="video-link-tooltip">
                <icon-info-circle class="tooltip-icon w-4" aria-hidden="true"/>
                <span class="tooltip hidden">
                  <transition>
                    <tool-tip
                      id="video-link-tooltip"
                      class="tooltip left-[-8.5rem] w-72"
                      :content="t('text.videoLinkNotice')"
                    />
                  </transition>
                </span>
              </span>
            </div>
          </text-input>
          <checkbox-input
            name="generateZoomLink"
            :label="t('label.generateZoomLink')"
            v-model="generateZoomLink"
            :disabled="!scheduleInput.active || !hasZoomAccount"
            @change="toggleZoomLinkCreation"
          />
          <label class="relative flex flex-col gap-1">
            <div class="input-label ">
              {{ t("label.notes") }}
            </div>
            <textarea
              v-model="scheduleInput.details"
              :placeholder="t('placeholder.writeHere')"
              :disabled="!scheduleInput.active"
              class="place-holder h-24 w-full resize-none rounded-md text-sm"
              :maxlength="charLimit"
              data-testid="dashboard-meeting-details-notes-input"
            ></textarea>
            <div
              class="absolute bottom-3 right-3 text-xs"
              :class="{
              'text-orange-500': charCount >= charLimit * 0.92,
              '!text-rose-600': charCount === charLimit,
            }"
            >
              {{ charCount }}/{{ charLimit }}
            </div>
          </label>
        </div>
      </div>

      <!-- step 4 -->
      <div
        id="schedule-details"
        class="schedule-creation-step"
        :class="{ 'active': activeStep4 }"
        @click="state = ScheduleCreationState.Booking"
      >
        <div class="flex cursor-pointer items-center justify-between" data-testid="dashboard-boooking-settings-panel-btn">
          <div class="flex flex-col">
            <h2>
              {{ t("label.bookingSettings") }}
            </h2>
            <h3 class="text-xs">
              {{ t('label.scheduleSettings.bookingSettingsSubHeading') }}
            </h3>
          </div>
          <icon-chevron-down
            class="size-6 -rotate-90 fill-transparent stroke-gray-800 stroke-1 transition-transform dark:stroke-gray-100"
            :class="{ '!rotate-0': activeStep4 }"
          />
        </div>
        <div v-show="activeStep4" class="flex flex-col gap-2">
          <hr/>
          <!-- custom quick link -->
          <label class="relative flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <text-input
                type="text"
                name="slug"
                :prefix="`/${user.data.username}/`"
                v-model="scheduleInput.slug"
                class="w-full rounded-md disabled:cursor-not-allowed"
                :small-text="true"
                maxLength="16"
                :disabled="!scheduleInput.active"
              >
                {{ t("label.quickLink") }}
              </text-input>
              <link-button
                class="p-0.5"
                @click="scheduleInput.active ? refreshSlug() : null"
                :disabled="!scheduleInput.active"
                data-testid="dashboard-booking-settings-link-refresh-btn"
              >
                <refresh-icon />
              </link-button>
            </div>
          </label>
          <!-- option to deactivate confirmation -->
          <div class="flex flex-col gap-3">
            <switch-toggle
              class="my-1 text-sm font-medium text-gray-500 dark:text-gray-300"
              name="booking_confirmation"
              :active="scheduleInput.booking_confirmation"
              :label="t('label.bookingConfirmation')"
              :disabled="!scheduleInput.active"
              @changed="toggleBookingConfirmation"
              no-legend
            />
            <div class="whitespace-pre-line rounded-lg pb-3 text-xs text-gray-500">
              <div>
                {{ t('text.yourQuickLinkIs', { url: user.myLink }) }}<br />
                <i18n-t keypath="text.toUpdateYourUsername.text" tag="span">
                  <template v-slot:link>
                    <router-link class="underline" :to="{ name: 'settings' }" target="_blank">
                      {{ t('text.toUpdateYourUsername.link') }}
                    </router-link>
                  </template>
                </i18n-t>
                <span v-if="scheduleInput.booking_confirmation">
                  {{ t('text.bookingsWillRequireToBeConfirmed') }}
                </span>
                <span v-else>
                  {{ t('text.bookingsWillAutomaticallyBeConfirmed') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Snack-ish Bar - The dark info bubble at the bottom of this form -->
    <!-- First time no calendars -->
    <snackish-bar
      v-if="!calendarStore.hasConnectedCalendars"
      :show-icon=true
      :message="t('text.scheduleSettings.noCalendars')"
    >
      <u><a href="/settings/calendar">{{ t('text.scheduleSettings.clickHereToConnect') }}</a></u>
    </snackish-bar>
    <!-- No schedule? Create one please! -->
    <snackish-bar v-else-if="!existing" :message="t('text.scheduleSettings.create')">
      <primary-button
        class="btn-save w-full"
        @click="saveSchedule(!existing)"
        :disabled="!scheduleInput.active"
      >
        {{ t('label.save') }}
      </primary-button>
    </snackish-bar>
    <!-- Schedule is not active -->
    <snackish-bar
      v-else-if="!scheduleInput.active"
      :show-icon=true
      :message="t('text.scheduleSettings.notActive')"
    />
    <!-- Form is dirty, please clean it -->
    <snackish-bar
      v-else-if="isFormDirty"
      :show-icon="true"
      :message="t('text.scheduleSettings.formDirty')"
    >
      <primary-button
        class="btn-save w-full"
        @click="isSlugDirty ? showRefreshSlugConfirmation() : saveSchedule(!existing)"
        :disabled="!scheduleInput.active || savingInProgress"
        data-testid="dashboard-save-changes-btn"
      >
        {{ t('label.save') }}
      </primary-button>
      <link-button
        class="btn-revert w-full py-4"
        @click="revertForm()"
        :disabled="!scheduleInput.active"
      >
        {{ t('label.revertChanges') }}
      </link-button>
    </snackish-bar>
    <div v-else>
      <div class="my-8 flex justify-center gap-4">
        <primary-button
          v-if="user.myLink && existing"
          class="btn-copy"
          @click="copyLink"
          data-testid="dashboard-share-quick-link-btn"
          :tooltip="myLinkTooltip"
          :force-tooltip="myLinkShow"
        >
          <template v-slot:icon>
            <copy-icon/>
          </template>
          {{ t('label.shareMyLink') }}
        </primary-button>
      </div>
    </div>
  </div>
  <!-- modals -->
  <appointment-created-modal
    :open="savedConfirmation.show"
    :is-schedule="true"
    :title="savedConfirmation.title"
    :public-link="user.data.signedUrl"
    @close="closeModals"
  />
  <!-- Refresh link confirmation modal -->
  <confirmation-modal
    :open="refreshSlugModalOpen"
    :title="t('label.refreshLink')"
    :message="t('text.refreshLinkNotice')"
    :confirm-label="t('label.save')"
    :cancel-label="t('label.cancel')"
    @confirm="saveSchedule(!existing)"
    @close="closeModals"
  ></confirmation-modal>
</template>

<style scoped>
.schedule-creation-container {
  position: sticky;
  top: 6rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 1rem;
  border: 1px solid var(--colour-neutral-border);
  background: var(--colour-neutral-lower);
}

.schedule-creation-step {
  margin: 0 .75rem;
  padding: .75rem;
  display: flex;
  flex-direction: column;
  gap: .5rem;
  border-radius: .5rem;
  border: 1px solid var(--colour-neutral-border);

  &.active {
    background: var(--colour-neutral-base);
    border-color: var(--colour-service-primary);
  }
}

.input-label {
  color: var(--colour-ti-base);
  font-family: var(--font-sans);
  font-size: var(--txt-input);
  line-height: var(--line-height-input);
  width: 100%;
  font-weight: 500;
}

/* If the device does not support hover (i.e. mobile) then make it activate on focus within */
@media (hover: none) {
  .tooltip-label:focus-within .tooltip {
    display: block;
  }
}

.schedule-name {
  background-color: transparent !important;
}

.tooltip-icon:hover ~ .tooltip {
  display: block;
}

.edit-link-btn {
  min-width: auto;
}
</style>
