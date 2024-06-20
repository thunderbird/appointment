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
import { useUserStore } from '@/stores/user-store';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import SyncCard from '@/tbpro/elements/SyncCard.vue';
import InfoBar from '@/elements/InfoBar.vue';
import { defaultSlotDuration } from '@/definitions.js';
import { useI18n } from 'vue-i18n';
import { useCalendarStore } from '@/stores/calendar-store.js';
import BubbleSelect from '@/elements/BubbleSelect.vue';

const { t } = useI18n();
const call = inject('call');
const dj = inject('dayjs');
const isoWeekdays = inject('isoWeekdays');

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep,
} = storeToRefs(ftueStore);
const { nextStep, previousStep } = ftueStore;
const user = useUserStore();
const calendarStore = useCalendarStore();
const { connectedCalendars } = storeToRefs(calendarStore);

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

const scheduleName = ref(`${user.data.name}'s Availability`);
const calendar = ref({});
const startTime = ref('09:00');
const endTime = ref('17:00');
const bookingDuration = ref(defaultSlotDuration);
const scheduleDays = ref([1, 2, 3, 4, 5]);

const duration = computed(() => `${bookingDuration.value} minute`);
const isLoading = ref(false);

const onSubmit = async () => {
  if (!formRef.value.checkValidity()) {
    console.log('Nope!');
  }

  // await nextStep();
};

onMounted(async () => {
  await calendarStore.fetch(call);
  calendar.value = connectedCalendars.value[0].id;
});

</script>

<template>
  <div class="content">
    <InfoBar>
      You can edit this schedule later
    </InfoBar>
    <form ref="formRef" autocomplete="off" autofocus>
      <div class="column">
        <text-input name="scheduleName" v-model="scheduleName" required>Schedule's Name</text-input>
        <div class="pair">
        <text-input type="time" name="startTime" v-model="startTime" required>Start Time</text-input>
        <text-input type="time" name="endTime" v-model="endTime" required>End Time</text-input>
        </div>
        <bubble-select :options="scheduleDayOptions" />
      </div>
      <div class="column">
        <select-input name="calendar" v-model="calendar" :options="calendarOptions" required>Select Calendar</select-input>
        <select-input name="duration" v-model="bookingDuration" :options="durationOptions" required>Booking Duration</select-input>
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
  <div class="absolute bottom-[5.75rem] flex w-full justify-end gap-4">
    <secondary-button
      class="btn-back"
      title="Back"
      v-if="hasPreviousStep"
      :disabled="isLoading"
      @click="previousStep()"
    >Back
    </secondary-button>
    <primary-button
      class="btn-continue"
      title="Continue"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading"
    >Continue</primary-button>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

form {
  gap: 1rem;
  border-radius: 0.5625rem;
  background-color: color-mix(in srgb, var(--surface-base) 65%, transparent);
  width: 100%;
  height: 100%;
  padding: 1rem;
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

@media (--md) {
  form {
    display: flex;
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
