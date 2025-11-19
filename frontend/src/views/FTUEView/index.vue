<script setup lang="ts">
import { storeToRefs } from 'pinia';
import OrbGraphic from '@/assets/images/orb-graphic.png';
import { useFTUEStore } from '@/stores/ftue-store';
import { FtueStep } from '@/definitions';

// Steps
import CreateYourProfileStep from './steps/CreateYourProfileStep.vue';
import ConnectYourCalendarStep from './steps/ConnectYourCalendarStep.vue';
import ConnectYourCalendarCalDavStep from './steps/ConnectYourCalendarCalDavStep.vue';
import ConnectYourCalendarGoogleStep from './steps/ConnectYourCalendarGoogleStep.vue';
import CreateBookingPageStep from './steps/CreateBookingPageStep.vue';
import SetYourAvailabilityStep from './steps/SetYourAvailabilityStep.vue';

const STEPS = {
  [FtueStep.SetupProfile]: CreateYourProfileStep,
  [FtueStep.CalendarProvider]: SetYourAvailabilityStep,
}

const ftueStore = useFTUEStore();
const { currentStep } = storeToRefs(ftueStore);

// Force light mode in FTUE
document.documentElement.classList.remove('dark');
</script>

<script lang="ts">
export default {
  name: 'FTUEView'
}
</script>

<template>
  <section>
    <div class="card">
      <!-- Left side: Orb graphic -->
      <div class="left-side">
        <img :src="OrbGraphic" alt="Thunderbird Orb" class="orb-graphic" />
      </div>

      <!-- Right side: Panel -->
      <div class="right-side">
        <div class="panel">
          <component :is="STEPS[currentStep]" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--colour-ti-base);

  .card {
    width: 100%;
    height: auto;
    min-height: 100vh;
    display: flex;
    align-items: stretch;
    justify-content: center;
    background-color: inherit;

    .left-side {
      display: none;
    }

    .right-side {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      min-height: 100vh;
      flex: 1;
      background-color: var(--colour-neutral-base);
    }

    .panel {
      padding: 0 2rem;

      &:has(.notice-bar) {
        padding: 6rem 2rem;
      }
    }
  }
}

@media (--sm) {
  section {
    .card {
      .left-side {
        display: block;
        flex: 1;
        max-width: 556px;
        min-height: 100vh;
        background-color: #1A202C; /* --colour-ti-base forced on light mode */

        .orb-graphic {
          display: block;
          width: 100%;
          height: 100%;
          min-height: 100vh;
          object-fit: cover;
        }
      }
    }
  }
}

@media (--xl) {
  section {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background-color: #1A202C; /* --colour-ti-base forced on light mode */
    padding: 1rem;

    .card {
      width: 1280px;
      height: auto;
      min-height: 720px;
      border-radius: 2rem;
      align-items: initial;
      border: 0.0625rem solid var(--colour-neutral-border-intense);

      .left-side {
        background-color: unset;
        height: auto;
        min-height: auto;

        .orb-graphic {
          min-height: auto;
          border-radius: 2rem 0 0 2rem;
        }
      }

      .right-side {
        border-radius: 0 2rem 2rem 0;
        min-height: auto;

        .panel {
          padding: 6rem 10rem 5.625rem 6rem;

          &:has(.notice-bar) {
            padding: 6rem 10rem 5.625rem 6rem;
          }
        }
      }
    }
  }
}
</style>
