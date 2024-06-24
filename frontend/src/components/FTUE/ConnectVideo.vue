<template>
  <div class="content">
    <div class="card zoom" @click="connectZoom">
      <img class="zoom-logo" src="@/assets/svg/zoom-logo.svg" alt="Zoom"/>
      <p class="zoom-description">
        Connect your Zoom account to generate instant meeting invites for each booking
      </p>
      <primary-button class="connect-zoom" :disabled="isLoading">Connect</primary-button>
    </div>
    <div class="card">
      <h2>Custom video meeting link</h2>
      <p>Use a single meeting link for all bookings from your selected provider</p>
      <text-input name="custom-meeting-link" v-model="customMeetingLink" placeholder="http://meet.google.com">Video meeting link</text-input>
    </div>
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
      :title="continueTitle"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading || !selected"
    >
      Continue
    </primary-button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import {
  onMounted, inject, ref, computed,
} from 'vue';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import SyncCard from '@/tbpro/elements/SyncCard.vue';
import TextButton from '@/elements/TextButton.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import { useExternalConnectionsStore } from '@/stores/external-connections-store.js';
import { useRoute, useRouter } from 'vue-router';

const { t } = useI18n();

const call = inject('call');
const route = useRoute();
const router = useRouter();
const isLoading = ref(false);

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;

const externalConnectionStore = useExternalConnectionsStore();
const { zoom } = storeToRefs(externalConnectionStore);
const customMeetingLink = ref('');
const selected = computed(() => zoom.value.length > 0 || customMeetingLink.value.length > 0);

const continueTitle = '';// computed(() => (selected.value ? 'Continue' : 'Please enable one calendar to continue'));
const initFlowKey = 'tba/startedMeetingConnect';

const errorMessage = ref('');

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
  gap: 3.125rem;
  width: 100%;
  justify-content: center;
  align-items: center;
  height: 23rem;
  margin-top: 6.25rem;
  font-family: 'Inter', 'sans-serif';
  font-size: 0.8125rem;
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

@media (--md) {
  .card {
    width: 18.75rem;
    height: 15.0rem;
  }

  .content {
    flex-direction: row;
    margin-top: 0;
  }

  .connect-zoom {
    margin: auto;
    width: 50%;
  }
}
</style>
