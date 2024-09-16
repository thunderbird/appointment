<script setup lang="ts">
import { useFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';
import { onMounted, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { FtueStep } from '@/definitions';
import { refreshKey } from '@/keys';
import WordMark from '@/elements/WordMark.vue';
import GooglePermissions from '@/components/FTUE/GooglePermissions.vue';
import SetupProfile from '@/components/FTUE/SetupProfile.vue';
import ConnectCalendars from '@/components/FTUE/ConnectCalendars.vue';
import SetupSchedule from '@/components/FTUE/SetupSchedule.vue';
import ConnectVideo from '@/components/FTUE/ConnectVideo.vue';
import Finish from '@/components/FTUE/Finish.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import NoticeBar from '@/tbpro/elements/NoticeBar.vue';
import ScheduleView from '@/views/ScheduleView.vue';

const ftueStore = useFTUEStore();
const {
  stepTitle, currentStep, infoMessage, errorMessage, warningMessage,
} = storeToRefs(ftueStore);

const { t } = useI18n();
const refresh = inject(refreshKey);

onMounted(async () => {
  await refresh();
});
</script>

<template>
  <schedule-view></schedule-view>
  <div class="page-ftue overlay" role="dialog" tabindex="-1" aria-labelledby="ftue-title" aria-modal="true">
    <div class="modal">
      <div class="relative flex size-full w-full flex-col items-center gap-4">
        <div class="modal-header">
          <word-mark v-if="currentStep === FtueStep.SetupProfile || currentStep === FtueStep.Finish"/>
          <h2 id="ftue-title">
            {{ t(stepTitle) }}
          </h2>
          <notice-bar type="error" v-if="errorMessage">
            {{ errorMessage }}
          </notice-bar>
          <notice-bar type="warning" v-else-if="warningMessage">
            {{ warningMessage }}
          </notice-bar>
          <notice-bar v-else-if="infoMessage">
            {{ infoMessage }}
          </notice-bar>
          <div class="pls-keep-height" v-else/>
        </div>
        <div class="modal-body flex w-full flex-col items-center justify-center">
          <setup-profile v-if="currentStep === FtueStep.SetupProfile"/>
          <google-permissions v-else-if="currentStep === FtueStep.GooglePermissions"/>
          <connect-calendars v-else-if="currentStep === FtueStep.ConnectCalendars"/>
          <setup-schedule v-else-if="currentStep === FtueStep.SetupSchedule"/>
          <connect-video v-else-if="currentStep === FtueStep.ConnectVideoConferencing"/>
          <finish v-else-if="currentStep === FtueStep.Finish"/>
          <div class="error-page" v-else>
            <span>🤔</span>
            <h2>{{ t('ftue.errorHeading') }}</h2>
            <p>{{ t('ftue.errorBody') }}</p>
            <primary-button @click="ftueStore.$reset()">{{ t('label.goBack') }}</primary-button>
          </div>
        </div>
        <div class="divider"></div>
        <div class="footer">
          <router-link to="contact">Support</router-link>
          <router-link to="logout">Log out</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
<style>
/* Ensure you can't scroll the background! */
body {
    overflow: hidden;
}
</style>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.overlay {
  position: fixed;
  display: flex;
  left: 0;
  top: 0;
  z-index: 55;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: color-mix(in srgb, var(--colour-shark-900) 60%, transparent);
  align-items: center;
  justify-content: center;
}

.modal-header {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 8.0rem;
  width: 100%;
  gap: 1rem;
}

/* Empty space if a notice bar isn't shown */
.pls-keep-height {
  min-height: 2.0625rem; /* 33px */
}

#ftue-title {
  color: var(--colour-ti-base);
  font-family: 'Inter', 'sans-serif';
  font-weight: 400;
  font-size: 1.375rem;
  line-height: 1.664rem;
}

/* position-center apmt-background-color fixed z-[60] flex size-full gap-6 rounded-xl bg-white p-8 pb-0 drop-shadow-xl*/
.modal {
  --background-color: var(--colour-neutral-raised);
  --background: url('@/assets/svg/ftue-background.svg');
  position: relative;
  width: 100%;
  height: 100%;
  background-color: var(--background-color);
  background-image: var(--background);
  background-size: cover;
  background-repeat: no-repeat;
  border-radius: 0.75rem;
  padding: 1rem 1rem 0;
  overflow-y: scroll;
  overflow-x: hidden;
}

.dark .modal {
  --background: url('@/assets/svg/ftue-background-dark.svg');
}

.modal::before {
  content: '';
  position: absolute;
  inset: -4px;
  margin: 50% 5% 0;
  opacity: 0.8;
  z-index: -1;
  border-radius: 9px;
  background: linear-gradient(119deg, #A3ECE3 -1.91%, #03AFD7 48.8%, #008080 100.54%);
  filter: blur(30px);
}

.dark {
  .modal::before {
    border-radius: 9px;
    background: linear-gradient(119deg, #0B8C86 -1.91%, #1C6395 100.54%);
    filter: blur(30px);
  }
}

.divider {
  width: 100%;
  padding-bottom: 1px;
  border-radius: unset;
  background: linear-gradient(90deg, rgba(21, 66, 124, 0) 20.5%, rgba(21, 66, 124, 0.2) 50%, rgba(21, 66, 124, 0) 79.5%);
}
.dark {
  .divider {
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.00) 0%, rgba(255, 255, 255, 0.40) 50%, rgba(255, 255, 255, 0.00) 100%);
  }
}

.footer {
  bottom: 0;
  height: 4rem;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 1rem;
  gap: 1rem;

  a {
    color: var(--colour-service-primary-pressed);
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
  .modal-header {
    margin-bottom: 0;
  }

  .modal {
    width: 50rem; /* 800px */
    height: 37.5rem; /* 600px */
    padding: 2rem 2rem 0;
    overflow: visible;
  }

  .modal-body {
    height: 15.0rem;
  }

  .divider {
    position: absolute;
    bottom: 4rem;
    width: 50rem;
    height: 0.0625rem;
  }

  .footer {
    position: absolute;
    padding-bottom: 0;
  }
}

</style>
