<script setup lang="ts">
import { useFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';
import { onMounted, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { AlertSchemes, FtueStep } from '@/definitions';
import { refreshKey } from '@/keys';
import WordMark from '@/elements/WordMark.vue';
import AlertBox from '@/elements/AlertBox.vue';
import GooglePermissions from '@/components/FTUE/CalendarProvider.vue';
import SetupProfile from '@/components/FTUE/SetupProfile.vue';
import ConnectCalendars from '@/components/FTUE/ConnectCalendars.vue';
import SetupSchedule from '@/components/FTUE/SetupSchedule.vue';
import ConnectVideo from '@/components/FTUE/ConnectVideo.vue';
import Finish from '@/components/FTUE/StepFinish.vue';
import DashboardView from '@/views/DashboardView/index.vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';

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
  <dashboard-view></dashboard-view>
  <div class="page-ftue overlay" role="dialog" tabindex="-1" aria-labelledby="ftue-title" aria-modal="true">
    <div class="modal">
      <div class="relative flex w-full flex-col items-center">
        <div class="modal-header">
          <word-mark v-if="currentStep === FtueStep.SetupProfile || currentStep === FtueStep.Finish"/>
          <h2 id="ftue-title">
            {{ t(stepTitle) }}
          </h2>
          <alert-box
            v-if="errorMessage"
            :alert="errorMessage"
            :scheme="AlertSchemes.Error"
            @close="errorMessage = null"
          />
          <alert-box
            v-else-if="warningMessage"
            :alert="warningMessage"
            :scheme="AlertSchemes.Warning"
            @close="warningMessage = null"
          />
          <alert-box
            v-else-if="infoMessage"
            :alert="infoMessage"
            :scheme="AlertSchemes.Info"
            @close="infoMessage = null"
          />
        </div>
        <div class="modal-body flex w-full flex-col items-center justify-center">
          <setup-profile v-if="currentStep === FtueStep.SetupProfile"/>
          <google-permissions v-else-if="currentStep === FtueStep.CalendarProvider"/>
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
  z-index: 9999;
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
  width: 100%;
  gap: 1rem;
  margin-block-end: 1rem;
}

#ftue-title {
  color: var(--colour-ti-base);
  font-family: 'Inter', 'sans-serif';
  font-weight: 400;
  font-size: 1.375rem;
  line-height: 1.664rem;
  margin-block: 1rem;
}

/* position-center apmt-background-color fixed z-[60] flex size-full gap-6 rounded-xl bg-white p-8 pb-0 drop-shadow-xl*/
.modal {
  --background-color: var(--colour-primary-soft);
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
  --background-color: var(--colour-neutral-raised);
  --background: url('@/assets/svg/ftue-background-dark.svg');
  border: 0.0625rem solid var(--colour-apmt-primary);
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
  .modal {
    box-sizing: content-box;
    width: 50rem; /* 800px */
    height: fit-content;
    padding: 2rem 2rem 0;
    overflow: visible;
  }

  .divider {
    width: 50rem;
    height: 0.0625rem;
  }

  .footer {
    padding-bottom: 0;
  }
}

</style>
