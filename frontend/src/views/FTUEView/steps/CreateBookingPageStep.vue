<script setup lang="ts">
import { ref, computed, useTemplateRef, inject, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { PrimaryButton, SelectInput, TextInput, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { useUserStore } from '@/stores/user-store';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useScheduleStore } from '@/stores/schedule-store';
import { SelectOption } from '@/models';
import { FtueStep, DEFAULT_SLOT_DURATION } from '@/definitions';
import { dayjsKey } from '@/keys';

import StepTitle from '../components/StepTitle.vue';

const dj = inject(dayjsKey);

const { t } = useI18n();
const user = useUserStore();
const ftueStore = useFTUEStore();
const calendarStore = useCalendarStore();
const scheduleStore = useScheduleStore();

const { calendars } = storeToRefs(calendarStore);

const bookingPageTitle = ref(scheduleStore.firstSchedule?.name ?? '');
const calendarForNewAppointments = ref(
  scheduleStore.firstSchedule?.calendar_id ?? calendars.value?.[0]?.id ?? 0
);
const isLoading = ref(false);
const errorMessage = ref(null);
const formRef = useTemplateRef('formRef');

const isContinueButtonDisabled = computed(() => !bookingPageTitle.value?.trim() || !calendarForNewAppointments.value || isLoading.value);

const calendarOptions = computed<SelectOption[]>(() => calendars.value.map((calendar) => ({
  label: calendar.title,
  value: calendar.id,
})));

const onBackButtonClick = () => {
  ftueStore.moveToStep(FtueStep.ConnectCalendars, true);
};

const onContinueButtonClick = async () => {
  if (!formRef.value.checkValidity()) {
    return;
  }

  isLoading.value = true;
 
  try {
    // First, we need to connect / activate the selected calendar
    await calendarStore.connectCalendar(calendarForNewAppointments.value);

    const payload = {
      name: bookingPageTitle.value,
      calendar_id: calendarForNewAppointments.value,
      // The API endpoint expects a full schedule object
      // but on this step we only have two fields: name and calendar
      // so we will fill the rest with default values
      start_date: dj().format('YYYY-MM-DD'),
      start_time: '09:00',
      end_time: '17:00',
      slot_duration: DEFAULT_SLOT_DURATION,
      weekdays: [1, 2, 3, 4, 5],
      earliest_booking: 1440,
      farthest_booking: 20160,
      timezone: user.data.settings.timezone,
    };

    const data = await scheduleStore.createSchedule(payload);

    if (Object.prototype.hasOwnProperty.call(data, 'error')) {
      errorMessage.value = (data as unknown as Error)?.message ?? t('error.somethingWentWrong');
      isLoading.value = false;
      return;
    }

    ftueStore.clearMessages();
    await ftueStore.moveToStep(FtueStep.SetAvailability);
  } catch (error) {
    errorMessage.value = error ? error.message : t('error.somethingWentWrong');
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  // Force re-fetch calendars to ensure we have the latest data
  // since we just connected an account on the previous step and data will be outdated
  await calendarStore.fetch(true);
});
</script>

<template>
  <step-title :title="t('ftue.createBookingPage')" />

  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage }}
  </notice-bar>

  <form ref="formRef" @submit.prevent @keyup.enter="onContinueButtonClick">
    <text-input
      name="bookingPageTitle"
      :placeholder="t('ftue.bookingPagePlaceholder')"
      :help="t('ftue.bookingPageTitleHelp')"
      class="booking-page-title-input"
      required
      v-model="bookingPageTitle"
    >
      {{ t('ftue.bookingPageTitle') }}
    </text-input>
  
    <select-input
      name="calendarForNewAppointments"
      :options="calendarOptions"
      :help="t('ftue.calendarForNewAppointmentsHelp')"
      required
      v-model="calendarForNewAppointments"
    >
      {{ t('ftue.calendarForNewAppointments') }}
    </select-input>
  </form>

  <div class="buttons-container">
    <primary-button variant="outline" :title="t('label.back')" @click="onBackButtonClick">
      {{ t('label.back') }}
    </primary-button>
    <primary-button :title="t('label.continue')" @click="onContinueButtonClick" :disabled="isContinueButtonDisabled">
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
.booking-page-title-input {
  margin-block-end: 2.25rem;
}

.notice-bar {
  margin-block-end: 1.5rem;
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 10.30rem;

  button {
    min-width: 123px;
  }

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>