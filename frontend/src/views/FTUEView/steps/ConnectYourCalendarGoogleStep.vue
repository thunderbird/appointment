<script setup lang="ts">
import { ref, onMounted, inject } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { PrimaryButton, LinkButton } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { ExternalConnectionProviders, FtueStep } from '@/definitions';
import { callKey } from '@/keys';
import { BooleanResponse, Exception, ExceptionDetail } from '@/models';

import GradientCheckCircle from '../components/GradientCheckCircle.vue';
import StepTitle from '../components/StepTitle.vue';

const accountDashboardUrl = import.meta.env.VITE_TB_ACCOUNT_DASHBOARD_URL;
const initFlowKey = 'tba/startedCalConnect';

const call = inject(callKey);

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const user = useUserStore();
const ftueStore = useFTUEStore();
const calendarStore = useCalendarStore();
const externalConnectionStore = useExternalConnectionsStore();

const { calendars } = storeToRefs(calendarStore);

const isLoading = ref(false);
const errorMessage = ref(null);

const onContinueButtonClick = async () => {
  isLoading.value = true;

  try {
    // Create key so we can move to the next page after we come back
    localStorage?.setItem(initFlowKey, 'true');
    await calendarStore.connectGoogleCalendar(user.data.email);
  } catch (error) {
    errorMessage.value = error ? error.message : t('error.somethingWentWrong');
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  // First, let's check if we have any calendars
  await calendarStore.fetch(true);

  // Are we coming back from the Google OAuth flow?
  const hasFlowKey = localStorage?.getItem(initFlowKey);

  const noCalendarsError = hasFlowKey && calendars.value.length === 0;

  // Error occurred during flow
  if (route.query.error || noCalendarsError) {
    localStorage?.removeItem(initFlowKey);

    if (noCalendarsError) {
      errorMessage.value = t('error.externalAccountHasNoCalendars', { external: 'Google' });

      // Also remove the google calendar
      if (externalConnectionStore.google.length > 0) {
        await externalConnectionStore.disconnect(ExternalConnectionProviders.Google);
      }
    } else {
      errorMessage.value = route.query.error;
    }

    await router.replace(route.path);
  }

  if (localStorage?.getItem(initFlowKey)) {
    localStorage?.removeItem(initFlowKey);

    const { data, error }: BooleanResponse = await call('google/ftue-status').get().json();

    // Did they hit back?
    if (error?.value) {
      errorMessage.value = {
        title: ((data.value as Exception)?.detail as ExceptionDetail)?.message,
        details: null,
      };
      return;
    }

    // We are all good, move to the next step
    await ftueStore.moveToStep(FtueStep.CreateBookingPage);
  }
});
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