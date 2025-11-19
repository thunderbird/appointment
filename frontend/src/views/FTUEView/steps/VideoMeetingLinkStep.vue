<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { TextInput, PrimaryButton, LinkButton } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import zoomLogo from '@/assets/images/zoom-icon.png';

import StepTitle from '../components/StepTitle.vue';
import ProviderCardButton from '../components/ProviderCardButton.vue';

const { t } = useI18n();
const ftueStore = useFTUEStore();
</script>

<template>
  <step-title :title="t('ftue.videoMeetingLink')" />

  <div class="video-meeting-link-container">
    <provider-card-button
      :title="t('ftue.connectWithZoom')"
      :description="t('ftue.connectWithZoomInfo')"
      :iconSrc="zoomLogo"
      :iconAlt="t('ftue.zoomIcon')"
    />
  </div>

  <h3>{{ t('ftue.customVideoMeetingLink') }}</h3>
  <p>{{ t('ftue.customVideoMeetingLinkInfo') }}</p>

  <text-input
    name="customVideoMeetingLink"
    :placeholder="t('ftue.customVideoMeetingLinkPlaceholder')"
  />

  <div class="buttons-container">
    <link-button :title="t('label.cancel')" @click="ftueStore.previousStep()">
      {{ t('label.cancel') }}
    </link-button>
    <link-button :title="t('ftue.skipThisStep')">
      {{ t('ftue.skipThisStep') }}
    </link-button>
    <primary-button :title="t('label.continue')" @click="ftueStore.nextStep()">
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-block-end: 1rem;
  color: black;
}

p {
  margin-block-end: 1rem;
}

.video-meeting-link-container {
  margin-block-end: 2.25rem;
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 5.8125rem;

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
    text-transform: lowercase;
    padding-inline: 0.5rem;
  }
}
</style>