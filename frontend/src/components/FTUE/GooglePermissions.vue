<template>
  <div class="flex w-full flex-col gap-4">
  <p class="mb-2 text-lg">{{ t('text.googlePermissionDisclaimer') }}</p>
  <ul class="text-md mx-8 list-disc">
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
  <div class="absolute bottom-[5.75rem] flex w-full justify-end gap-4">
    <secondary-button
      class="btn-back"
      title="Back"
      v-if="hasPreviousStep"
      @click="previousStep()"
    >Back</secondary-button>
    <secondary-button
      class="btn-continue"
      title="Connect Google Calendar"
      v-if="hasNextStep"
      @click="onSubmit()"
      >
      <template v-slot:icon><span title="Google Calendar Logo" class="google-calendar-logo"/></template>
      Connect Google Calendar
    </secondary-button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import { defineEmits, onMounted, inject } from 'vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store.js';
import { storeToRefs } from 'pinia';

const { t } = useI18n();
const call = inject('fetch');

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;

const onSubmit = () => {
  const calendarStore = useCalendarStore();
  const user = useUserStore();

  calendarStore.connectGoogleCalendar(call, user.data.email);
};

</script>
<style scoped>
.google-calendar-logo {
  display: inline-block;
  background-image: url('@/assets/svg/google-calendar-logo.svg');
  width: 1.625rem;
  height: 1.625rem;
}
</style>
