<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { SLOT_DURATION_OPTIONS } from '@/definitions';
import { SelectOption } from '@/models';
import { CheckboxInput, TextArea, TextInput } from '@thunderbirdops/services-ui';
import RadioGroupPill from '../RadioGroupPill.vue';

const { t } = useI18n();
const autoGenerateZoomLink = ref();
const meetingDuration = ref("15_min");

// Appointment duration options
const durationOptions: SelectOption[] = SLOT_DURATION_OPTIONS.map((duration) => ({
  label: t('units.minutes', { value: duration }),
  value: duration,
}));
</script>

<script lang="ts">
export default {
  name: 'BookingPageDetails'
}
</script>

<template>
  <header>
    <h2>Booking Page Details</h2>
  </header>

  <div class="fields-container">
    <!-- Page name -->
    <div>
      <h3>{{ t('label.pageName') }}:</h3>
      <p>General Availability</p>
    </div>

    <!-- Page description -->
    <text-area
      name="pageDescription"
      :placeholder="t('label.enterDescriptionToSchedulingPage')"
    >
      {{ t('label.pageDescription') }}:
    </text-area>

    <!-- Auto generate Zoom link in invites -->
     <checkbox-input
      name="autoGenerateZoomLink"
      :label="t('label.autogenerateZoomLinks')"
      v-model="autoGenerateZoomLink"
    />

    <text-input
      type="text"
      name="virtualMeetingLink"
    >
      {{ t('label.virtualMeetingLink') }}:
    </text-input>

    <text-input
      type="text"
      name="virtualMeetingDetails"
    >
      {{ t('label.virtualMeetingDetails') }}:
    </text-input>

    <radio-group-pill
      v-model="meetingDuration"
      name="meetingDuration"
      :legend="t('label.meetingDuration')"
      :options="[
        { label: '15 Min', value: '15_min' },
        { label: '30 Min', value: '30_min' },
        { label: '60 Min', value: '60_min' },
        { label: '75 Min', value: '75_min' },
        { label: '90 Min', value: '90_min' },
      ]"
    />
  </div>
</template>

<style scoped>
header {
  margin-block-end: 2rem;
}

h2 {
  font-size: 1.5rem;
}

h3 {
  font-size: 0.8125rem;
  font-weight: bold;
}

.fields-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>