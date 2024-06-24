<template>
  <div class="page-ftue overlay fixed left-0 top-0 z-[55] h-screen w-screen overflow-hidden" role="dialog" tabindex="-1" aria-labelledby="ftue-title" aria-modal="true">
    <div class="modal">
      <div class="relative flex size-full w-full flex-col items-center gap-4">
        <word-mark v-if="currentStep === ftueStep.setupProfile"/>
        <h2 id="ftue-title">
          {{ stepTitle }}
        </h2>
        <div class="flex w-full flex-col items-center justify-center">
          <setup-profile v-if="currentStep === ftueStep.setupProfile"/>
          <google-permissions v-else-if="currentStep === ftueStep.googlePermissions"/>
          <connect-calendars v-else-if="currentStep === ftueStep.connectCalendars"/>
          <setup-schedule v-else-if="currentStep === ftueStep.setupSchedule"/>
          <connect-video v-else-if="currentStep === ftueStep.connectVideoConferencing"/>
          <finish v-else-if="currentStep === ftueStep.finish"/>
          <div class="error-page" v-else>
            <span>🤔</span>
            <h2>Huh, how did this happen?</h2>
            <p>Looks like there was an error. Click the button below to go back!</p>
            <primary-button @click="ftueStore.$reset()">Go back</primary-button>
          </div>
        </div>
        <div class="divider"></div>
        <div class="footer">
          <router-link to="contact">Support</router-link>
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
import WordMark from '@/elements/WordMark.vue';
import { onMounted } from 'vue';
import ConnectCalendars from '@/components/FTUE/ConnectCalendars.vue';
import SetupSchedule from '@/components/FTUE/SetupSchedule.vue';
import ConnectVideo from '@/components/FTUE/ConnectVideo.vue';
import Finish from '@/components/FTUE/Finish.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';

const ftueStore = useFTUEStore();
const {
  stepTitle, currentStep,
} = storeToRefs(ftueStore);

onMounted(() => {
  // Force light-mode
  localStorage?.setItem('theme', 'light');
});

</script>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.overlay {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: #727375;
  align-items: center;
  justify-content: center;
}

/* position-center apmt-background-color fixed z-[60] flex size-full gap-6 rounded-xl bg-white p-8 pb-0 drop-shadow-xl*/
.modal {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: white;
  background-image: url('@/assets/svg/ftue-background.svg');
  background-size: cover;
  background-repeat: no-repeat;
  border-radius: 0.75rem;
  padding: 2rem 2rem 0;
}

.modal:before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 12px;
  filter: blur(64px);
  margin: 50% 5% 0;
  opacity: 0.8;
  z-index: -1;
  background: linear-gradient(118.89deg, #A3ECE3 -1.91%, #03AFD7 48.8%, #008080 100.54%);
}

#ftue-title {
  color: var(--tbpro-text);
  font-family: 'Inter', 'sans-serif';
  font-weight: 400;
  font-size: 1.375rem;
  line-height: 1.664rem;
}

.divider {
  width: 50rem;
  height: 1px;
  border-radius: unset;
  background: linear-gradient(90deg, rgba(21, 66, 124, 0) 20.5%, rgba(21, 66, 124, 0.2) 50%, rgba(21, 66, 124, 0) 79.5%);
  position: absolute;
  bottom: 4rem;
}

.footer {
  position: absolute;
  bottom: 0;
  height: 4rem;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  a {
    color: var(--tbpro-primary);
    font-size: 0.75rem;
    line-height: 1.5rem;
  }
}

.error-page {
  width: 100%;
  height: 28.125rem;
  display: flex;
  flex-direction: column;
  margin: auto;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  font-family: 'Inter', 'sans-serif';

  span {
    font-size: 11.25rem;
  }

  h2 {
    font-size: 1.125rem;
    font-weight: 700;
  }

  p {
    font-size: 0.8125rem
  }
}

@media (--md) {
  .modal {
    width: 50rem; /* 800px */
    height: 37.5rem; /* 600px */
  }
}
</style>
