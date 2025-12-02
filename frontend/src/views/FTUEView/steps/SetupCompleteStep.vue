<script setup lang="ts">
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { PrimaryButton } from '@thunderbirdops/services-ui';
import { useUserStore } from '@/stores/user-store';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();

const userStore = useUserStore();

const onContinueButtonClick = async () => {
  window.location.href = '/dashboard';
};

onMounted(async () => {
  await userStore.finishFTUE();
  await userStore.profile();

  // Clear the FTUE flow
  window.localStorage?.removeItem('tba/ftue');

  // Hard reload to dashboard after a delay so that
  // we initialize all the stores and data properly
  setTimeout(() => window.location.href = '/dashboard', 5000);
});
</script>

<template>
  <div class="setup-complete-container">
    <div class="setup-complete-title-container">
      <step-title :title="t('ftue.setupComplete')" />
    </div>

    <h3>{{ t('ftue.thunderbirdAppointmentIsReady') }}</h3>
    <p>{{ t('ftue.redirectingToDashboard') }}</p>

    <primary-button :title="t('ftue.continueToDashboard')" @click="onContinueButtonClick()">
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