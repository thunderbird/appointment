<script setup lang="ts">
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { PrimaryButton } from '@thunderbirdops/services-ui';
import { useUserStore } from '@/stores/user-store';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();

const router = useRouter();
const userStore = useUserStore();

const onContinueButtonClick = async () => {
  router.push('/dashboard');
};

onMounted(async () => {
  await userStore.finishFTUE();
  await userStore.profile();

  // Clear the FTUE flow
  window.localStorage?.removeItem('tba/ftue');

  // Redirect to dashboard after a delay
  setTimeout(() => router.push('/dashboard'), 5000);
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