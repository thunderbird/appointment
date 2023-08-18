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
        @click="emit('start')"
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
  </div>
</template>
<script setup>
import { locationTypes } from "@/definitions";
import { ref, reactive, computed, inject, watch } from "vue";
import { useI18n } from "vue-i18n";

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
const activeStep1 = true;
const activeStep2 = true;
const activeStep3 = true;

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
</script>
