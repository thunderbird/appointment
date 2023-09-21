<template>
  <div class="relative flex flex-col gap-4 h-full">
    <div class="font-semibold text-center text-xl text-teal-500">
      {{ t("heading.generalAvailability") }}
    </div>
    <alert-box v-if="scheduleCreationError" :title="t('label.scheduleCreationError')">
      {{ scheduleCreationError }}
    </alert-box>

    <!-- step 1 -->
    <div
      @click="state = scheduleCreationState.details"
      class="rounded-lg p-4 flex flex-col gap-2 text-gray-700 dark:text-gray-100 bg-gray-100 dark:bg-gray-600"
    >
      <div class="flex justify-between items-center cursor-pointer">
        <span class="font-semibold">
          {{ t("label.generalDetails") }}
        </span>
        <icon-chevron-down
          class="h-6 w-6 stroke-1 fill-transparent rotate-90 transition-transform stroke-gray-800 dark:stroke-gray-100"
          :class="{ '!rotate-0': activeStep1 }"
        />
      </div>
      <div v-show="activeStep1" class="flex flex-col gap-2">
        <hr />
        <label>
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("heading.generalAvailability") }} {{ t("label.name") }}
          </div>
          <input
            type="text"
            v-model="schedule.name"
            :placeholder="t('placeholder.biWeeklyCafeDates')"
            class="rounded-md w-full place-holder"
          />
        </label>
        <label>
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.selectCalendar") }}
          </div>
          <select v-model="schedule.calendar_id" class="rounded-md w-full">
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
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.location") }}
          </div>
          <tab-bar
            :tab-items="locationTypes"
            :active="schedule.location_type"
            @update="updateLocationType"
          />
        </label>
        <label>
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.videoLink") }}
          </div>
          <input
            type="text"
            v-model="schedule.location_url"
            :placeholder="t('placeholder.zoomCom')"
            class="rounded-md w-full place-holder"
          />
        </label>
        <label class="relative">
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.notes") }}
          </div>
          <textarea
            v-model="schedule.details"
            :placeholder="t('placeholder.writeHere')"
            class="rounded-md w-full text-sm h-24 resize-none place-holder"
            :maxlength="charLimit"
          ></textarea>
          <div
            class="absolute bottom-3.5 right-3 text-xs"
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
      class="rounded-lg p-4 flex flex-col gap-2 text-gray-700 dark:text-gray-100 bg-gray-100 dark:bg-gray-600"
    >
      <div
        @click="state = scheduleCreationState.availability"
        class="flex justify-between items-center cursor-pointer"
      >
        <span class="font-semibold">
          {{ t("label.chooseYourAvailability") }}
        </span>
        <icon-chevron-down
          class="h-6 w-6 stroke-1 fill-transparent rotate-90 transition-transform stroke-gray-800 dark:stroke-gray-100"
          :class="{ '!rotate-0': activeStep2 }"
        />
      </div>
      <div v-show="activeStep2" class="flex flex-col gap-3">
        <hr />
        <div class="grid grid-cols-2 gap-4">
          <label>
            <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
              {{ t("label.startDate") }}
            </div>
            <input
              type="date"
              v-model="schedule.start_date"
              class="rounded-md w-full"
            />
          </label>
          <label>
            <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
              {{ t("label.endDate") }}
            </div>
            <input
              type="date"
              v-model="schedule.end_date"
              :placeholder="t('placeholder.never')"
              class="rounded-md w-full place-holder"
            />
          </label>
          <label>
            <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
              {{ t("label.startTime") }}
            </div>
            <input
              type="time"
              v-model="schedule.start_time"
              class="rounded-md w-full"
            />
          </label>
          <label>
            <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
              {{ t("label.endTime") }}
            </div>
            <input
              type="time"
              v-model="schedule.end_time"
              class="rounded-md w-full"
            />
          </label>
        </div>
        <div>
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.availableDays") }}
          </div>
          <div class="grid grid-cols-2 grid-rows-4 grid-flow-col gap-2 bg-white p-4 rounded-lg">
            <label v-for="(w, i) in dj.weekdays()" class="flex gap-2 items-center text-sm select-none cursor-pointer">
              <input
                type="checkbox"
                v-model="schedule.weekdays"
                :value="i"
                class="text-teal-500 w-5 h-5"
              />
              <span>{{ w }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
    <!-- step 3 -->
    <div
      class="rounded-lg p-4 flex flex-col gap-2 text-gray-700 dark:text-gray-100 bg-gray-100 dark:bg-gray-600"
    >
      <div
        @click="state = scheduleCreationState.settings"
        class="flex justify-between items-center cursor-pointer"
      >
        <span class="font-semibold">
          {{ t("label.bookingSettings") }}
        </span>
        <icon-chevron-down
          class="h-6 w-6 stroke-1 fill-transparent rotate-90 transition-transform stroke-gray-800 dark:stroke-gray-100"
          :class="{ '!rotate-0': activeStep3 }"
        />
      </div>
      <div v-show="activeStep3" class="flex flex-col gap-3">
        <hr />
        <div class="grid grid-cols-2 gap-4">
          <label>
            <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
              {{ t("label.earliestBooking") }}
            </div>
            <select v-model="schedule.earliest_booking" class="rounded-md w-full">
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
            <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
              {{ t("label.farthestBooking") }}
            </div>
            <select v-model="schedule.farthest_booking" class="rounded-md w-full">
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
            <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
              {{ t("label.slotLength") }}
            </div>
            <input
              type="number"
              min="5"
              v-model="schedule.slot_duration"
              class="rounded-md w-full"
            />
          </label>
        </div>
        <div class="bg-white px-4 py-6 rounded-lg flex-center text-sm text-center">
          <div>{{ t('text.recipientsCanScheduleBetween', { earliest: earliest, farthest: farthest }) }}</div>
        </div>
      </div>
    </div>
    <!-- action buttons -->
    <div class="flex gap-4 mt-auto">
      <secondary-button
        :label="t('label.cancel')"
        @click="resetSchedule()"
        class="w-1/2"
      />
      <primary-button
        v-show="activeStep1 || activeStep2"
        :label="t('label.next')"
        @click="nextStep()"
        class="w-1/2"
      />
      <primary-button
        v-show="activeStep3"
        :label="t('label.save')"
        @click="saveSchedule()"
        class="w-1/2"
      />
    </div>
  </div>
  <!-- modals -->
  <appointment-created-modal
    :open="savedConfirmation.show"
    :is-schedule="true"
    :title="savedConfirmation.title"
    :public-link="savedConfirmation.publicLink"
    @close="closeCreatedModal"
  />
</template>

<script setup>
import { locationTypes, scheduleCreationState } from "@/definitions";
import { ref, reactive, computed, inject, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import AppointmentCreatedModal from "@/components/AppointmentCreatedModal";
import PrimaryButton from "@/elements/PrimaryButton";
import SecondaryButton from "@/elements/SecondaryButton";
import TabBar from "@/components/TabBar";

// icons
import { IconChevronDown } from "@tabler/icons-vue";
import AlertBox from "@/elements/AlertBox";

// component constants
const { t } = useI18n();
const dj = inject("dayjs");
const call = inject("call");

// component emits
const emit = defineEmits(["created", "updated"]);

// component properties
const props = defineProps({
  calendars: Array, // list of user defined calendars
  schedule: Object, // existing schedule to update or null
  user: Object, // currently logged in user, null if not logged in
  activeDate: Object, // dayjs object indicating the currently active calendar view date
});

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
  name: "",
  calendar_id: props.calendars[0]?.id,
  location_type: locationTypes.inPerson,
  location_url: "",
  details: "",
  start_date: dj().format("YYYY-MM-DD"),
  end_date: null,
  start_time: "09:00",
  end_time: "17:00",
  earliest_booking: 1440,
  farthest_booking: 20160,
  weekdays: [1,2,3,4,5],
  slot_duration: 30,
};
const schedule = ref({ ...defaultSchedule });
onMounted(() => {
  schedule.value = props.schedule ? { ...props.schedule } : { ...defaultSchedule };
});

const scheduleCreationError = ref(null);
const scheduledRangeMinutes = computed(() => {
  const start = dj(`20230101T${schedule.value.start_time}:00`);
  const end = dj(`20230101T${schedule.value.end_time}:00`);
  return end.diff(start, 'minutes');
});
// generate time slots from current schedule configuration
const getSlots = () => {
  const slots = [];
  const end = schedule.value.end_date
    ? dj.min(dj(schedule.value.end_date), dj(props.activeDate).endOf('month'))
    : dj(props.activeDate).endOf('month');
  let pointerDate = dj.max(dj(schedule.value.start_date), dj(props.activeDate).startOf('month'));
  while (pointerDate <= end) {
    if (schedule.value.weekdays?.includes(pointerDate.weekday())) {
      slots.push({
        "start": `${pointerDate.format("YYYY-MM-DD")}T${schedule.value.start_time}:00`,
        "duration": scheduledRangeMinutes.value ?? 30,
        "attendee_id": null,
        "id": null
      });
    }
    pointerDate = pointerDate.add(1, 'day');
  }
  return slots;
};
// generate an appointment object with slots from current schedule data
const getScheduleAppointment = () => {
  return {
    title: schedule.value.name,
    calendar_id: schedule.value.calendar_id,
    calendar_title: calendarTitles.value[schedule.value.calendar_id],
    location_type: schedule.value.location_type,
    location_url: schedule.value.location_url,
    details: schedule.value.details,
    status: 2,
    slots: getSlots(),
  }
};

// tab navigation for location types
const updateLocationType = (type) => {
  schedule.value.location_type = locationTypes[type];
};

// handle notes char limit
const charLimit = 250;
const charCount = computed(() => schedule.value.details.length);

// booking options
const earliestOptions = {};
[0.5,1,2,3,4,5].forEach(d => earliestOptions[d*60*24] = dj.duration(d, "days").humanize());
const farthestOptions = {};
[1,2,3,4].forEach(d => farthestOptions[d*60*24*7] = dj.duration(d, "weeks").humanize());

// humanize selected durations
const earliest = computed(() => dj.duration(schedule.value.earliest_booking, "minutes").humanize());
const farthest = computed(() => dj.duration(schedule.value.farthest_booking, "minutes").humanize());

// show confirmation dialog
const savedConfirmation = reactive({
  show: false,
  title: "",
  publicLink: "",
});
const closeCreatedModal = () => {
  savedConfirmation.show = false;
};

// reset the Schedule creation form
const resetSchedule = () => {
  scheduleCreationError.value = null;
  state.value = scheduleCreationState.details;
};

// handle actual schedule creation/update
const saveSchedule = async () => {
  // build data object for post request
  const obj = { ...schedule.value };
  delete obj.availabilities;
  delete obj.time_created;
  delete obj.time_updated;
  delete obj.id;

  // save schedule data
  const { data, error } = props.schedule
    ? await call(`schedule/${props.schedule.id}`).put(obj).json()
    : await call("schedule").post(obj).json();

  if (error.value) {
    // error message is in data
    scheduleCreationError.value = data.value.detail || t("error.unknownScheduleError");
    // go back to the start
    state.value = scheduleCreationState.details;
    return;
  }

  // Retrieve the user short url
  const { data: sig_data, error: sig_error } = await call('me/signature').get().json();
  if (sig_error.value) {
    return;
  }

  // show confirmation
  savedConfirmation.title = data.value.name;
  savedConfirmation.publicLink = sig_data.value.url;
  savedConfirmation.show = true;

  resetSchedule();

  emit("created");
};

// track if steps were already visited
watch(
  () => state.value,
  (_, oldValue) => {
    if (oldValue === 1) visitedStep1.value = true;
    emit('updated', getScheduleAppointment());
  }
);

// track changes and send schedule updates
watch(
  () => [
    schedule.value.name,
    schedule.value.calendar_id,
    schedule.value.start_date,
    schedule.value.end_date,
    schedule.value.start_time,
    schedule.value.end_time,
    schedule.value.weekdays,
    props.activeDate,
  ],
  () => {
    // if an existing schedule was given update anyway
    // if a new schedule gets created, only update on step 2
    if (props.schedule || !props.schedule && visitedStep1.value) {
      emit('updated', getScheduleAppointment());
    }
  }
);
</script>
