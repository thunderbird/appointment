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
  <div class="absolute bottom-[5.75rem] flex w-full justify-end gap-4">
    <secondary-button
      class="btn-back"
      title="Back"
      v-if="hasPreviousStep"
      :disabled="isLoading"
      @click="previousStep()"
    >Back
    </secondary-button>
    <secondary-button
      class="btn-continue"
      title="Connect Google Calendar"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading"
    >
      <template v-slot:icon><span title="Google Calendar Logo" class="google-calendar-logo"/></template>
      Connect Google Calendar
    </secondary-button>
  </div>
</template>

<script setup>
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

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const call = inject('call');

const isLoading = ref(false);

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep, errorMessage,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;

const calendarStore = useCalendarStore();
const { calendars } = storeToRefs(calendarStore);
const initFlowKey = 'tba/startedCalConnect';

onMounted(async () => {
  await calendarStore.fetch(call);
  const hasFlowKey = localStorage?.getItem(initFlowKey);

  // Error occurred during flow
  if (route.query.error || (hasFlowKey && calendars.value.length === 0)) {
    localStorage?.removeItem(initFlowKey);
    errorMessage.value = route.query.error;
    await router.replace(route.path);
  }

  if (localStorage?.getItem(initFlowKey)) {
    localStorage?.removeItem(initFlowKey);
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
<style scoped>

.content {
  display: flex;
  height: 24rem;
  margin: auto;
}

.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 70%;
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
</style>
