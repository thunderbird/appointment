<script setup lang="ts">
import { inject, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { BubbleSelect, TextInput, SwitchToggle, CheckboxInput, LinkButton } from '@thunderbirdops/services-ui';
import { dayjsKey, isoWeekdaysKey } from '@/keys';
import { useUserStore } from '@/stores/user-store';
import { useAvailabilityStore } from '@/stores/availability-store';
import { Availability, SelectOption } from '@/models';

import AvailabilityCalendarSelect from './components/AvailabilityCalendarSelect.vue';
import AvailabilitySelect from './components/AvailabilitySelect.vue';
import AvailabilityMinimumNoticePill from './components/AvailabilityMinimumNoticePill.vue';
import AvailabilityBookingWindowPill from './components/AvailabilityBookingWindowPill.vue';

const { t } = useI18n();
const dj = inject(dayjsKey);
const isoWeekdays = inject(isoWeekdaysKey);

const userStore = useUserStore();
const availabilityStore = useAvailabilityStore();
const router = useRouter();

const { currentState } = storeToRefs(availabilityStore);

const isBookable = computed({
  get: () => currentState.value.active,
  set: (value) => {
    availabilityStore.$patch({ currentState: { active: value } })
  }
})

const requiresBookingConfirmation = computed({
  get: () => currentState.value.booking_confirmation,
  set: (value) => {
    availabilityStore.$patch({ currentState: { booking_confirmation: value } })
  }
})

const useCustomAvailabilities = computed({
  get: () => currentState.value.use_custom_availabilities,
  set: (value) => {
    availabilityStore.$patch({ currentState: { use_custom_availabilities: value } })
  }
})

const startTime = computed({
  get: () => currentState.value.start_time,
  set: (value) => {
    availabilityStore.$patch({ currentState: { start_time: value } })
  }
})

const endTime = computed({
  get: () => currentState.value.end_time,
  set: (value) => {
    availabilityStore.$patch({ currentState: { end_time: value } })
  }
})

const slotDuration = computed({
  get: () => currentState.value.slot_duration,
  set: (value) => {
    availabilityStore.$patch({ currentState: { slot_duration: value } })
  }
})

const weekDays = computed({
  get: () => currentState.value.weekdays,
  set: (value) => {
    availabilityStore.$patch({ currentState: { weekdays: value } })
  }
})

const scheduleDayOptions: SelectOption[] = isoWeekdays.map((day) => ({
  label: day.min[0],
  value: day.iso,
}));

function onAvailabilitySelectUpdated(availabilities: Availability[]) {
  // Create a single array of availabilities from the list grouped by day of week
  // Only take valid availabilities and filter placeholder availabilities out
  const validAvailabilities = availabilities.map((a) => ({ ...a, schedule_id: currentState.value.id }));
  availabilityStore.$patch({ currentState: { availabilities: validAvailabilities } })
}
</script>

<script lang="ts">
export default {
  name: "AvailabilitySettings"
}
</script>

<template>
  <header>
    <h2>{{ t('heading.setYourAvailability') }}</h2>
    <switch-toggle
      class="toggle-bookable"
      name="active"
      no-legend
      :label="isBookable ? t('label.youAreBookable') : t('label.youAreNotBookable')"
      v-model="isBookable"
      :title="t('label.activateSchedule')"
      data-testid="availability-set-availability-toggle"
    />
  </header>

  <div class="fields-container">
    <!-- Time zone -->
    <div>
      <h3>{{ t('label.timeZone') }}:</h3>
      <div class="user-timezone-container">
        <p>{{ userStore.data.settings.timezone ?? dj.tz.guess() }}</p>
        <link-button @click="router.push({ name: 'settings' })">{{ t('label.edit') }}</link-button>
      </div>
    </div>

    <!-- Booking to (calendars) -->
    <div class="booking-to-calendar-container">
      <availability-calendar-select />
    </div>

    <!-- Automatically confirm booking checkbox -->
    <checkbox-input
      :name="t('label.automaticallyConfirmBookingsIfTimeIsAvailable')"
      :label="t('label.automaticallyConfirmBookingsIfTimeIsAvailable')"
      data-testid="availability-automatically-confirm-checkbox"
      v-model="requiresBookingConfirmation"
      :disabled="!currentState.active"
    />

    <hr />

    <!-- Available days and times -->
    <h3>{{ t('label.availableDaysAndTimes') }}:</h3>
    <checkbox-input
      name="customizePerDay"
      :label="t('label.customizePerDay')"
      v-model="useCustomAvailabilities"
      :disabled="!currentState.active"
    />

    <!-- Availability with customization -->
    <template v-if="useCustomAvailabilities">
      <availability-select
        :options="scheduleDayOptions"
        :availabilities="currentState.availabilities"
        :start-time="startTime"
        :end-time="endTime"
        :slot-duration="slotDuration"
        :required="true"
        v-model="weekDays"
        @update="onAvailabilitySelectUpdated"
        :disabled="!currentState.active"
      />
    </template>

    <!-- Availability without customization -->
    <template v-if="!useCustomAvailabilities">
      <div class="availability-times-container">
        <text-input
          type="time"
          name="start_time"
          class="full-width"
          v-model="startTime"
          :disabled="!currentState.active"
        >
          {{ t("label.startTime") }}
        </text-input>

        <span class="to-span">{{ t("label.to") }}</span>

        <text-input
          type="time"
          name="end_time"
          class="full-width"
          v-model="endTime"
          :disabled="!currentState.active"
        >
          {{ t("label.endTime") }}
        </text-input>
      </div>
      <bubble-select
        :options="scheduleDayOptions"
        :required="false"
        v-model="weekDays"
        :disabled="!currentState.active"
      />
    </template>

    <!-- Minimum notice -->
    <availability-minimum-notice-pill />

    <!-- Booking window -->
    <availability-booking-window-pill />
  </div>
</template>

<style scoped>
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-block-end: 2rem;

  .toggle-bookable.component-container {
    font-size: 0.75rem;
    gap: 1rem;
  }
}

h2 {
  font-size: 1.5rem;
}

h3 {
  font-size: 0.8125rem;
  font-weight: bold;
}

.full-width {
  width: 100%;
}

.fields-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .user-timezone-container {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .availability-times-container {
    display: flex;
    align-items: center;
    gap: 1.5rem;

    .to-span {
      margin-block-start: 1.25rem;
    }
  }
}
</style>