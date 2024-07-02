<template>
  <div class="content">
    <form ref="formRef" autocomplete="off" autofocus @submit.prevent @keyup.enter="onSubmit">
      <div class="column">
        <text-input name="scheduleName" v-model="schedule.name" required>{{ t('ftue.scheduleName') }}</text-input>
        <div class="pair">
        <text-input type="time" name="startTime" v-model="schedule.startTime" required>{{ t('label.startTime') }}</text-input>
        <text-input type="time" name="endTime" v-model="schedule.endTime" required>{{ t('label.endTime') }}</text-input>
        </div>
        <bubble-select class="bubbleSelect" :options="scheduleDayOptions" v-model="schedule.days" />
      </div>
      <div class="column">
        <select-input name="calendar" v-model="schedule.calendar" :options="calendarOptions" required>{{ t('label.selectCalendar') }}</select-input>
        <select-input name="duration" v-model="schedule.duration" :options="durationOptions" required>{{ t('label.slotLength') }}</select-input>
        <div class="scheduleInfo">{{
            t('text.recipientsCanScheduleBetween', {
              duration: duration,
              earliest: '24 hours',
              farthest: '2 weeks',
            })
          }}
        </div>
      </div>
    </form>
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
    <primary-button
      class="btn-continue"
      :title="t('label.continue')"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading"
    >{{ t('label.continue') }}
    </primary-button>
  </div>
</template>
<script setup>

import TextInput from '@/tbpro/elements/TextInput.vue';
import SelectInput from '@/tbpro/elements/SelectInput.vue';
import {
  computed,
  inject, onMounted, ref,
} from 'vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import { storeToRefs } from 'pinia';
import { useFTUEStore } from '@/stores/ftue-store';
import { useUserStore } from '@/stores/user-store.ts';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import { dateFormatStrings, defaultSlotDuration } from '@/definitions';
import { useI18n } from 'vue-i18n';
import { useCalendarStore } from '@/stores/calendar-store.ts';
import BubbleSelect from '@/elements/BubbleSelect.vue';
import { useScheduleStore } from '@/stores/schedule-store.ts';

const { t } = useI18n();
const dj = inject('dayjs');
const call = inject('call');
const isoWeekdays = inject('isoWeekdays');

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep,
} = storeToRefs(ftueStore);
const { nextStep, previousStep } = ftueStore;
const { errorMessage, infoMessage } = storeToRefs(ftueStore);
const user = useUserStore();
const calendarStore = useCalendarStore();
const scheduleStore = useScheduleStore();
const { connectedCalendars } = storeToRefs(calendarStore);
const { schedules } = storeToRefs(scheduleStore);
const { timeToBackendTime, timeToFrontendTime } = scheduleStore;

const calendarOptions = computed(() => connectedCalendars.value.map((calendar) => ({
  label: calendar.title,
  value: calendar.id,
})));
const durationOptions = [15, 30, 45, 60, 75, 90].map((min) => ({
  label: `${min} min`,
  value: min,
}));
const scheduleDayOptions = isoWeekdays.map((day) => ({
  label: day.min[0],
  value: day.iso,
}));
/**
 * @type {Ref<HTMLFormElement>}
 */
const formRef = ref();

const schedule = ref({
  name: `${user.data.name}'s Availability`,
  calendar: 0,
  startTime: '09:00',
  endTime: '17:00',
  duration: defaultSlotDuration,
  days: [1, 2, 3, 4, 5],
  details: '',
});

const duration = computed(() => `${schedule.value.duration} minute`);
const isLoading = ref(false);

const onSubmit = async () => {
  isLoading.value = true;

  errorMessage.value = null;

  if (!formRef.value.checkValidity()) {
    isLoading.value = false;
    return;
  }

  const scheduleData = {
    ...schedules?.value[0] ?? {},
    active: true,
    name: schedule.value.name,
    calendar_id: schedule.value.calendar,
    start_time: timeToBackendTime(schedule.value.startTime),
    end_time: timeToBackendTime(schedule.value.endTime),
    slot_duration: schedule.value.duration,
    weekdays: schedule.value.days,
    earliest_booking: 1440,
    farthest_booking: 20160,
    start_date: dj().format(dateFormatStrings.qalendarFullDay),
    details: schedule.value?.details ?? '',
  };

  const data = schedules.value.length > 0
    ? await scheduleStore.updateSchedule(call, schedules.value[0].id, scheduleData)
    : await scheduleStore.createSchedule(call, scheduleData);

  if (data?.error) {
    errorMessage.value = data?.message;
    isLoading.value = false;
    return;
  }

  await nextStep();
};

onMounted(async () => {
  isLoading.value = true;
  infoMessage.value = t('ftue.setupScheduleInfo');

  await Promise.all([
    calendarStore.fetch(call, true),
    scheduleStore.fetch(call, true),
  ]);

  schedule.value.calendar = connectedCalendars.value[0].id;

  if (schedules?.value && schedules.value[0]) {
    const dbSchedule = schedules.value[0];
    schedule.value = {
      ...schedule.value,
      name: dbSchedule.name,
      calendar: dbSchedule.calendar_id,
      startTime: timeToFrontendTime(dbSchedule.start_time),
      endTime: timeToFrontendTime(dbSchedule.end_time),
      duration: dbSchedule.slot_duration,
      days: dbSchedule.weekdays,
    };
  }

  isLoading.value = false;
});

</script>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 0.5625rem;
  background-color: color-mix(in srgb, var(--surface-base) 65%, transparent);
  width: 100%;
  height: 100%;
  padding: 1rem;
}

.bubbleSelect {
  overflow-x: scroll;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 3.125rem;
  width: 100%;
  justify-content: center;
  align-items: center;
  font-family: 'Inter', 'sans-serif';
}

.scheduleInfo {
  padding: 1rem;
  border-radius: 0.3565625rem;
  border: 0.0625rem solid var(--surface-border);
  background-color: var(--surface-raised);
  font-size: 0.6875rem;
  line-height: 163%;
  font-weight: 400;
}
.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (--md) {
  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
  form {
    flex-direction: row;
    width: 40.0rem;
    height: 18rem
  }
  .column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 50%;
  }
  .pair {
    display: flex;
    gap: 2rem;
  }
}
</style>
