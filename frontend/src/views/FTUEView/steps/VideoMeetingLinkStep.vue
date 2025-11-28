<script setup lang="ts">
import { ref, inject, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { TextInput, PrimaryButton, LinkButton, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';
import { useScheduleStore } from '@/stores/schedule-store';
import zoomLogo from '@/assets/images/zoom-icon.png';
import { FtueStep } from '@/definitions';
import { callKey } from '@/keys';
import { AuthUrlResponse, AuthUrl, BooleanResponse, Exception, ExceptionDetail } from '@/models';

import StepTitle from '../components/StepTitle.vue';
import ProviderCardButton from '../components/ProviderCardButton.vue';

const initFlowKey = 'tba/startedMeetingConnect';

const call = inject(callKey);

const { t } = useI18n();
const ftueStore = useFTUEStore();
const scheduleStore = useScheduleStore();

const customMeetingLink = ref(scheduleStore.firstSchedule?.location_url ?? '');
const isLoading = ref(false);
const errorMessage = ref(null);

const isContinueButtonDisabled = computed(() => !customMeetingLink.value?.trim() || isLoading.value);

const onZoomButtonClick = async () => {
  localStorage?.setItem(initFlowKey, 'true');
  isLoading.value = true;
  const { data }: AuthUrlResponse = await call('zoom/auth').get().json();

  // Ship them to the auth link
  window.location.href = (data.value as AuthUrl).url;
};

const onBackButtonClick = () => {
  ftueStore.moveToStep(FtueStep.SetAvailability, true);
};

const onContinueButtonClick = async () => {
  isLoading.value = true;

  try {
    const data = await scheduleStore.updateSchedule(scheduleStore.firstSchedule.id, {
      ...scheduleStore.firstSchedule,
      location_url: customMeetingLink.value,
    });

    if (Object.prototype.hasOwnProperty.call(data, 'error')) {
      errorMessage.value = (data as unknown as Error)?.message ?? t('error.somethingWentWrong');
      return;
    }

    ftueStore.clearMessages();
    await ftueStore.moveToStep(FtueStep.SetupComplete);
  } catch (error) {
    errorMessage.value = error ? error.message : t('error.somethingWentWrong');
  } finally {
    isLoading.value = false;
  }
}

const onSkipButtonClick = async () => {
  ftueStore.clearMessages();
  await ftueStore.moveToStep(FtueStep.SetupComplete);
};

onMounted(async () => {
  const isBackFromConnectFlow = localStorage?.getItem(initFlowKey);
  localStorage?.removeItem(initFlowKey);

  if (isBackFromConnectFlow) {
    const { data, error }: BooleanResponse = await call('zoom/ftue-status').get().json();

    // Did they hit back?
    if (error?.value) {
      errorMessage.value = ((data.value as Exception)?.detail as ExceptionDetail)?.message;
      return;
    }

    ftueStore.clearMessages();
    await ftueStore.moveToStep(FtueStep.SetupComplete);
  }
});
</script>

<template>
  <step-title :title="t('ftue.videoMeetingLink')" />

  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage }}
  </notice-bar>

  <div class="video-meeting-link-container">
    <provider-card-button
      :title="t('ftue.connectWithZoom')"
      :description="t('ftue.connectWithZoomInfo')"
      :iconSrc="zoomLogo"
      :iconAlt="t('ftue.zoomIcon')"
      @click="onZoomButtonClick()"
    />
  </div>

  <h3>{{ t('ftue.customVideoMeetingLink') }}</h3>
  <p>{{ t('ftue.customVideoMeetingLinkInfo') }}</p>

  <text-input
    name="customVideoMeetingLink"
    :placeholder="t('ftue.customVideoMeetingLinkPlaceholder')"
    v-model="customMeetingLink"
  />

  <div class="buttons-container">
    <link-button :title="t('ftue.skipThisStep')" class="btn-skip" @click="onSkipButtonClick()" :disabled="isLoading">
      {{ t('ftue.skipThisStep') }}
    </link-button>
    <primary-button variant="outline" :title="t('label.back')" :disabled="isLoading" @click="onBackButtonClick">
      {{ t('label.back') }}
    </primary-button>
    <primary-button :title="t('label.continue')" @click="onContinueButtonClick()" :disabled="isContinueButtonDisabled">
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

.notice-bar {
  margin-block-end: 1.5rem;
}

.video-meeting-link-container {
  margin-block-end: 2.25rem;
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 5.8125rem;

  button {
    min-width: 123px;
  }

  .btn-skip {
    min-width: auto;
  }

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
    text-transform: lowercase;
    padding-inline: 0.5rem;
  }
}
</style>