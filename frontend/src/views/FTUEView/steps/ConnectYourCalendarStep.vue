<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { PrimaryButton, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import calendarIcon from '@/assets/svg/icons/calendar.svg';
import googleCalendarLogo from '@/assets/svg/google-calendar-logo.svg';
import mailIcon from '@/assets/svg/icons/mail.svg';
import { FtueStep } from '@/definitions';

import StepTitle from '../components/StepTitle.vue';
import RadioProviderCardButton from '../components/RadioProviderCardButton.vue';

const { t } = useI18n();

const calendarStore = useCalendarStore();
const ftueStore = useFTUEStore();
const { errorMessage } = storeToRefs(ftueStore);

type CalendarProvider = 'caldav' | 'google' | 'oidc';
const calendarProvider = ref<CalendarProvider | null>('oidc');
const isLoading = ref(false);

const onBackButtonClick = () => {
  ftueStore.moveToStep(FtueStep.SetupProfile, true);
};

const onContinueButtonClick = async () => {
  ftueStore.clearMessages();

  switch (calendarProvider.value) {
    case 'oidc': {
      isLoading.value = true;
      try {
        const { data, error } = await calendarStore.connectOIDCCalendar();

        if (data.value?.detail?.message) {
          ftueStore.errorMessage = { title: data.value?.detail?.message };
          return;
        }

        if (error.value) {
          ftueStore.errorMessage = { title: t('error.somethingWentWrong') };
          return;
        }

        ftueStore.moveToStep(FtueStep.CreateBookingPage);
      } catch (err) {
        const message = err instanceof Error ? err.message : null;
        ftueStore.errorMessage = { title: message || t('error.somethingWentWrong') };
      } finally {
        isLoading.value = false;
      }
      break;
    }
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
  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage.title }}
  </notice-bar>

  <step-title :title="t('ftue.connectYourCalendar')" />
  <p>{{ t('ftue.connectYourCalendarInfo') }}</p>

  <div class="radio-group" role="radiogroup" :aria-label="t('ftue.connectYourCalendar')">
    <radio-provider-card-button
      :title="t('ftue.connectCalendarTBPro')"
      :description="t('ftue.connectCalendarTBProInfo')"
      :iconSrc="mailIcon"
      :iconAlt="t('ftue.appointmentLogo')"
      value="oidc"
      name="calendar-provider"
      v-model="calendarProvider"
    />

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
    <primary-button variant="outline" :title="t('label.back')" @click="onBackButtonClick" :disabled="isLoading">
      {{ t('label.back') }}
    </primary-button>
    <primary-button :title="t('label.continue')" @click="onContinueButtonClick" :disabled="!calendarProvider || isLoading">
      {{ isLoading ? t('label.connecting') : t('label.continue') }}
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

  button {
    min-width: 123px;
  }

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }

  button + button {
    margin-block-start: 0;
  }
}
</style>