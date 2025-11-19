<script setup lang="ts">
import { LinkButton, PrimaryButton, SelectInput, TextInput } from '@thunderbirdops/services-ui';
import { useI18n } from 'vue-i18n';
import { useFTUEStore } from '@/stores/ftue-store';

const { t } = useI18n();
const ftueStore = useFTUEStore();

const calendarOptions = [];
</script>

<template>
  <h2>{{ t('ftue.createBookingPage') }}</h2>

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
h2 {
  font-size: 2.25rem;
  font-family: metropolis;
  font-weight: normal;
  letter-spacing: -0.36px;
  line-height: 1.2;
  color: var(--colour-ti-highlight);
  margin: 0 0 1.5rem 0;
}

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