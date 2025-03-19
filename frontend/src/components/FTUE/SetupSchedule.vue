<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import TextInput from '@/tbpro/elements/TextInput.vue';
import SelectInput from '@/tbpro/elements/SelectInput.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import BubbleSelect from '@/tbpro/elements/BubbleSelect.vue';
import { DateFormatStrings, DEFAULT_SLOT_DURATION, SLOT_DURATION_OPTIONS } from '@/definitions';
import { createFTUEStore } from '@/stores/ftue-store';
import { useUserStore } from '@/stores/user-store';
import { createCalendarStore } from '@/stores/calendar-store';
import { createScheduleStore } from '@/stores/schedule-store';
import {
  dayjsKey, callKey, isoWeekdaysKey,
} from '@/keys';
import { Error, SelectOption } from '@/models';

const { t } = useI18n();
const dj = inject(dayjsKey);
const call = inject(callKey);
const isoWeekdays = inject(isoWeekdaysKey);

const ftueStore = createFTUEStore(call);
const {
  hasNextStep, hasPreviousStep,
} = storeToRefs(ftueStore);
const { errorMessage, infoMessage } = storeToRefs(ftueStore);
const user = useUserStore();
const calendarStore = createCalendarStore(call);
const scheduleStore = createScheduleStore(call);
const { connectedCalendars } = storeToRefs(calendarStore);
const { schedules } = storeToRefs(scheduleStore);
const { timeToBackendTime, timeToFrontendTime } = scheduleStore;

const calendarOptions = computed<SelectOption[]>(() => connectedCalendars.value.map((calendar) => ({
  label: calendar.title,
  value: calendar.id,
})));
const durationOptions: SelectOption[] = SLOT_DURATION_OPTIONS.map((min) => ({
  label: `${min} min`,
  value: min,
}));
const scheduleDayOptions: SelectOption[] = isoWeekdays.map((day) => ({
  label: day.min[0],
  value: day.iso,
}));

const formRef = ref<HTMLFormElement>();

const schedule = ref({
  name: `${user.data.name}'s Availability`,
  calendar: 0,
  startTime: '09:00',
  endTime: '17:00',
  duration: DEFAULT_SLOT_DURATION,
  days: [1, 2, 3, 4, 5],
  details: '',
});

const duration = computed(() => `${schedule.value.duration} minute`);
const isLoading = ref(false);

// Form validation
const errorScheduleName = ref<string>(null);

const onSubmit = async () => {
  isLoading.value = true;
  errorMessage.value = null;
  errorScheduleName.value = null;

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
    start_date: dj().format(DateFormatStrings.QalendarFullDay),
    details: schedule.value?.details ?? '',
    timezone: user.data.settings.timezone,
  };

  const data = schedules.value.length > 0
    ? await scheduleStore.updateSchedule(schedules.value[0].id, scheduleData)
    : await scheduleStore.createSchedule(scheduleData);

  if ((data as Error)?.error) {
    errorMessage.value = {
      title: (data as Error)?.message,
      details: null,
    };
    isLoading.value = false;
    return;
  }

  await ftueStore.nextStep();
};

onMounted(async () => {
  isLoading.value = true;
  infoMessage.value = {
    title: t('ftue.setupScheduleInfo'),
    details: null,
  };

  await Promise.all([
    calendarStore.fetch(true),
    scheduleStore.fetch(true),
  ]);

  schedule.value.calendar = connectedCalendars.value[0].id;

  if (schedules?.value && schedules.value[0]) {
    const dbSchedule = schedules.value[0];
    schedule.value = {
      ...schedule.value,
      name: dbSchedule.name,
      calendar: dbSchedule.calendar_id,
      startTime: timeToFrontendTime(dbSchedule.start_time, dbSchedule.time_updated),
      endTime: timeToFrontendTime(dbSchedule.end_time, dbSchedule.time_updated),
      duration: dbSchedule.slot_duration,
      days: dbSchedule.weekdays,
    };
  }

  isLoading.value = false;
});

</script>

<template>
  <div class="content">
    <form ref="formRef" autocomplete="off" autofocus @submit.prevent @keyup.enter="onSubmit">
      <div class="column">
        <text-input name="scheduleName" v-model="schedule.name" required :error="errorScheduleName">
          {{ t('ftue.scheduleName') }}
        </text-input>
        <div class="pair">
        <text-input type="time" name="startTime" v-model="schedule.startTime" required>
          {{ t('label.startTime') }}
        </text-input>
        <text-input type="time" name="endTime" v-model="schedule.endTime" required>
          {{ t('label.endTime') }}
        </text-input>
        </div>
        <bubble-select class="bubbleSelect" :options="scheduleDayOptions" v-model="schedule.days" :required="true">
          {{ t('label.availableDays') }}
        </bubble-select>
      </div>
      <div class="column">
        <select-input name="calendar" v-model="schedule.calendar" :options="calendarOptions" required>
          {{ t('label.selectCalendar') }}
        </select-input>
        <select-input name="duration" v-model="schedule.duration" :options="durationOptions" required>
          {{ t('label.slotLength') }}
        </select-input>
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
      @click="ftueStore.previousStep()"
    >
      {{ t('label.back') }}
    </secondary-button>
    <primary-button
      class="btn-continue"
      :title="t('label.continue')"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading"
    >
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';
@import '@/assets/styles/mixins.pcss';

form {
  --colour-background: var(--colour-neutral-base);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 0.5625rem;
  @mixin faded-background var(--colour-background);
  width: 100%;
  height: 100%;
  padding: 1rem;
}

.dark {
  .card {
    --colour-background: var(--colour-neutral-lower);
  }
}

.bubbleSelect {
  overflow-x: auto;
  padding-top: 1rem;
  padding-bottom: 1rem;
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
  --colour-background: var(--colour-neutral-raised);
  padding: 1rem;
  border-radius: 0.3565625rem;
  border: 0.0625rem solid var(--colour-neutral-border);
  background-color: var(--colour-background);
  font-size: 0.6875rem;
  line-height: 163%;
  font-weight: 400;
}

.dark {
  .scheduleInfo {
    --colour-background: var(--colour-neutral-lower);
  }
}

.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (--md) {
  .bubbleSelect {
    padding: 0;
  }
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
