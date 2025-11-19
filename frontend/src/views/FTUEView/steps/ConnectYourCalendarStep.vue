<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { PrimaryButton, LinkButton } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';

const { t } = useI18n();

const ftueStore = useFTUEStore();
</script>

<template>
  <h2>{{ t('ftue.connectYourCalendar') }}</h2>
  <p>{{ t('ftue.connectYourCalendarInfo') }}</p>

  <button>
    <img src="@/assets/svg/icons/calendar.svg" :alt="t('ftue.calendarIcon')" :title="t('ftue.calendarIcon')"/>

    <div>
      <h3>{{ t('ftue.connectCalendarCalDav') }}</h3>
      <p>{{ t('ftue.connectCalendarCalDavInfo') }}</p>
    </div>
  </button>

  <button>
    <img src="@/assets/svg/google-calendar-logo.svg" :alt="t('ftue.googleCalendarLogo')" :title="t('ftue.googleCalendarLogo')"/>

    <div>
      <h3>{{ t('ftue.connectCalendarCalDav') }}</h3>
      <p>{{ t('ftue.connectCalendarCalDavInfo') }}</p>
    </div>
  </button>

  <div class="buttons-container">
    <link-button :title="t('label.cancel')" @click="ftueStore.previousStep()">
      {{ t('label.cancel') }}
    </link-button>
    <primary-button :title="t('label.continue')" @click="ftueStore.nextStep()">
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<style scoped>
h2 {
  font-size: 2.25rem;
  font-family: metropolis;
  font-weight: normal;
  letter-spacing: -0.36px;
  line-height: 1.2;
  color: var(--colour-ti-highlight);
  margin: 0 0 1.1325rem 0;
}

p {
  line-height: 1.32;
  margin-block-end: 1rem;
}

button {
  display: flex;
  gap: 1.5rem;
  padding: 1rem;
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.12);
  border-radius: 0.5rem;
  text-align: left;
  align-items: center;

  img { 
    width: 2.25rem;
    height: 2.25rem;
  }

  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--colour-ti-base);
    margin-block-end: 0.5rem;
  }

  p {
    margin-block-end: 0;
  }

  &:hover {
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.12);
  }
}

button + button {
  margin-block-start: 0.5rem;
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 4.25rem;

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }

  button + button {
    margin-block-start: 0;
  }
}
</style>