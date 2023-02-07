<template>
  <div class="relative flex flex-col gap-4 h-full">
    <div class="text-teal-500 font-semibold text-center text-xl">
      {{ t('heading.createNewAppointment') }}
    </div>
    <!-- step 1 -->
    <div class="text-gray-700 bg-gray-100 rounded-lg p-4 flex flex-col gap-2">
      <div class="flex justify-between items-center cursor-pointer" @click="emit('start')">
        <span class="font-semibold flex gap-1">
          <check-icon v-show="validStep1" class="h-6 w-6 stroke-2 stroke-teal-500 fill-transparent" />
          <alert-triangle-icon v-show="invalidStep1" class="h-6 w-6 stroke-2 stroke-red-500 fill-transparent" />
          {{ t('label.appointmentDetails') }}
        </span>
        <chevron-down-icon
          class="h-6 w-6 stroke-1 stroke-gray-800 fill-transparent rotate-90 transition-transform"
          :class="{ 'rotate-0': activeStep1 }"
        />
      </div>
      <div v-show="activeStep1" class="flex flex-col gap-2">
        <hr />
        <label>
          <div class="font-medium text-gray-500 mb-1">{{ t('label.appointmentName') }}</div>
          <input
            type="text"
            v-model="appointment.title"
            :placeholder="t('placeholder.biWeeklyCafeDates')"
            class="rounded-md bg-gray-50 border-gray-200 w-full"
          />
        </label>
        <label>
          <div class="font-medium text-gray-500 mb-1">{{ t('label.selectCalendar') }}</div>
          <select v-model="appointment.calendar_id" class="rounded-md bg-gray-50 border-gray-200 w-full">
            <option v-for="calendar in calendars" :key="calendar.id" :value="calendar.id">{{ calendar.title }}</option>
          </select>
        </label>
        <label>
          <div class="font-medium text-gray-500 mb-1">{{ t('label.location') }}</div>
          <tab-bar
            :tab-items="locationTypes"
            :active="appointment.location_type"
            @update="updateLocationType"
          />
        </label>
        <label>
          <div class="font-medium text-gray-500 mb-1">{{ t('label.videoLink') }}</div>
          <input
            type="text"
            v-model="appointment.location_url"
            :placeholder="t('placeholder.zoomCom')"
            class="rounded-md bg-gray-50 border-gray-200 w-full"
          />
        </label>
        <label class="relative">
          <div class="font-medium text-gray-500 mb-1">{{ t('label.notes') }}</div>
          <textarea
            v-model="appointment.details"
            :placeholder="t('placeholder.writeHere')"
            class="rounded-md bg-gray-50 border-gray-200 w-full text-sm h-40 resize-none"
            :maxlength="charLimit"
          ></textarea>
          <div
            class="absolute bottom-3.5 right-3 text-xs"
            :class="{
              'text-orange-500': charCount >= charLimit*0.92,
              '!text-red-600': charCount === charLimit
            }"
          >
            {{ charCount }}/{{ charLimit }}
          </div>
        </label>
      </div>
    </div>
    <!-- step 2 -->
    <div class="text-gray-700 bg-gray-100 rounded-lg p-4 flex flex-col gap-2">
      <div class="flex justify-between items-center cursor-pointer" @click="emit('next')">
        <span class="font-semibold flex gap-1">
          <check-icon v-show="validStep2" class="h-6 w-6 stroke-2 stroke-teal-500 fill-transparent" />
          <alert-triangle-icon v-show="invalidStep2" class="h-6 w-6 stroke-2 stroke-red-500 fill-transparent" />
          {{ t('label.chooseYourAvailability') }}
        </span>
        <chevron-down-icon
          class="h-6 w-6 stroke-1 stroke-gray-800 fill-transparent rotate-90 transition-transform"
          :class="{ 'rotate-0': activeStep2 }"
        />
      </div>
      <div v-show="activeStep2" class="flex flex-col gap-3">
        <hr />
        <div v-show="!validStep2" class="text-sm">{{ t('text.defineDaysAndTimeSlots') }}</div>
        <div v-show="validStep2" class="flex flex-col gap-2">
          <div v-for="(list, day) in slots" :key="day">
            <div class="flex justify-between mb-1">
              <div>{{ dj(day).format('LL') }}</div>
              <div>
                <button @click="addTime(day)" class="flex items-center px-2 py-1 border-r rounded-full bg-teal-500 text-white text-xs">
                  <plus-icon class="h-3 w-3 stroke-2 stroke-white fill-transparent" />
                  {{ t('label.addTime') }}
                </button>
              </div>
            </div>
            <div v-for="(s, i) in list" :key="s.start" class="flex gap-4 justify-center items-end mb-2">
              <label class="flex flex-col">
                <div class="text-sm text-gray-500">{{ t('label.start') }}</div>
                <input
                  type="time"
                  v-model="s.start"
                  class="rounded-md bg-gray-50 border-gray-200 text-sm py-1"
                />
              </label>
              <label class="flex flex-col">
                <div class="text-sm text-gray-500">{{ t('label.end') }}</div>
                <input
                  type="time"
                  v-model="s.end"
                  class="rounded-md bg-gray-50 border-gray-200 text-sm py-1"
                />
              </label>
              <div class="mb-2 p-1 cursor-pointer" @click="removeTime(day, i)">
                <x-icon class="h-5 w-5 stroke-2 stroke-red-500 fill-transparent" />
              </div>
            </div>
          </div>
        </div>
        <secondary-button
          :label="t('label.addDay')"
          class="!text-sm !text-teal-500 !h-8 self-center"
          @click="showDatePicker = true"
        />
      </div>
    </div>
    <!-- action buttons -->
    <div class="flex gap-4 mt-auto">
      <secondary-button
        :label="t('label.cancel')"
        @click="emit('cancel')"
        class="w-1/2"
      />
      <primary-button
        v-show="activeStep1"
        :label="t('label.next')"
        :disabled="!validStep1"
        @click="validStep1 ? emit('next') : null"
        class="w-1/2"
      />
      <primary-button
        v-show="activeStep2"
        :label="t('label.create')"
        :disabled="!validStep1 || !validStep2"
        @click="validStep1 && validStep2 ? createAppointment() : null"
        class="w-1/2"
      />
    </div>
    <div v-show="showDatePicker" class="absolute position-center rounded-lg bg-white shadow w-11/12 p-4 ">
      <!-- monthly mini calendar -->
      <calendar-month
        :selected="activeDate"
        :mini="true"
        :nav="true"
        @prev="dateNav('month', false)"
        @next="dateNav('month')"
        @day-selected="addDate"
      />
    </div>
  </div>
  <!-- modals -->
  <appointment-created-modal
    :open="createdConfirmation.show"
    :title="createdConfirmation.title"
    :public-link="createdConfirmation.publicLink"
    @close="closeCreatedModal"
  />
</template>

<script setup>
import { locationTypes } from '@/definitions';
import { ref, reactive, computed, inject, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import AppointmentCreatedModal from '@/components/AppointmentCreatedModal';
import CalendarMonth from '@/components/CalendarMonth';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';
import TabBar from '@/components/TabBar';

// icons
import {
  AlertTriangleIcon,
  CheckIcon,
  ChevronDownIcon,
  PlusIcon,
  XIcon,
} from "vue-tabler-icons";

// component constants
const { t } = useI18n();
const dj = inject("dayjs");
const call = inject('call');
const baseurl = inject('baseurl');

// component emits
const emit = defineEmits(['start', 'next', 'create', 'cancel']);

// component properties
const props = defineProps({
  status:    Number, // dialog creation progress [hidden: 0, details: 1, availability: 2, finished: 3]
  calendars: Array,  // list of user defined calendars
});

// calculate the current visible step by given status
// first step are the appointment details
// second step are the availability slots
const activeStep1 = computed(() => props.status === 1 || props.status === 3);
const activeStep2 = computed(() => props.status === 2);

// tab navigation for location types
const updateLocationType = type => {
  appointment.location_type = locationTypes[type];
};

// defaul appointment object (for start and reset) and appointment form data
const defaultAppointment = {
  title:         '',
  calendar_id:   props.calendars[0].id,
  location_type: locationTypes.inPerson,
  location_url:  '',
  details:       '',
  status:        2, // appointment is opened | TODO: make configurable sometime
};
const appointment = reactive({...defaultAppointment});

// date and time selection data
// an object having the iso date as key and a list of objects holding start and end time for each day
// format: {'2022-12-01': [{ start: '10:00', end: '11:30'}, ...], ...}
const slots = reactive({});

// bring slots into list form for requests later
// format: [{ start: '2022-12-01T10:00:00', duration: 90}, ...]
const slotList = computed(() => {
  const list = [];
  for (const day in slots) {
    if (Object.hasOwnProperty.call(slots, day)) {
      const times = slots[day];
      times.forEach(slot => {
        const start = dj(day + ' ' + slot.start);
        const end = dj(day + ' ' + slot.end);
        list.push({
          start: start.format('YYYY-MM-DDTHH:mm:ss'),
          duration: end.diff(start, 'minutes')
        });
      });
    }
  }
  return list;
});

// handle notes char limit
const charLimit      = 250;
const charCount      = computed(() => appointment.details.length);

// calculate validity of input data for each step (to show corresponding indicators)
const validStep1     = computed(() => appointment.title !== '');
const validStep2     = computed(() => Object.keys(slots).length > 0);
const visitedStep1   = ref(false);
const visitedStep2   = ref(false);
const invalidStep1   = computed(() => !validStep1.value && visitedStep1.value);
const invalidStep2   = computed(() => !validStep2.value && visitedStep2.value);

// show mini month date picker
const showDatePicker = ref(false);
const activeDate     = ref(dj());

// handle date and time input of user
const addDate = (d) => {
  const day = dj(d).format('YYYY-MM-DD');
  if (!Object.hasOwn(slots, day)) {
    slots[day] = [{
      start: dj(d).add(10, 'hours').format('HH:mm'),
      end: dj(d).add(11, 'hours').format('HH:mm')
    }];
  }
  showDatePicker.value = false;
};
const addTime = (d) => {
  const day = dj(d).format('YYYY-MM-DD');
  // get latest end time to start next time slot default value with
  const latestTime = slots[day].reduce((p, c) => c.end > p ? c.end : p, '00:00');
  slots[day].push({
    start: latestTime,
    end: dj(day + 'T' + latestTime).add(1, 'hour').format('HH:mm')
  });
};
const removeTime = (day, index) => {
  if (slots[day].length < 2) {
    delete slots[day];
  } else {
    slots[day].splice(index, 1);
  }
};

// show confirmation dialog
const createdConfirmation = reactive({
  show: false,
  title: '',
  publicLink: ''
});
const closeCreatedModal = () => createdConfirmation.show = false;

// handle actual appointment creation
const createAppointment = async () => {
  // build data object for post request
  const obj = {
    appointment: appointment,
    slots: slotList.value
  };
  // save selected appointment data
  const { data } = await call('apmt').post(obj).json();

  // show confirmation
  createdConfirmation.title = data.value.title;
  createdConfirmation.publicLink = baseurl + data.value.slug; // TODO
  createdConfirmation.show = true;
  // reset everything to start again
  for (const attr in defaultAppointment) {
    appointment[attr] = defaultAppointment[attr];
  }
  for (const attr in slots) {
    delete slots[attr];
  }
  visitedStep1.value = false;
  visitedStep2.value = false;
  emit('create');
};

// date navigation
const dateNav = (unit = 'month', forward = true) => {
  if (forward) {
    activeDate.value = activeDate.value.add(1, unit);
  } else {
    activeDate.value = activeDate.value.subtract(1, unit);
  }
};

// track if steps were already visited
watch(() => props.status, (newValue, oldValue) => {
  if (oldValue === 1) visitedStep1.value = true;
  if (oldValue === 2 && newValue !== 3) visitedStep2.value = true;
});
</script>
