<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { PrimaryButton, LinkButton, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import calendarIcon from '@/assets/svg/icons/calendar.svg';
import googleCalendarLogo from '@/assets/svg/google-calendar-logo.svg';
import { FtueStep } from '@/definitions';

import StepTitle from '../components/StepTitle.vue';
import RadioProviderCardButton from '../components/RadioProviderCardButton.vue';

const accountDashboardUrl = import.meta.env.VITE_TB_ACCOUNT_DASHBOARD_URL;

const { t } = useI18n();

const ftueStore = useFTUEStore();
const { errorMessage } = storeToRefs(ftueStore);

type CalendarProvider = 'caldav' | 'google' | 'oidc';
const calendarProvider = ref<CalendarProvider | null>(null);

const onContinueButtonClick = async () => {
  ftueStore.clearMessages();

  switch (calendarProvider.value) {
    case 'oidc':
      // TODO: Implement OIDC flow (get the token and try to authenticate)
      break;
    case 'caldav':
      await ftueStore.moveToStep(FtueStep.ConnectCalendarsCalDav);
      break;
    case 'google':
      await ftueStore.moveToStep(FtueStep.ConnectCalendarsGoogle);
      break;
    default:
      break;
  }
};
</script>

<template>
  <step-title :title="t('ftue.connectYourCalendar')" />
  <p>{{ t('ftue.connectYourCalendarInfo') }}</p>

  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage.title }}
  </notice-bar>

  <div class="radio-group" role="radiogroup" :aria-label="t('ftue.connectYourCalendar')">
    <!-- TODO: Implement OIDC / TB Pro Calendar auto-connect through token -->
    <!-- <radio-provider-card-button
      :title="t('ftue.connectCalendarTBPro')"
      :description="t('ftue.connectCalendarTBProInfo')"
      :iconSrc="calendarIcon"
      :iconAlt="t('ftue.appointmentLogo')"
      value="oidc"
      name="calendar-provider"
      v-model="calendarProvider"
    /> -->

    <radio-provider-card-button
      :title="t('ftue.connectCalendarCalDav')"
      :description="t('ftue.connectCalendarCalDavInfo')"
      :iconSrc="calendarIcon"
      :iconAlt="t('ftue.calendarIcon')"
      value="caldav"
      name="calendar-provider"
      v-model="calendarProvider"
    />

    <radio-provider-card-button
      :title="t('ftue.connectCalendarGoogle')"
      :description="t('ftue.connectCalendarGoogleInfo')"
      :iconSrc="googleCalendarLogo"
      :iconAlt="t('ftue.googleCalendarLogo')"
      value="google"
      name="calendar-provider"
      v-model="calendarProvider"
    />
  </div>

  <div class="buttons-container">
    <link-button :title="t('label.cancel')">
      <a :href="accountDashboardUrl">
        {{ t('label.cancel') }}
      </a>
    </link-button>
    <primary-button :title="t('label.continue')" @click="onContinueButtonClick">
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
p {
  line-height: 1.32;
  margin-block-end: 1rem;
}

.notice-bar {
  margin-block-end: 1.5rem;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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