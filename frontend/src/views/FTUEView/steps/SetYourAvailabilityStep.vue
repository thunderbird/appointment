<script setup lang="ts">
import { ref, inject, useTemplateRef, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { BubbleSelect, PrimaryButton, SelectInput, TextInput, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import { useScheduleStore } from '@/stores/schedule-store';
import { isoWeekdaysKey } from '@/keys';
import { SelectOption } from '@/models';
import { FtueStep, DEFAULT_SLOT_DURATION, SLOT_DURATION_OPTIONS } from '@/definitions';

import StepTitle from '../components/StepTitle.vue';

const isoWeekdays = inject(isoWeekdaysKey);

const { t } = useI18n();
const ftueStore = useFTUEStore();
const scheduleStore = useScheduleStore();
const { timeToFrontendTime, timeToBackendTime } = scheduleStore;

const startTime = ref(scheduleStore.firstSchedule
  ? timeToFrontendTime(scheduleStore.firstSchedule?.start_time, scheduleStore.firstSchedule?.time_updated)
  : '09:00');

const endTime = ref(scheduleStore.firstSchedule
  ? timeToFrontendTime(scheduleStore.firstSchedule?.end_time, scheduleStore.firstSchedule?.time_updated)
  : '17:00');

const duration = ref(scheduleStore.firstSchedule?.slot_duration ?? DEFAULT_SLOT_DURATION);
const weekdays = ref(scheduleStore.firstSchedule?.weekdays ?? [1, 2, 3, 4, 5]);
const isLoading = ref(false);
const errorMessage = ref(null);
const formRef = useTemplateRef('formRef');

const isContinueButtonDisabled = computed(() => !weekdays.value.length || !startTime.value || !endTime.value || !duration.value || isLoading.value);

const scheduleDayOptions: SelectOption[] = isoWeekdays.map((day) => ({
  label: day.min[0],
  value: day.iso,
}));

const bookingDurationOptions: SelectOption<string>[] = SLOT_DURATION_OPTIONS.map((duration) => ({
  label: t('units.minutesShort', { value: duration }),
  value: duration.toString(),
}));

const onBackButtonClick = () => {
  ftueStore.moveToStep(FtueStep.CreateBookingPage, true);
};

const onContinueButtonClick = async () => {
  if (!formRef.value.checkValidity()) {
    return;
  }

  isLoading.value = true;
  errorMessage.value = null;

  try {
    const data = await scheduleStore.updateSchedule(scheduleStore.firstSchedule.id, {
      ...scheduleStore.firstSchedule,
      start_time: timeToBackendTime(startTime.value),
      end_time: timeToBackendTime(endTime.value),
      slot_duration: duration.value,
      weekdays: weekdays.value,
    });

    if (Object.prototype.hasOwnProperty.call(data, 'error')) {
      errorMessage.value = (data as unknown as Error)?.message ?? t('error.somethingWentWrong');
      return;
    }

    ftueStore.clearMessages();
    await ftueStore.moveToStep(FtueStep.VideoMeetingLink);
  } catch (error) {
    errorMessage.value = error ? error.message : t('error.somethingWentWrong');
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <step-title :title="t('ftue.setYourAvailability')" />

  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage }}
  </notice-bar>

  <form ref="formRef" @submit.prevent @keyup.enter="onContinueButtonClick" class="availability-container">
    <bubble-select
      name="selectDays"
      :options="scheduleDayOptions"
      required
      v-model="weekdays"
    >
      {{ t('ftue.selectDays') }}
    </bubble-select>
  
    <div class="time-container">
      <text-input type="time" name="startTime" required class="time-input" v-model="startTime">
        {{ t('ftue.startTime') }}
      </text-input>
      <text-input type="time" name="endTime" required class="time-input" v-model="endTime">
        {{ t('ftue.endTime') }}
      </text-input>
    </div>
  
    <select-input
      name="bookingDuration"
      :options="bookingDurationOptions"
      required
      v-model="duration"
    >
      {{ t('ftue.bookingDuration') }}
    </select-input>
  </form>

  <div class="buttons-container">
    <primary-button variant="outline" :title="t('label.back')" @click="onBackButtonClick">
      {{ t('label.back') }}
    </primary-button>
    <primary-button :title="t('label.continue')" @click="onContinueButtonClick()" :disabled="isContinueButtonDisabled">
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
.notice-bar {
  margin-block-end: 1.5rem;
}

.availability-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .time-container {
    display: flex;
    gap: 1.5rem;

    .time-input {
      width: 100%;
    }
  }
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 7.75rem;

  button {
    min-width: 123px;
  }

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>
