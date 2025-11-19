<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { PrimaryButton, LinkButton } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';

import GradientCheckCircle from '../components/GradientCheckCircle.vue';
import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();
const ftueStore = useFTUEStore();
</script>

<template>
  <step-title :title="t('ftue.connectGoogleCalendar')" />

  <p class="info-text">{{ t('ftue.connectGoogleCalendarInfo') }}</p>

  <div class="permission-container">
    <gradient-check-circle />
    <div>
      <strong>{{ t('ftue.googlePermissionOneTitle') }}</strong>
      <p>{{ t('ftue.googlePermissionOneDescription') }}</p>
    </div>
  </div>

  <div class="permission-container">
    <gradient-check-circle />
    <div>
      <strong>{{ t('ftue.googlePermissionTwoTitle') }}</strong>
      <p>{{ t('ftue.googlePermissionTwoDescription') }}</p>
    </div>
  </div>

  <i18n-t
    :keypath="`ftue.googlePermissionDisclaimer`"
    tag="p"
    :for="`ftue.googlePermissionDisclaimer`"
  >
    <a
      class="underline"
      href="https://developers.google.com/terms/api-services-user-data-policy"
      target="_blank"
    >
      {{ t(`text.settings.connectedApplications.connect.googleLegal.link`) }}
    </a>
  </i18n-t>

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
.info-text {
  margin-block-end: 1.5rem;
}

.permission-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-block-end: 1.5rem;

  strong {
    color: black;
    font-weight: 600;
    margin-block-end: 0.5rem;
  }
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 3.125rem;

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>