<script setup lang="ts">
import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { BubbleSelect, LinkButton, PrimaryButton, SelectInput, TextInput } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import { isoWeekdaysKey } from '@/keys';
import { SelectOption } from '@/models';

import StepTitle from '../components/StepTitle.vue';

const isoWeekdays = inject(isoWeekdaysKey);

const ftueStore = useFTUEStore();
const { t } = useI18n();

const scheduleDayOptions: SelectOption[] = isoWeekdays.map((day) => ({
  label: day.min[0],
  value: day.iso,
}));

const bookingDurationOptions = []
</script>

<template>
  <step-title :title="t('ftue.setYourAvailability')" />

  <div class="availability-container">
    <bubble-select
      name="selectDays"
      :options="scheduleDayOptions"
      required
    >
      {{ t('ftue.selectDays') }}
    </bubble-select>
  
    <div class="time-container">
      <text-input type="time" name="startTime" required class="time-input">
        {{ t('ftue.startTime') }}
      </text-input>
      <text-input type="time" name="endTime" required class="time-input">
        {{ t('ftue.endTime') }}
      </text-input>
    </div>
  
    <select-input
      name="bookingDuration"
      :options="bookingDurationOptions"
      required
    >
      {{ t('ftue.bookingDuration') }}
    </select-input>
  </div>

  <div class="buttons-container">
    <link-button :title="t('label.cancel')" @click="ftueStore.previousStep()">
      {{ t('label.cancel') }}
    </link-button>
    <primary-button :title="t('label.continue')" @click="ftueStore.nextStep()">
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
.availability-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .time-container {
    display: flex;
    gap: 1.5rem;

    .time-input {
      width: 100%;
    }
  }
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 7.75rem;

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>
