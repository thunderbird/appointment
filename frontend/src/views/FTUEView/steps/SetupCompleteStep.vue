<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { useFTUEStore } from '@/stores/ftue-store';
import { PrimaryButton } from '@thunderbirdops/services-ui';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();
const ftueStore = useFTUEStore();
</script>

<template>
  <div class="setup-complete-container">
    <div class="setup-complete-title-container">
      <step-title :title="t('ftue.setupComplete')" />
    </div>

    <h3>{{ t('ftue.thunderbirdAppointmentIsReady') }}</h3>
    <p>{{ t('ftue.redirectingToDashboard') }}</p>

    <primary-button :title="t('ftue.continueToDashboard')" @click="ftueStore.nextStep()">
      {{ t('ftue.continueToDashboard') }}
    </primary-button>
  </div>
</template>

<style scoped>
h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: black;
  margin-block-end: 1rem;
}

p {
  margin-block-end: 4.75rem;
}

.setup-complete-container {
  display: flex;
  flex-direction: column;
  align-items: center;

  .setup-complete-title-container {
    margin-block-end: 3rem;
  }
}
</style>