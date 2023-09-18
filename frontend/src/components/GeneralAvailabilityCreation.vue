<template>
  <div class="relative flex flex-col gap-4 h-full">
    <div class="font-semibold text-center text-xl text-teal-500">
      {{ t("heading.createGeneralAvailability") }}
    </div>
    <!-- step 1 -->
    <div
      class="rounded-lg p-4 flex flex-col gap-2 text-gray-700 dark:text-gray-100 bg-gray-100 dark:bg-gray-600"
    >
      <div
        class="flex justify-between items-center cursor-pointer"
        @click="setStep(1)"
      >
        <span class="font-semibold flex gap-1">
          <icon-check
            v-show="validStep1"
            class="h-6 w-6 stroke-2 fill-transparent stroke-teal-500"
          />
          <icon-alert-triangle
            v-show="invalidStep1"
            class="h-6 w-6 stroke-2 fill-transparent stroke-rose-500"
          />
          {{ t("label.generalAvailabilityDetails") }}
        </span>
        <icon-chevron-down
          class="h-6 w-6 stroke-1 fill-transparent rotate-90 transition-transform stroke-gray-800 dark:stroke-gray-100"
          :class="{ 'rotate-0': activeStep1 }"
        />
      </div>
      <div v-show="activeStep1" class="flex flex-col gap-2">
        <hr />
        <label>
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.appointmentName") }}
          </div>
          <input
            type="text"
            v-model="appointment.title"
            :placeholder="t('placeholder.biWeeklyCafeDates')"
            class="rounded-md w-full place-holder"
          />
        </label>
        <label>
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.location") }}
          </div>
          <tab-bar
            :tab-items="locationTypes"
            :active="appointment.location_type"
            @update="updateLocationType"
          />
        </label>
        <label>
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.videoLink") }}
          </div>
          <input
            type="text"
            v-model="appointment.location_url"
            :placeholder="t('placeholder.zoomCom')"
            class="rounded-md w-full place-holder"
          />
        </label>
        <label class="relative">
          <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t("label.notes") }}
          </div>
          <textarea
            v-model="appointment.details"
            :placeholder="t('placeholder.writeHere')"
            class="rounded-md w-full text-sm h-40 resize-none place-holder"
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
        class="flex justify-between items-center cursor-pointer"
        @click="setStep(2)"
      >
        <span class="font-semibold flex gap-1">
          <icon-check
            v-show="validStep2"
            class="h-6 w-6 stroke-2 fill-transparent stroke-teal-500"
          />
          <icon-alert-triangle
            v-show="invalidStep2"
            class="h-6 w-6 stroke-2 fill-transparent stroke-rose-500"
          />
          {{ t("label.chooseYourAvailability") }}
        </span>
        <icon-chevron-down
          class="h-6 w-6 stroke-1 fill-transparent rotate-90 transition-transform stroke-gray-800 dark:stroke-gray-100"
          :class="{ 'rotate-0': activeStep2 }"
        />
      </div>
      <div v-show="activeStep2" class="flex flex-col gap-3">
        <hr />
        <div class="flex flex-col gap-2">
          <div
            class="flex justify-between items-end mb-2 remove-end-date-container"
          >
            <label class="flex flex-col">
              <div class="text-sm text-gray-500 dark:text-gray-300">
                {{ t("label.startDate") }}
              </div>
              <input
                type="text"
                v-model="startDate"
                class="input-narrow rounded-md text-sm py-1"
                @click="showStartDatePicker = true"
              />
              <!-- <input type="date" class="rounded-md text-sm py-1" /> -->
            </label>
            <label class="flex flex-col">
              <div class="text-sm text-gray-500 dark:text-gray-300">
                {{ t("label.endDate") }}
              </div>
              <input
                type="text"
                class="input-narrow rounded-md text-sm py-1 border-2 border-rose-50"
                v-model="endDate"
                @click="showEndDatePicker = true"
              />

              <!-- <input type="date" class="rounded-md text-sm py-1" /> -->
            </label>
            <div
              v-if="endDate !== 'never'"
              class="remove-end-date mb-2 p-1 cursor-pointer"
              @click="removeEndDate()"
            >
              <icon-x
                class="h-5 w-5 stroke-2 fill-transparent stroke-rose-500"
              />
            </div>
          </div>
          <div class="flex gap-4 justify-between items-end mb-2">
            <label class="flex flex-col">
              <div class="text-sm text-gray-500 dark:text-gray-300">
                {{ t("label.startTime") }}
              </div>
              <input
                type="time"
                class="rounded-md text-sm py-1"
                v-model="startTime"
              />
            </label>
            <label class="flex flex-col">
              <div class="text-sm text-gray-500 dark:text-gray-300">
                {{ t("label.endTime") }}
              </div>
              <input
                type="time"
                class="rounded-md text-sm py-1"
                v-model="endTime"
              />
            </label>
          </div>
          <div class="flex flex-col gap-2 mb-2">
            <div class="text-sm text-gray-500 dark:text-gray-300">
              {{ t("label.availableDays") }}
            </div>
            <div class="flex flex-row justify-start">
              <div class="flex flex-col mr-6">
                <label class="mb-2">
                  <input type="checkbox" value="Sunday" />
                  Sunday
                </label>
                <label class="mb-2">
                  <input type="checkbox" value="Monday" checked />
                  Monday
                </label>
                <label class="mb-2">
                  <input type="checkbox" value="Tuesday" checked />
                  Tuesday
                </label>
                <label class="mb-2">
                  <input type="checkbox" value="Wednesday" checked />
                  Wednesday
                </label>
              </div>
              <div class="flex flex-col">
                <label class="mb-2">
                  <input type="checkbox" value="Thursday" checked />
                  Thursday
                </label>
                <label class="mb-2">
                  <input type="checkbox" value="Friday" checked />
                  Friday
                </label>
                <label class="mb-2">
                  <input type="checkbox" value="Saturday" />
                  Saturday
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- step 3 -->
    <div
      class="rounded-lg p-4 flex flex-col gap-2 text-gray-700 dark:text-gray-100 bg-gray-100 dark:bg-gray-600"
    >
      <div
        class="flex justify-between items-center cursor-pointer"
        @click="setStep(3)"
      >
        <span class="font-semibold flex gap-1">
          <icon-check
            v-show="validStep3"
            class="h-6 w-6 stroke-2 fill-transparent stroke-teal-500"
          />
          <icon-alert-triangle
            v-show="invalidStep3"
            class="h-6 w-6 stroke-2 fill-transparent stroke-rose-500"
          />
          {{ t("label.availabilityBookingSettings") }}
        </span>
        <icon-chevron-down
          class="h-6 w-6 stroke-1 fill-transparent rotate-90 transition-transform stroke-gray-800 dark:stroke-gray-100"
          :class="{ 'rotate-0': activeStep3 }"
        />
      </div>
      <div v-show="activeStep3" class="flex flex-col gap-3 gap-4">
        <hr />
        <div class="flex flex-col gap-2">
          <div class="flex gap-4 justify-between items-end mb-2">
            <label class="flex flex-col">
              <div class="text-sm text-gray-500 dark:text-gray-300">
                {{ t("label.bookingEarliest") }}
              </div>
              <input
                type="number"
                class="rounded-md text-sm py-1 input-narrow"
                v-model="hoursBefore"
              />
            </label>
            <label class="flex flex-col">
              <div class="text-sm text-gray-500 dark:text-gray-300">
                {{ t("label.bookingLatest") }}
              </div>
              <input
                type="number"
                class="rounded-md text-sm py-1 input-narrow"
                v-model="weeksBefore"
              />
            </label>
          </div>
          <div class="flex flex-col gap-2 mb-3">
            <label class="flex flex-col units-container">
              <div class="text-sm text-gray-500 dark:text-gray-300">
                {{ t("label.slotLength") }}
              </div>
              <input
                type="number"
                class="rounded-md text-sm py-1"
                v-model="slotLength"
              />
              <div class="units text-sm">
                <span>{{ slotLength }}</span>
                mins
              </div>
            </label>
          </div>
          <div class="flex gap-4 justify-center items-end mb-2">
            <label class="flex flex-col">
              <p>
                Recipients can schedule an appointment between
                <b>{{ hoursBefore }} hours</b> and
                <b>{{ weeksBefore }} weeks</b>
                ahead of time.
              </p>
            </label>
          </div>
        </div>
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
        v-show="activeStep1 || activeStep2"
        :label="t('label.next')"
        class="w-1/2"
      />
      <primary-button
        v-show="activeStep3"
        :label="t('label.create')"
        class="w-1/2"
      />
    </div>
    <div
      v-show="showStartDatePicker"
      class="absolute position-center rounded-lg shadow w-11/12 p-4 bg-white dark:bg-gray-700"
    >
      <!-- monthly mini calendar -->
      <calendar-month
        :selected="activeDate"
        :mini="true"
        :nav="true"
        :min-date="dj()"
        @prev="dateNav('month', false)"
        @next="dateNav('month')"
        @day-selected="setStartDate"
      />
    </div>
    <div
      v-show="showEndDatePicker"
      class="absolute position-center rounded-lg shadow w-11/12 p-4 bg-white dark:bg-gray-700"
    >
      <!-- monthly mini calendar -->
      <calendar-month
        :selected="activeDate"
        :mini="true"
        :nav="true"
        :min-date="dj()"
        @prev="dateNav('month', false)"
        @next="dateNav('month')"
        @day-selected="setEndDate"
      />
    </div>
  </div>
</template>
<script setup>
import { locationTypes } from "@/definitions";
import { ref, reactive, computed, inject, watch } from "vue";
import { useI18n } from "vue-i18n";
import CalendarMonth from "@/components/CalendarMonth";
import PrimaryButton from "@/elements/PrimaryButton";
import SecondaryButton from "@/elements/SecondaryButton";
import TabBar from "@/components/TabBar";

// icons
import {
  IconAlertTriangle,
  IconCheck,
  IconChevronDown,
  IconPlus,
  IconX,
} from "@tabler/icons-vue";

// component constants
const { t } = useI18n();
const dj = inject("dayjs");

// component emits
const emit = defineEmits(["start", "next", "create", "cancel"]);

// component properties
// const props = defineProps({
//   status: Number, // dialog creation progress [hidden: 0, details: 1, availability: 2, finished: 3]
//   user: Object, // currently logged in user, null if not logged in
// });

// calculate the current visible step by given status
// first step are the appointment details
// second step are the availability slots
// const activeStep1 = computed(() => props.status === 1 || props.status === 3);
// const activeStep2 = computed(() => props.status === 2);
const activeStep1 = ref(true);
const activeStep2 = ref(false);
const activeStep3 = ref(false);

function setStep(num) {
  activeStep1.value = false;
  activeStep2.value = false;
  activeStep3.value = false;

  switch (num) {
    case 1:
      activeStep1.value = true;
      break;
    case 2:
      activeStep2.value = true;
      break;
    case 3:
      activeStep3.value = true;
      break;
    default:
      break;
  }
}

// default appointment object (for start and reset) and appointment form data
const defaultAppointment = {
  title: "",
  // calendar_id: props.calendars[0]?.id,
  location_type: locationTypes.inPerson,
  location_url: "",
  details: "",
  status: 2, // appointment is opened | TODO: make configurable sometime
};

const appointment = reactive({ ...defaultAppointment });
const appointmentCreationError = ref(null);
// tab navigation for location types
const updateLocationType = (type) => {
  appointment.location_type = locationTypes[type];
};

const hoursBefore = ref(24);
const weeksBefore = ref(2);
const slotLength = ref(30);

const startTime = ref("09:00");
const endTime = ref("17:00");
const startDate = ref("08/21/2023");
const endDate = ref("never");

// show mini month date picker
const showStartDatePicker = ref(false);
const showEndDatePicker = ref(false);
const activeDate = ref(dj());

// handle date and time input of user
const setStartDate = (d) => {
  // const day = dj(d).format("YYYY-MM-DD");
  const date = dj(d).format("MM/DD/YYYY");
  // if (!Object.hasOwn(slots, day)) {
  //   slots[day] = [
  //     {
  //       start: dj(d).add(10, "hours").format("HH:mm"),
  //       end: dj(d).add(11, "hours").format("HH:mm"),
  //     },
  //   ];
  // }
  startDate.value = date;
  showStartDatePicker.value = false;
};
// handle date and time input of user
const setEndDate = (d) => {
  // const day = dj(d).format("YYYY-MM-DD");
  const date = dj(d).format("MM/DD/YYYY");
  // if (!Object.hasOwn(slots, day)) {
  //   slots[day] = [
  //     {
  //       start: dj(d).add(10, "hours").format("HH:mm"),
  //       end: dj(d).add(11, "hours").format("HH:mm"),
  //     },
  //   ];
  // }
  endDate.value = date;
  showEndDatePicker.value = false;
};

function removeEndDate() {
  endDate.value = "never";
}
</script>

<style scoped>
input[type="checkbox"]:checked {
  background-color: unset;
}
.input-narrow {
  width: 120px;
}
.units-container {
  position: relative;
}
.units {
  position: absolute;
  top: 1.61rem;
  left: 0.9rem;
}

.units span {
  visibility: hidden;
}
.remove-end-date-container {
  position: relative;
}
.remove-end-date {
  position: absolute;
  z-index: 9;
  right: 0;
  top: 1.61rem;
}
</style>
