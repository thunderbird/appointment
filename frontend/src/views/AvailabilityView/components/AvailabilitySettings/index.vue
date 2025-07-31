<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { BubbleSelect, TextInput, SwitchToggle, CheckboxInput } from '@thunderbirdops/services-ui';
import { dayjsKey, isoWeekdaysKey } from '@/keys';
import { useUserStore } from '@/stores/user-store';
import { SelectOption } from '@/models';

import AvailabilityCalendarSelect from './components/AvailabilityCalendarSelect.vue';
import AvailabilitySelect from './components/AvailabilitySelect.vue';
import RadioGroupPill from '../RadioGroupPill.vue';

const { t } = useI18n();
const dj = inject(dayjsKey);
const isoWeekdays = inject(isoWeekdaysKey);

const userStore = useUserStore();

const isBookable = ref(false);
const useCustomAvailabilities = ref(false);
const minimumNotice = ref("instant");
const bookingWindow = ref("7_days");

const scheduleDayOptions: SelectOption[] = isoWeekdays.map((day) => ({
  label: day.min[0],
  value: day.iso,
}));
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
      <p>{{ userStore.data.settings.timezone ?? dj.tz.guess() }}</p>
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
    />

    <hr />

    <!-- Available days and times -->
    <h3>{{ t('label.availableDaysAndTimes') }}:</h3>
    <checkbox-input
      name="customizePerDay"
      :label="t('label.customizePerDay')"
      v-model="useCustomAvailabilities"
    />

    <!-- Availability with customization -->
    <template v-if="useCustomAvailabilities">
      <availability-select
        class="availability-times-container"
        :options="scheduleDayOptions"
        :availabilities="[]"
        :start-time="''"
        :end-time="''"
        :slot-duration="1"
        :required="true"
        @update="() => {}"
      />
    </template>

    <!-- Availability without customization -->
    <template v-if="!useCustomAvailabilities">
      <div class="availability-times-container">
        <text-input
          type="time"
          name="start_time"
          class="full-width"
        >
          {{ t("label.startTime") }}
        </text-input>

        <span class="to-span">{{ t("label.to") }}</span>

        <text-input
          type="time"
          name="end_time"
          class="full-width"
        >
          {{ t("label.endTime") }}
        </text-input>
      </div>
      <bubble-select
        :options="scheduleDayOptions"
        :required="false"
      />
    </template>

    <!-- Minimum notice -->
    <radio-group-pill
      v-model="minimumNotice"
      name="minimum-notice"
      :legend="t('label.minimumNotice')"
      :options="[
        { label: 'Instant', value: 'instant' },
        { label: '12 Hrs', value: '12_hours' },
        { label: '2 Days', value: '2_days' },
        { label: '3 Days', value: '3_days' },
        { label: '4 Days', value: '4_days' },
        { label: '5 Days', value: '5_days' },
      ]"
    />

    <!-- Booking window -->
    <radio-group-pill
      v-model="bookingWindow"
      name="booking-window"
      :legend="t('label.bookingWindow')"
      :options="[
        { label: '7 Days', value: '7_days' },
        { label: '14 Days', value: '14_days' },
        { label: '21 Days', value: '21_days' },
        { label: 'A Month', value: 'a_month' },
      ]"
    />
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