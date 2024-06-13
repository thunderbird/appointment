<template>
  <div
    class="mdl-overlay-close fixed left-0 top-0 z-40 h-screen w-screen bg-gray-800/50"
  ></div>
  <div
    class="position-center fixed z-50 flex w-full max-w-lg flex-col items-center gap-6 rounded-xl bg-white p-12 dark:bg-gray-700"
  >
    <div class="text-2xl font-semibold text-teal-500">
      {{ stepTitle }}
    </div>
    <ftue-view/>
    <div class="flex gap-4">
      <secondary-button
        v-if="hasPreviousStep"
        class="btn-close"
        label="Back"
        @click="previousStep()"
        title="Back"
      />
      <primary-button
        v-if="hasNextStep"
        class="btn-copy"
        label="Continue"
        title="Continue"
        @click="nextStep()"
      />
    </div>
  </div>
</template>

<script setup>

import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import { useI18n } from 'vue-i18n';
import { useFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';

const ftueStore = useFTUEStore();
const { previousStep, nextStep } = ftueStore;
const {
  ftueView, hasPreviousStep, hasNextStep, stepTitle,
} = storeToRefs(ftueStore);

const { t } = useI18n();

</script>
