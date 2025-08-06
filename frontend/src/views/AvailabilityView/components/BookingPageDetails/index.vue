<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { MeetingLinkProviderType, SLOT_DURATION_OPTIONS } from '@/definitions';
import { SelectOption } from '@/models';
import { useAvailabilityStore } from '@/stores/availability-store';
import { CheckboxInput, TextArea, TextInput } from '@thunderbirdops/services-ui';
import RadioGroupPill from '../RadioGroupPill.vue';

const { t } = useI18n();

const availabilityStore = useAvailabilityStore();
const { currentState, hasZoom } = storeToRefs(availabilityStore);

const pageName = computed({
  get: () => currentState.value.name?.toString(),
  set: (value) => {
    availabilityStore.$patch({ currentState: { name: value } })
  }
})

const pageDescription = computed({
  get: () => currentState.value.details?.toString(),
  set: (value) => {
    availabilityStore.$patch({ currentState: { details: value } })
  }
})

const autoGenerateZoomLink = computed({
  get: () => currentState.value.meeting_link_provider === MeetingLinkProviderType.Zoom,
  set: (value) => {
    availabilityStore.$patch({
      currentState: {
        meeting_link_provider: value ? MeetingLinkProviderType.Zoom : MeetingLinkProviderType.None
      }
    })
  }
})

const virtualMeetingLink = computed({
  get: () => currentState.value.location_url?.toString(),
  set: (value) => {
    availabilityStore.$patch({ currentState: { location_url: value } })
  }
})

const meetingDuration = computed({
  get: () => currentState.value.slot_duration?.toString(),
  set: (value) => {
    availabilityStore.$patch({ currentState: { slot_duration: parseInt(value, 10) } })
  }
})

// Appointment duration options
const durationOptions: SelectOption<string>[] = SLOT_DURATION_OPTIONS.map((duration) => ({
  label: t('units.minutesShort', { value: duration }),
  value: duration.toString(),
}));
</script>

<script lang="ts">
export default {
  name: 'BookingPageDetails'
}
</script>

<template>
  <header>
    <h2>{{ t('label.bookingPageDetails') }}</h2>
  </header>

  <div class="fields-container">
    <!-- Page name -->
    <text-input
      type="text"
      name="pageName"
      v-model="pageName"
      required
    >
      {{ t('label.pageName') }}:
    </text-input>

    <!-- Page description -->
    <text-area
      name="pageDescription"
      :placeholder="t('label.enterDescriptionToSchedulingPage')"
      v-model="pageDescription"
    >
      {{ t('label.pageDescription') }}:
    </text-area>

    <!-- Auto generate Zoom link in invites -->
    <div class="auto-generate-link-container">
      <checkbox-input
        name="autoGenerateZoomLink"
        :label="t('label.autogenerateZoomLinks')"
        v-model="autoGenerateZoomLink"
        :disabled="!hasZoom"
      />
      <i18n-t v-if="!hasZoom" keypath="text.generateZoomMeetingHelpDisabled.text" tag="span" scope="global" class="zoom-helper-span">
        <template v-slot:link>
          <router-link class="underline" to="settings/connectedAccounts">
            {{ t('text.generateZoomMeetingHelpDisabled.link') }}
          </router-link>
        </template>
      </i18n-t>
    </div>

    <text-input
      type="text"
      name="virtualMeetingLink"
      v-model="virtualMeetingLink"
      placeholder="https://meet.jit.si/room"
    >
      {{ t('label.virtualMeetingLink') }}:
    </text-input>

    <!-- TBD -->
    <!-- <text-input
      type="text"
      name="virtualMeetingDetails"
    >
      {{ t('label.virtualMeetingDetails') }}:
    </text-input> -->

    <radio-group-pill
      v-model="meetingDuration"
      name="meetingDuration"
      :legend="t('label.meetingDuration')"
      :options="durationOptions"
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

.auto-generate-link-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  .zoom-helper-span {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}
</style>