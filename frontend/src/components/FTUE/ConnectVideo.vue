<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { onMounted, inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import { createFTUEStore } from '@/stores/ftue-store';
import { createExternalConnectionsStore } from '@/stores/external-connections-store';
import { callKey } from '@/keys';
import {
  AuthUrl, AuthUrlResponse, BooleanResponse, Error, Exception, ExceptionDetail,
} from '@/models';
import { createScheduleStore } from '@/stores/schedule-store';

const { t } = useI18n();

const call = inject(callKey);
const isLoading = ref(false);

const ftueStore = createFTUEStore(call);
const scheduleStore = createScheduleStore(call);
const externalConnectionStore = createExternalConnectionsStore(call);

const {
  hasNextStep, hasPreviousStep, errorMessage,
} = storeToRefs(ftueStore);
const { schedules } = storeToRefs(scheduleStore);

const customMeetingLink = ref('');
const customMeetingLinkRef = ref<typeof TextInput>();

const initFlowKey = 'tba/startedMeetingConnect';

onMounted(async () => {
  isLoading.value = true;
  await externalConnectionStore.fetch();
  isLoading.value = false;

  const isBackFromConnectFlow = localStorage?.getItem(initFlowKey);
  localStorage?.removeItem(initFlowKey);

  if (isBackFromConnectFlow) {
    const { data, error }: BooleanResponse = await call('zoom/ftue-status').get().json();
    // Did they hit back?
    if (error?.value) {
      errorMessage.value = {
        title: ((data.value as Exception)?.detail as ExceptionDetail)?.message,
        details: null,
      };
      return;
    }

    await ftueStore.nextStep();
  }
});

const onSubmit = async () => {
  isLoading.value = true;

  const data = await scheduleStore.updateSchedule(schedules.value[0].id, {
    ...schedules.value[0],
    location_url: customMeetingLink.value,
  });

  if ((data as Error)?.error) {
    errorMessage.value = { title: (data as Error)?.message, details: null };
    isLoading.value = false;
    return;
  }

  await ftueStore.nextStep();
};

const onSkip = async () => {
  isLoading.value = true;
  await ftueStore.nextStep();
};

const connectZoom = async () => {
  // If they have zoom attached, just skip for now.
  if (externalConnectionStore.zoom.length > 0) {
    await ftueStore.nextStep();
    return;
  }

  localStorage?.setItem(initFlowKey, 'true');
  isLoading.value = true;
  const { data }: AuthUrlResponse = await call('zoom/auth').get().json();
  // Ship them to the auth link
  window.location.href = (data.value as AuthUrl).url;
};

</script>

<template>
  <div class="content">
    <div class="cards">
      <div class="card zoom" @click="connectZoom">
        <div class="chip">Recommended</div>
        <img class="is-light-mode zoom-logo" src="@/assets/svg/zoom-logo.svg" :alt="t('heading.zoom')"/>
        <img class="is-dark-mode zoom-logo" src="@/assets/svg/zoom-logo-dark.svg" :alt="t('heading.zoom')"/>
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
      @click="ftueStore.previousStep()"
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
@import '@/assets/styles/mixins.pcss';

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
  --colour-background: var(--colour-neutral-base);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  padding: 1rem;
  border-radius: 0.5625rem;
  @mixin faded-background var(--colour-background);
  @mixin faded-border var(--colour-background);
  transition: var(--transition);

  &:hover,
  &:focus-within {
    border-color: var(--colour-service-primary);
    cursor: pointer;
  }
}

.dark {
  .card {
    --colour-background: var(--colour-neutral-lower);
  }
}

.card-selected {
  border-color: var(--colour-service-primary);
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
  color: var(--colour-ti-base);
  background-color: var(--colour-service-secondary);
  border-radius: 0.1875rem;
  text-transform: uppercase;
}

.dark {
  .chip {
    color: var(--colour-neutral-base);
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
  color: var(--colour-service-primary-pressed);
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
