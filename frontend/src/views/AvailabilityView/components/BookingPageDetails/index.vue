<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { MeetingLinkProviderType, SLOT_DURATION_OPTIONS } from '@/definitions';
import { SelectOption } from '@/models';
import { useAvailabilityStore } from '@/stores/availability-store';
import { CheckboxInput, TextArea, TextInput, SegmentedControl } from '@thunderbirdops/services-ui';

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

const MAX_DESCRIPTION_LENGTH = 250;
const pageDescriptionHelpLabel = computed(() => `${pageDescription.value?.length.toString() ?? 0}/${MAX_DESCRIPTION_LENGTH}`)

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
    <p>{{ t('label.chooseWhatVisitorsSeeOnYourBookingPage') }}</p>
  </header>

  <div class="fields-container">
    <!-- Page name -->
    <text-input
      class="page-name-input"
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
      class="page-description"
      v-model="pageDescription"
      :placeholder="t('label.enterDescriptionToSchedulingPage')"
      :max-length="MAX_DESCRIPTION_LENGTH"
      :help="pageDescriptionHelpLabel"
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
      class="virtual-meeting-link-input"
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

    <segmented-control
      v-model="meetingDuration"
      name="meetingDuration"
      required
      :legend="t('label.meetingDuration')"
      :options="durationOptions"
    >
      {{ t('label.meetingDuration') }}
    </segmented-control>
  </div>
</template>

<style scoped>
header {
  margin-block-end: 2.25rem;

  h2 {
    font-family: metropolis;
    font-size: 1.5rem;
    color: var(--colour-ti-highlight);
  }

  p {
    color: var(--colour-ti-muted);
  }
}

h3 {
  font-size: 0.8125rem;
  font-weight: bold;
}

.fields-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 768px;
  color: var(--colour-ti-secondary);

  .page-description {
    /* Help text (character count) */
    & :last-child {
      justify-content: end;
    }
  }

  .page-name-input {
    max-width: 364px;
    width: 100%;
  }

  .virtual-meeting-link-input {
    max-width: 389px;
    width: 100%;
  }
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