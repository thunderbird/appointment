<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import {
  onMounted, inject, ref,
} from 'vue';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';
import { useRoute, useRouter } from 'vue-router';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { callKey } from '@/keys';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const call = inject(callKey);

const isLoading = ref(false);

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep, errorMessage,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;

const calendarStore = useCalendarStore();
const externalConnectionStore = useExternalConnectionsStore();
const { calendars } = storeToRefs(calendarStore);
const initFlowKey = 'tba/startedCalConnect';

onMounted(async () => {
  await calendarStore.fetch(call, true);
  const hasFlowKey = localStorage?.getItem(initFlowKey);
  const noCalendarsError = hasFlowKey && calendars.value.length === 0;

  // Error occurred during flow
  if (route.query.error || noCalendarsError) {
    localStorage?.removeItem(initFlowKey);
    if (noCalendarsError) {
      errorMessage.value = t('error.externalAccountHasNoCalendars', { external: 'Google' });

      // Also remove the google calendar
      if (externalConnectionStore.google.length > 0) await externalConnectionStore.disconnect(call, 'google');
    } else {
      errorMessage.value = route.query.error;
    }
    await router.replace(route.path);
  }

  if (localStorage?.getItem(initFlowKey)) {
    localStorage?.removeItem(initFlowKey);

    const { data, error } = await call('google/ftue-status').get().json();
    // Did they hit back?
    if (error?.value) {
      errorMessage.value = data.value?.detail?.message;
      return;
    }

    await nextStep();
  }
});

const onSubmit = async () => {
  const user = useUserStore();

  isLoading.value = true;

  // Create key so we can move to the next page after we come back
  localStorage?.setItem(initFlowKey, 'true');
  await calendarStore.connectGoogleCalendar(call, user.data.email);
};

</script>
<template>
  <div class="content">
    <div class="card">
      <p class="">{{ t('text.googlePermissionDisclaimer') }}</p>
      <ul class="">
        <li>
          <strong>
            {{ t('text.googlePermissionEventsName') }}
          </strong> - {{ t('text.googlePermissionEventReason') }}
        </li>
        <li>
          <strong>
            {{ t('text.googlePermissionCalendarName') }}
          </strong> - {{ t('text.googlePermissionCalendarReason') }}
        </li>
      </ul>
      <i18n-t
        :keypath="`text.settings.connectedAccounts.connect.googleLegal.text`"
        tag="label"
        :for="`text.settings.connectedAccounts.connect.googleLegal.link`"
      >
        <a
          class="underline"
          href="https://developers.google.com/terms/api-services-user-data-policy"
          target="_blank"
        >
          {{ t(`text.settings.connectedAccounts.connect.googleLegal.link`) }}
        </a>
      </i18n-t>
    </div>
  </div>
  <div class="buttons">
    <secondary-button
      class="btn-back"
      :title="t('label.back')"
      v-if="hasPreviousStep"
      :disabled="isLoading"
      @click="previousStep()"
    >{{ t('label.back') }}
    </secondary-button>
    <secondary-button
      class="btn-continue"
      :title="t('label.connectGoogleCalendar')"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading"
    >
      <template v-slot:icon><span :title="t('ftue.googleCalendarLogo')" class="google-calendar-logo"/></template>
      {{ t('label.connectGoogleCalendar') }}
    </secondary-button>
  </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.content {
  display: flex;
  margin: auto;
}

.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  padding: 1rem;
  border-radius: 0.5625rem;
  background-color: color-mix(in srgb, var(--neutral) 65%, transparent);
  border: 0.0625rem solid color-mix(in srgb, var(--neutral) 65%, transparent);
  font-size: 0.8125rem;
  margin: auto;
}

.google-calendar-logo {
  display: inline-block;
  background-image: url('@/assets/svg/google-calendar-logo.svg');
  width: 1.625rem;
  height: 1.625rem;
}

.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (--md) {
  .card {
    width: 70%;
  }

  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
