<template>
  <div class="content">
    <div class="cards">
      <div class="card zoom" @click="connectZoom">
        <img class="zoom-logo" src="@/assets/svg/zoom-logo.svg" :alt="t('heading.zoom')"/>
        <p class="zoom-description">
          {{ t('text.connectZoom') }}
        </p>
        <primary-button class="connect-zoom" :disabled="isLoading">{{ t('label.connect') }}</primary-button>
      </div>
      <div class="card">
        <strong>{{ t('ftue.customVideoMeetingLink') }}</strong>
        <p>{{ t('ftue.customVideoMeetingText') }}</p>
        <text-input name="custom-meeting-link" v-model="customMeetingLink" placeholder="http://meet.google.com">{{ t('ftue.videoMeetingLink') }}</text-input>
      </div>
    </div>
    <div class="skip-text">
      <a href="#" @click="onSkip">{{ t('ftue.skipConnectVideo') }}</a>
    </div>
  </div>
  <div class="buttons">
    <secondary-button
      class="btn-back"
      :title="t('label.back')"
      v-if="hasPreviousStep"
      :disabled="isLoading"
      @click="previousStep()"
    >Back
    </secondary-button>
    <primary-button
      class="btn-continue"
      :title="t('label.continue')"
      :tooltip="customMeetingLink.length === 0 ? t('ftue.videoConnectionRequired') : null"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading || customMeetingLink.length === 0"
    >
      Continue
    </primary-button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import {
  onMounted, inject, ref,
} from 'vue';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import { useFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';

const { t } = useI18n();

const call = inject('call');
const isLoading = ref(false);

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;

const externalConnectionStore = useExternalConnectionsStore();
const { zoom } = storeToRefs(externalConnectionStore);
const customMeetingLink = ref('');

const initFlowKey = 'tba/startedMeetingConnect';

onMounted(async () => {
  isLoading.value = true;
  await externalConnectionStore.fetch(call);
  isLoading.value = false;

  const isBackFromConnectFlow = localStorage?.getItem(initFlowKey);
  localStorage?.removeItem(initFlowKey);

  // Error occurred during flow
  if (isBackFromConnectFlow && zoom.value.length === 0) {
    return;
  }

  if (isBackFromConnectFlow) {
    await nextStep();
  }
});

const onSubmit = async () => {
  isLoading.value = true;
  await nextStep();
};

const onSkip = async () => {
  isLoading.value = true;
  await nextStep();
};

const connectZoom = async () => {
  localStorage?.setItem(initFlowKey, true);
  isLoading.value = true;
  const { data } = await call('zoom/auth').get().json();
  // Ship them to the auth link
  window.location.href = data.value.url;
};

</script>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-family: 'Inter', 'sans-serif';
  font-size: 0.8125rem;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 3.125rem;
  width: 100%;
  justify-content: center;
  align-items: center;
}

.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  padding: 1rem;
  border-radius: 0.5625rem;
  background-color: color-mix(in srgb, var(--neutral) 65%, transparent);
  border: 0.0625rem solid color-mix(in srgb, var(--neutral) 65%, transparent);
  transition: var(--transition);

  &.zoom:hover {
    border-color: var(--teal-700);
    cursor: pointer;
  }
}

.zoom-logo {
  margin: auto;
  width: 8.25rem;
}

.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

  .skip-text {
    color: var(--tbpro-primary-pressed);
    margin-right: 0;
    margin-left: auto;
    text-transform: uppercase;
    font-size: 0.5625rem;
    font-weight: 600;
    text-decoration: underline;
    padding: 0.75rem 1.5rem;
  }

@media (--md) {
  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }

  .card {
    width: 18.75rem;
    height: 15.0rem;
  }

  .content {
    margin-top: 0;
  }

  .cards {
    flex-direction: row;
    margin-top: 0;
  }

  .connect-zoom {
    margin: auto;
    width: 50%;
  }
}
</style>
