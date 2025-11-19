<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { PrimaryButton, LinkButton } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import calendarIcon from '@/assets/svg/icons/calendar.svg';
import googleCalendarLogo from '@/assets/svg/google-calendar-logo.svg';

import StepTitle from '../components/StepTitle.vue';
import ProviderCardButton from '../components/ProviderCardButton.vue';

const { t } = useI18n();

const ftueStore = useFTUEStore();
</script>

<template>
  <step-title :title="t('ftue.connectYourCalendar')" />
  <p>{{ t('ftue.connectYourCalendarInfo') }}</p>

  <provider-card-button
    :title="t('ftue.connectCalendarCalDav')"
    :description="t('ftue.connectCalendarCalDavInfo')"
    :iconSrc="calendarIcon"
    :iconAlt="t('ftue.calendarIcon')"
  />

  <provider-card-button
    :title="t('ftue.connectCalendarGoogle')"
    :description="t('ftue.connectCalendarGoogleInfo')"
    :iconSrc="googleCalendarLogo"
    :iconAlt="t('ftue.googleCalendarLogo')"
  />

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
p {
  line-height: 1.32;
  margin-block-end: 1rem;
}

button + button {
  margin-block-start: 0.5rem;
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 4.25rem;

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }

  button + button {
    margin-block-start: 0;
  }
}
</style>