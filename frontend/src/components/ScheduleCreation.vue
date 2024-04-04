<template>
  <div class="sticky top-24 flex flex-col gap-4">
    <div class="flex items-center justify-around text-center text-xl font-semibold text-teal-500">
      <span>{{ t("heading.generalAvailability") }}</span>
      <switch-toggle v-if="existing" class="mt-0.5" :active="schedule.active" no-legend @changed="toggleActive"/>
    </div>
    <alert-box
      @close="scheduleCreationError = ''"
      v-if="scheduleCreationError"
    >
      {{ scheduleCreationError }}
    </alert-box>

    <!-- step 1 -->
    <div
      @click="state = scheduleCreationState.details"
      class="flex flex-col gap-2 rounded-lg bg-gray-100 p-4 text-gray-700 dark:bg-gray-600 dark:text-gray-100"
    >
      <div class="flex cursor-pointer items-center justify-between">
        <span class="font-semibold">
          {{ t("label.generalDetails") }}
        </span>
        <icon-chevron-down
          class="size-6 rotate-90 fill-transparent stroke-gray-800 stroke-1 transition-transform dark:stroke-gray-100"
          :class="{ '!rotate-0': activeStep1 }"
        />
      </div>
      <div v-show="activeStep1" class="flex flex-col gap-2">
        <hr/>
        <label>
          <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
            {{ t("heading.generalAvailability") }} {{ t("label.name") }}
          </div>
          <input
            type="text"
            v-model="scheduleInput.name"
            :placeholder="t('placeholder.biWeeklyCafeDates')"
            :disabled="!scheduleInput.active"
            class="place-holder w-full rounded-md"
          />
        </label>
        <label>
          <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
            {{ t("label.selectCalendar") }}
          </div>
          <select v-model="scheduleInput.calendar_id" class="w-full rounded-md" :disabled="!scheduleInput.active">
            <option
              v-for="calendar in calendars"
              :key="calendar.id"
              :value="calendar.id"
            >
              {{ calendar.title }}
            </option>
          </select>
        </label>
        <label>
          <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
            {{ t("label.location") }}
          </div>
          <tab-bar
            :tab-items="locationTypes"
            :active="scheduleInput.location_type"
            :disabled="!scheduleInput.active"
            @update="updateLocationType"
          />
        </label>
        <label>
          <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
            {{ t("label.videoLink") }}
          </div>
          <input
            type="text"
            v-model="scheduleInput.location_url"
            :placeholder="t('placeholder.zoomCom')"
            :disabled="!scheduleInput.active || scheduleInput.meeting_link_provider !== meetingLinkProviderType.none"
            class="place-holder w-full rounded-md disabled:cursor-not-allowed"
          />
        </label>
        <label class="flex items-center gap-2">
          <input
            type="checkbox"
            :checked="scheduleInput.meeting_link_provider === meetingLinkProviderType.zoom"
            @change="toggleZoomLinkCreation"
            class="size-5 rounded-md"
          />
          <div class="font-medium text-gray-500 dark:text-gray-300">
            {{ t("label.generateZoomLink") }}
          </div>
        </label>
        <label class="relative flex flex-col gap-1">
          <div class="font-medium text-gray-500 dark:text-gray-300">
            {{ t("label.notes") }}
          </div>
          <textarea
            v-model="scheduleInput.details"
            :placeholder="t('placeholder.writeHere')"
            :disabled="!scheduleInput.active"
            class="place-holder h-24 w-full resize-none rounded-md text-sm"
            :maxlength="charLimit"
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
    <!-- step 2 -->
    <div
      class="flex flex-col gap-2 rounded-lg bg-gray-100 p-4 text-gray-700 dark:bg-gray-600 dark:text-gray-100"
    >
      <div
        @click="state = scheduleCreationState.availability"
        class="flex cursor-pointer items-center justify-between"
      >
        <span class="font-semibold">
          {{ t("label.chooseYourAvailability") }}
        </span>
        <icon-chevron-down
          class="size-6 rotate-90 fill-transparent stroke-gray-800 stroke-1 transition-transform dark:stroke-gray-100"
          :class="{ '!rotate-0': activeStep2 }"
        />
      </div>
      <div v-show="activeStep2" class="flex flex-col gap-3">
        <hr/>
        <div class="grid grid-cols-2 gap-4">
          <label>
            <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
              {{ t("label.startDate") }}
            </div>
            <input
              type="date"
              v-model="scheduleInput.start_date"
              :disabled="!scheduleInput.active"
              class="w-full rounded-md"
            />
          </label>
          <label>
            <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
              {{ t("label.endDate") }}
            </div>
            <input
              type="date"
              v-model="scheduleInput.end_date"
              :placeholder="t('placeholder.never')"
              :disabled="!scheduleInput.active"
              class="place-holder w-full rounded-md"
            />
          </label>
          <label>
            <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
              {{ t("label.startTime") }}
            </div>
            <input
              type="time"
              v-model="scheduleInput.start_time"
              :disabled="!scheduleInput.active"
              class="w-full rounded-md"
            />
          </label>
          <label>
            <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
              {{ t("label.endTime") }}
            </div>
            <input
              type="time"
              v-model="scheduleInput.end_time"
              :disabled="!scheduleInput.active"
              class="w-full rounded-md"
            />
          </label>
        </div>
        <div>
          <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
            {{ t("label.availableDays") }}
          </div>
          <div class="grid grid-flow-col grid-cols-2 grid-rows-4 gap-2 rounded-lg bg-white p-4 dark:bg-gray-800">
            <label
              v-for="w in isoWeekdays"
              :key="w.iso"
              class="flex cursor-pointer select-none items-center gap-2 text-sm"
            >
              <input
                type="checkbox"
                v-model="scheduleInput.weekdays"
                :value="w.iso"
                :disabled="!scheduleInput.active"
                class="size-5 text-teal-500"
              />
              <span>{{ w.long }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
    <!-- step 3 -->
    <div
      class="flex flex-col gap-2 rounded-lg bg-gray-100 p-4 text-gray-700 dark:bg-gray-600 dark:text-gray-100"
    >
      <div
        @click="state = scheduleCreationState.settings"
        class="flex cursor-pointer items-center justify-between"
      >
        <span class="font-semibold">
          {{ t("label.bookingSettings") }}
        </span>
        <icon-chevron-down
          class="size-6 rotate-90 fill-transparent stroke-gray-800 stroke-1 transition-transform dark:stroke-gray-100"
          :class="{ '!rotate-0': activeStep3 }"
        />
      </div>
      <div v-show="activeStep3" class="flex flex-col gap-3">
        <hr/>
        <div class="grid grid-cols-2 gap-4">
          <label>
            <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
              {{ t("label.earliestBooking") }}
            </div>
            <select
              v-model="scheduleInput.earliest_booking"
              class="w-full rounded-md"
              :disabled="!scheduleInput.active"
            >
              <option
                v-for="(label, value) in earliestOptions"
                :key="value"
                :value="value"
              >
                {{ label }}
              </option>
            </select>
          </label>
          <label>
            <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
              {{ t("label.farthestBooking") }}
            </div>
            <select
              v-model="scheduleInput.farthest_booking"
              class="w-full rounded-md"
              :disabled="!scheduleInput.active"
            >
              <option
                v-for="(label, value) in farthestOptions"
                :key="value"
                :value="value"
              >
                {{ label }}
              </option>
            </select>
          </label>
          <label class="col-span-2">
            <div class="mb-1 font-medium text-gray-500 dark:text-gray-300">
              {{ t("label.slotLength") }}
            </div>
            <input
              type="number"
              min="10"
              v-model="scheduleInput.slot_duration"
              :disabled="!scheduleInput.active"
              class="w-full rounded-md"
            />
          </label>
        </div>
        <div class="flex-center rounded-lg bg-white px-4 py-6 text-center text-sm dark:bg-gray-800">
          <div>{{ t('text.recipientsCanScheduleBetween', {earliest: earliest, farthest: farthest}) }}</div>
        </div>
      </div>
    </div>
    <!-- action buttons -->
    <div class="my-8 flex justify-center gap-4">
      <primary-button
        v-if="user.data.signedUrl && existing"
        :label="t('label.shareMyLink')"
        :copy="user.data.signedUrl"
      />
    </div>
    <div class="flex gap-4">
      <secondary-button
        :label="t('label.cancel')"
        @click="resetSchedule()"
        :disabled="!scheduleInput.active"
        class="w-1/2"
      />
      <primary-button
        v-show="activeStep1 || activeStep2"
        :label="t('label.next')"
        @click="nextStep()"
        :disabled="!scheduleInput.active"
        class="w-1/2"
      />
      <primary-button
        v-show="activeStep3"
        :label="t('label.save')"
        @click="saveSchedule(!existing)"
        :waiting="savingInProgress"
        :disabled="!scheduleInput.active"
        class="w-1/2"
      />
    </div>
  </div>
  <!-- modals -->
  <appointment-created-modal
    :open="savedConfirmation.show"
    :is-schedule="true"
    :title="savedConfirmation.title"
    :public-link="user.data.signedUrl"
    @close="closeCreatedModal"
  />
</template>

<script setup>
import {
  dateFormatStrings, defaultSlotDuration, locationTypes, meetingLinkProviderType, scheduleCreationState,
} from '@/definitions';
import {
  ref, reactive, computed, inject, watch, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import AppointmentCreatedModal from '@/components/AppointmentCreatedModal';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';
import TabBar from '@/components/TabBar';

// icons
import { IconChevronDown } from '@tabler/icons-vue';
import AlertBox from '@/elements/AlertBox';
import SwitchToggle from '@/elements/SwitchToggle';

// component constants
const user = useUserStore();
const { t } = useI18n();
const dj = inject('dayjs');
const call = inject('call');
const isoWeekdays = inject('isoWeekdays');
const dateFormat = dateFormatStrings.qalendarFullDay;

// component emits
const emit = defineEmits(['created', 'updated']);

// component properties
const props = defineProps({
  calendars: Array, // list of user defined calendars
  schedule: Object, // existing schedule to update or null
  activeDate: Object, // dayjs object indicating the currently active calendar view date
});

// check if existing schedule is given
const existing = computed(() => Boolean(props.schedule));

// schedule creation state indicating the current step
const state = ref(scheduleCreationState.details);

// calculate the current visible step by given status
// first step are the general details
// second step is the availability configuration
// third step are the booking settings
const activeStep1 = computed(() => state.value === scheduleCreationState.details);
const activeStep2 = computed(() => state.value === scheduleCreationState.availability);
const activeStep3 = computed(() => state.value === scheduleCreationState.settings);
const visitedStep1 = ref(false);
const nextStep = () => state.value++;

// calculate calendar titles
const calendarTitles = computed(() => {
  const calendarsById = {};
  props.calendars?.forEach((c) => {
    calendarsById[c.id] = c.title;
  });
  return calendarsById;
});

// default schedule object (for start and reset) and schedule form data
const defaultSchedule = {
  active: true,
  name: '',
  calendar_id: props.calendars[0]?.id,
  location_type: locationTypes.inPerson,
  location_url: '',
  details: '',
  start_date: dj().format(dateFormat),
  end_date: null,
  start_time: '09:00',
  end_time: '17:00',
  earliest_booking: 1440,
  farthest_booking: 20160,
  weekdays: [1, 2, 3, 4, 5],
  slot_duration: defaultSlotDuration,
  meeting_link_provider: meetingLinkProviderType.none,
};
const scheduleInput = ref({ ...defaultSchedule });
onMounted(() => {
  if (props.schedule) {
    scheduleInput.value = { ...props.schedule };
    // calculate utc back to user timezone
    scheduleInput.value.start_time = dj(`${dj().format(dateFormat)}T${scheduleInput.value.start_time}:00`)
      .utc(true)
      .tz(user.data.timezone ?? dj.tz.guess())
      .format('HH:mm');
    scheduleInput.value.end_time = dj(`${dj().format(dateFormat)}T${scheduleInput.value.end_time}:00`)
      .utc(true)
      .tz(user.data.timezone ?? dj.tz.guess())
      .format('HH:mm');
  } else {
    scheduleInput.value = { ...defaultSchedule };
  }
});

const scheduleCreationError = ref(null);
const scheduledRangeMinutes = computed(() => {
  const start = dj(`${dj().format(dateFormat)}T${scheduleInput.value.start_time}:00`);
  const end = dj(`${dj().format(dateFormat)}T${scheduleInput.value.end_time}:00`);
  return end.diff(start, 'minutes');
});

// generate time slots from current schedule configuration
const getSlots = () => {
  const slots = [];
  const end = scheduleInput.value.end_date
    ? dj.min(dj(scheduleInput.value.end_date), dj(props.activeDate).endOf('month'))
    : dj(props.activeDate).endOf('month');
  let pointerDate = dj.max(dj(scheduleInput.value.start_date), dj(props.activeDate).startOf('month'));
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
const getScheduleAppointment = () => ({
  title: scheduleInput.value.name,
  calendar_id: scheduleInput.value.calendar_id,
  calendar_title: calendarTitles.value[scheduleInput.value.calendar_id],
  location_type: scheduleInput.value.location_type,
  location_url: scheduleInput.value.location_url,
  details: scheduleInput.value.details,
  status: 2,
  slots: getSlots(),
  type: 'schedule',
});

// tab navigation for location types
const updateLocationType = (type) => {
  scheduleInput.value.location_type = locationTypes[type];
};

// handle notes char limit
const charLimit = 250;
const charCount = computed(() => scheduleInput.value.details.length);

// booking options
const earliestOptions = {};
[0, 0.5, 1, 2, 3, 4, 5].forEach((d) => {
  // Special case to avoid "in a few seconds"
  if (d === 0) {
    earliestOptions[0] = t('label.immediately');
    return;
  }
  earliestOptions[d * 60 * 24] = dj.duration(d, 'days').humanize();
});
const farthestOptions = {};
[1, 2, 3, 4].forEach((d) => {
  farthestOptions[d * 60 * 24 * 7] = dj.duration(d, 'weeks').humanize();
});

// humanize selected durations
const earliest = computed(() => (parseInt(scheduleInput.value.earliest_booking, 10) === 0
  ? t('label.immediately') : dj.duration(scheduleInput.value.earliest_booking, 'minutes').humanize()));
const farthest = computed(() => dj.duration(scheduleInput.value.farthest_booking, 'minutes').humanize());

// show confirmation dialog
const savedConfirmation = reactive({
  show: false,
  title: '',
});
const closeCreatedModal = () => {
  savedConfirmation.show = false;
};

// reset the Schedule creation form
const resetSchedule = () => {
  scheduleCreationError.value = null;
  state.value = scheduleCreationState.details;
};

const handleErrorResponse = (responseData) => {
  scheduleCreationError.value = null;

  const { value } = responseData;

  if (value?.detail?.message) {
    scheduleCreationError.value = value?.detail?.message;
  } else if (value?.detail instanceof Array) {
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
      const fieldLocalized = t(`fields.${field}`);
      let message = t('error.unknownScheduleError');

      if (err.type === 'greater_than_equal') {
        const contextValue = err.ctx.ge;
        const valueLocalized = t(fieldUnits[field] ?? 'units.none', { value: contextValue });

        message = t('error.minimumValue', {
          field: fieldLocalized,
          value: valueLocalized,
        });
      }

      return message;
    });

    scheduleCreationError.value = errorDetails.join('\n');
  } else {
    scheduleCreationError.value = t('error.unknownScheduleError');
  }
};

// handle actual schedule creation/update
const savingInProgress = ref(false);
const saveSchedule = async (withConfirmation = true) => {
  savingInProgress.value = true;
  // build data object for post request
  const obj = { ...scheduleInput.value };
  // convert local input times to utc times

  obj.start_time = dj(`${dj().format('YYYY-MM-DD')}T${obj.start_time}:00`)
    .tz(user.data.timezone ?? dj.tz.guess(), true)
    .utc()
    .format('HH:mm');
  obj.end_time = dj(`${dj().format('YYYY-MM-DD')}T${obj.end_time}:00`)
    .tz(user.data.timezone ?? dj.tz.guess(), true)
    .utc()
    .format('HH:mm');
  // remove unwanted properties
  delete obj.availabilities;
  delete obj.time_created;
  delete obj.time_updated;
  delete obj.id;

  // save schedule data
  const { data, error } = props.schedule
    ? await call(`schedule/${props.schedule.id}`).put(obj).json()
    : await call('schedule/').post(obj).json();

  if (error.value) {
    // error message is in data
    handleErrorResponse(data);
    // go back to the start
    state.value = scheduleCreationState.details;
    savingInProgress.value = false;
    return;
  }

  if (withConfirmation) {
    // show confirmation
    savedConfirmation.title = data.value.name;
    savedConfirmation.show = true;
  }

  savingInProgress.value = false;
  emit('created');
  resetSchedule();
};

// handle schedule activation / deactivation
const toggleActive = async (newValue) => {
  scheduleInput.value.active = newValue;
  await saveSchedule(false);
};

// Work-around for v-model and value not working for some reason...
const toggleZoomLinkCreation = () => {
  if (scheduleInput.value.meeting_link_provider === meetingLinkProviderType.none) {
    scheduleInput.value.meeting_link_provider = meetingLinkProviderType.zoom;
    return;
  }

  scheduleInput.value.meeting_link_provider = meetingLinkProviderType.none;
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
      if (oldValue === 1) visitedStep1.value = true;
      emit('updated', getScheduleAppointment());
    }
  },
);

// track changes and send schedule updates
watch(
  () => [
    scheduleInput.value.name,
    scheduleInput.value.calendar_id,
    scheduleInput.value.start_date,
    scheduleInput.value.end_date,
    scheduleInput.value.start_time,
    scheduleInput.value.end_time,
    scheduleInput.value.weekdays,
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
