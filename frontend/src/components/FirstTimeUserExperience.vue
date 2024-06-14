<template>
  <div role="dialog" tabindex="-1" aria-labelledby="ftue-title" aria-modal="true">
    <div
      class="fixed left-0 top-0 z-[55] h-screen w-screen overflow-hidden bg-gray-800/50"
    ></div>
    <div
      class="position-center apmt-background-color fixed z-[60] flex size-full max-h-xl max-w-3xl  gap-6 rounded-xl bg-white p-12 drop-shadow-xl"
    >
      <div class="relative flex size-full w-full flex-col items-center gap-6">
        <div id="ftue-title" class="text-2xl font-semibold text-teal-500">
          {{ stepTitle }}
        </div>
        <div class="apmt-error-color flex h-12 w-full items-center justify-center font-medium">
          <p>This is a test error, wooooo!</p>
        </div>
        <div class="flex w-full flex-col items-center justify-center">
          <ftue-view/>
        </div>
        <div class="absolute bottom-0 flex gap-4">
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
