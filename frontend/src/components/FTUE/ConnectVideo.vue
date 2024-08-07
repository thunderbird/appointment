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
  hasNextStep, hasPreviousStep, errorMessage,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;

const externalConnectionStore = useExternalConnectionsStore();
const customMeetingLink = ref('');
const customMeetingLinkRef = ref();

const initFlowKey = 'tba/startedMeetingConnect';

onMounted(async () => {
  isLoading.value = true;
  await externalConnectionStore.fetch(call);
  isLoading.value = false;

  const isBackFromConnectFlow = localStorage?.getItem(initFlowKey);
  localStorage?.removeItem(initFlowKey);

  if (isBackFromConnectFlow) {
    const { data, error } = await call('zoom/ftue-status').get().json();
    // Did they hit back?
    if (error?.value) {
      errorMessage.value = data.value?.detail?.message;
      return;
    }

    await nextStep(call);
  }
});

const onSubmit = async () => {
  isLoading.value = true;
  await nextStep(call);
};

const onSkip = async () => {
  isLoading.value = true;
  await nextStep(call);
};

const connectZoom = async () => {
  // If they have zoom attached, just skip for now.
  if (externalConnectionStore.zoom.length > 0) {
    await nextStep(call);
    return;
  }

  localStorage?.setItem(initFlowKey, true);
  isLoading.value = true;
  const { data } = await call('zoom/auth').get().json();
  // Ship them to the auth link
  window.location.href = data.value.url;
};

</script>
<template>
  <div class="content">
    <div class="cards">
      <div class="card zoom" @click="connectZoom">
        <div class="chip">Recommended</div>
        <img class="zoom-logo" src="@/assets/svg/zoom-logo.svg" :alt="t('heading.zoom')"/>
        <p class="zoom-description">
          {{ t('text.connectZoom') }}
        </p>
        <primary-button class="connect-zoom" :disabled="isLoading">{{ t('label.connect') }}</primary-button>
      </div>
      <div class="card" :class="{'card-selected': customMeetingLink.length > 0}" @click="customMeetingLinkRef.focus()">
        <strong>{{ t('ftue.customVideoMeetingLink') }}</strong>
        <p>{{ t('ftue.customVideoMeetingText') }}</p>
        <text-input
          name="custom-meeting-link"
          v-model="customMeetingLink"
          ref="customMeetingLinkRef"
          placeholder="https://meet.google.com"
        >
          {{ t('ftue.videoMeetingLink') }}
        </text-input>
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
    >{{ t('label.back') }}
    </secondary-button>
    <primary-button
      class="btn-continue"
      :title="t('label.continue')"
      :tooltip="customMeetingLink.length === 0 ? t('ftue.videoConnectionRequired') : null"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading || customMeetingLink.length === 0"
    >
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>
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

  &:hover,
  &:focus-within {
    border-color: var(--teal-700);
    cursor: pointer;
  }
}

.card-selected {
  border-color: var(--teal-700);
  cursor: pointer;
}

.chip {
  display: flex;
  justify-content: center;
  align-self: flex-end;
  align-items: center;
  width: 6.0625rem;
  min-height: 1.0625rem;
  font-size: 0.5625rem;
  font-weight: 700;
  color: var(--tbpro-text);
  background-color: var(--tbpro-appointment-seconday);
  border-radius: 0.1875rem;
  text-transform: uppercase;
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
