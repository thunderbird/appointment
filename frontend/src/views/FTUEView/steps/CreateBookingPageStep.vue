<script setup lang="ts">
import { LinkButton, PrimaryButton, SelectInput, TextInput } from '@thunderbirdops/services-ui';
import { useI18n } from 'vue-i18n';
import { useFTUEStore } from '@/stores/ftue-store';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();
const ftueStore = useFTUEStore();

const calendarOptions = [];
</script>

<template>
  <step-title :title="t('ftue.createBookingPage')" />

  <text-input
    name="bookingPageTitle"
    :placeholder="t('ftue.bookingPagePlaceholder')"
    :help="t('ftue.bookingPageTitleHelp')"
    class="booking-page-title-input"
    required
  >
    {{ t('ftue.bookingPageTitle') }}
  </text-input>

  <select-input
    name="calendarForNewAppointments"
    :options="calendarOptions"
    :help="t('ftue.calendarForNewAppointmentsHelp')"
    required
  >
    {{ t('ftue.calendarForNewAppointments') }}
  </select-input>

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
.booking-page-title-input {
  margin-block-end: 2.25rem;
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 10.30rem;

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>