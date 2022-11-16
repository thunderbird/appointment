<template>
  <div class="relative flex flex-col gap-4 h-full">
    <div class="text-teal-500 font-semibold text-center text-xl">
      {{ t('heading.createNewAppointment') }}
    </div>
    <div class="text-gray-700 bg-gray-100 rounded-lg p-4 flex flex-col gap-2">
      <div class="flex justify-between items-center cursor-pointer" @click="emit('start')">
        <span class="font-semibold flex gap-1">
          <icon-check v-show="validStep1" class="h-6 w-6 stroke-2 stroke-teal-500 fill-transparent" />
          <icon-alert-triangle v-show="invalidStep1" class="h-6 w-6 stroke-2 stroke-red-500 fill-transparent" />
          {{ t('label.appointmentDetails') }}
        </span>
        <icon-chevron-down
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
            v-model="appointment.name"
            :placeholder="t('placeholder.biWeeklyCafeDates')"
            class="rounded-md bg-gray-50 border-gray-200 w-full"
          />
        </label>
        <label>
          <div class="font-medium text-gray-500 mb-1">{{ t('label.selectCalendar') }}</div>
          <select v-model="appointment.calendar" class="rounded-md bg-gray-50 border-gray-200 w-full">
            <option value="p">Personal</option>
            <option value="w">Work</option>
            <option value="f">Freelance</option>
          </select>
        </label>
        <label>
          <div class="font-medium text-gray-500 mb-1">{{ t('label.location') }}</div>
          <tab-bar
            :tab-items="Object.keys(locationTypes)"
            :active="locationTypeActive"
            @update="updateLocationType"
          />
        </label>
        <label>
          <div class="font-medium text-gray-500 mb-1">{{ t('label.videoLink') }}</div>
          <input
            type="text"
            v-model="appointment.videoLink"
            :placeholder="t('placeholder.zoomCom')"
            class="rounded-md bg-gray-50 border-gray-200 w-full"
          />
        </label>
        <label class="relative">
          <div class="font-medium text-gray-500 mb-1">{{ t('label.notes') }}</div>
          <textarea
            v-model="appointment.notes"
            :placeholder="t('placeholder.writeHere')"
            class="rounded-md bg-gray-50 border-gray-200 w-full text-sm h-40 resize-none"
            :maxlength="charLimit"
          ></textarea>
          <div class="absolute bottom-3.5 right-3 text-xs" :class="{ 'text-red-700': charCount === charLimit }">
            {{ charCount }}/{{ charLimit }}
          </div>
        </label>
      </div>
    </div>
    <div class="text-gray-700 bg-gray-100 rounded-lg p-4 flex flex-col gap-2">
      <div class="flex justify-between items-center cursor-pointer" @click="emit('next')">
        <span class="font-semibold flex gap-1">
          <icon-check v-show="validStep2" class="h-6 w-6 stroke-2 stroke-teal-500 fill-transparent" />
          <icon-alert-triangle v-show="invalidStep2" class="h-6 w-6 stroke-2 stroke-red-500 fill-transparent" />
          {{ t('label.chooseYourAvailability') }}
        </span>
        <icon-chevron-down
          class="h-6 w-6 stroke-1 stroke-gray-800 fill-transparent rotate-90 transition-transform"
          :class="{ 'rotate-0': activeStep2 }"
        />
      </div>
      <div v-show="activeStep2" class="flex flex-col gap-3">
        <hr />
        <div v-show="!validStep2" class="text-sm">{{ t('text.defineDaysAndTimeSlots') }}</div>
        <div v-show="validStep2">
          <div v-for="(s, i) in appointment.slots" :key="s.start" class="flex gap-4 items-end mb-2">
            <label class="flex flex-col text-sm">
              {{ t('label.start') }}
              <input
                type="time"
                :value="dj(s.start).format('HH:mm')"
                class="rounded-md bg-gray-50 border-gray-200"
              />
            </label>
            <label class="flex flex-col text-sm">
              {{ t('label.end') }}
              <input
                type="time"
                :value="dj(s.start).add(s.duration, 'minutes').format('HH:mm')"
                class="rounded-md bg-gray-50 border-gray-200"
              />
            </label>
            <div class="mb-2 p-1 cursor-pointer" @click="removeTime(i)">
              <icon-x class="h-5 w-5 stroke-2 stroke-red-500 fill-transparent" />
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
        @click="validStep1 && validStep2 ? emit('create') : null"
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
        @selected="addDate"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, inject, watch } from 'vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import IconX from '@/elements/icons/IconX.vue';
import IconCheck from '@/elements/icons/IconCheck.vue';
import IconAlertTriangle from '@/elements/icons/IconAlertTriangle.vue';
import IconChevronDown from '@/elements/icons/IconChevronDown.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// component properties
const props = defineProps({
  status: Number, // dialog creation progress [hidden: 0, details: 1, availability: 2, finished: 3]
});

// calculate the current visible step by given status
const activeStep1 = computed(() => props.status === 1);
const activeStep2 = computed(() => props.status === 2);

// tab navigation for location types
const locationTypes = { 'inPerson': 0, 'online': 1 };
const locationTypeActive = ref(locationTypes.inPerson);
const updateLocationType = type => {
  locationTypeActive.value = locationTypes[type];
};

// appointment form data
const appointment = reactive({
  name: '',
  calendar: 'p',
  locationType: locationTypeActive.value,
  videoLink: '',
  notes: '',
  slots: []
});

// handle notes char limit
const charLimit = 250;
const charCount = computed(() => appointment.notes.length);

// calculate validity of input data for each step (to show corresponding indicators)
const validStep1 = computed(() => appointment.name !== '');
const validStep2 = computed(() => appointment.slots.length > 0);
const visitedStep1 = ref(false);
const visitedStep2 = ref(false);
const invalidStep1 = computed(() => !validStep1.value && visitedStep1.value);
const invalidStep2 = computed(() => !validStep2.value && visitedStep2.value);

// show mini month date picker
const showDatePicker = ref(false);
const activeDate = ref(dj());
const addDate = (d) => {
  appointment.slots.push({
    start: dj(d).add(10, 'hours').format(),
    duration: 90
  });
  showDatePicker.value = false;
};

// date navigation
const dateNav = (unit = 'month', forward = true) => {
  if (forward) {
    activeDate.value = activeDate.value.add(1, unit);
  } else {
    activeDate.value = activeDate.value.subtract(1, unit);
  }
};

// component emits
const emit = defineEmits(['start', 'next', 'create', 'cancel']);

// track if steps were already visited
watch(() => props.status, (_, oldValue) => {
  if (oldValue === 1) visitedStep1.value = true;
  if (oldValue === 2) visitedStep2.value = true;
});
</script>
