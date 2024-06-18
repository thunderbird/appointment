<template>
  <div class="fixed left-0 top-0 z-[55] h-screen w-screen overflow-hidden bg-gray-800" role="dialog" tabindex="-1" aria-labelledby="ftue-title" aria-modal="true">
    <div
      class="position-center apmt-background-color fixed z-[60] flex size-full max-h-xl max-w-3xl  gap-6 rounded-xl bg-white p-12 drop-shadow-xl"
    >
      <div class="relative flex size-full w-full flex-col items-center gap-4">
        <div id="ftue-title" class="text-2xl font-semibold text-teal-500">
          {{ stepTitle }}
        </div>
        <div class="flex w-full flex-col items-center justify-center">
          <SetupProfile v-if="currentStep === ftueStep.setupProfile"/>
          <GooglePermissions v-else-if="currentStep === ftueStep.googlePermissions"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import { useFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';
import SetupProfile from '@/components/FTUE/SetupProfile.vue';
import { ftueStep } from '@/definitions';
import GooglePermissions from '@/components/FTUE/GooglePermissions.vue';
import InfoBar from '@/elements/InfoBar.vue';

const ftueStore = useFTUEStore();
const {
  stepTitle, currentStep,
} = storeToRefs(ftueStore);

</script>
