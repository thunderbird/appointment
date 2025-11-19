<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { CheckboxInput, TextInput, PrimaryButton, LinkButton } from '@thunderbirdops/services-ui';
import { useFTUEStore } from '@/stores/ftue-store';

const { t } = useI18n();
const ftueStore = useFTUEStore();

const onSubmit = () => {
  console.log('Connect with CalDAV');
};
</script>

<template>
  <h2>{{ t('ftue.connectWithCalDav') }}</h2>

  <form @submit.prevent @keyup.enter="onSubmit">
    <div class="calendar-url-container">
      <img src="@/assets/svg/icons/calendar.svg" :alt="t('ftue.calendarIcon')" :title="t('ftue.calendarIcon')"/>
      <text-input name="calendarUrl" :placeholder="t('ftue.calendarUrlPlaceholder')" required class="calendar-url-input">
        {{ t('ftue.calendarUrl') }}
      </text-input>
    </div>

    <div class="no-sign-in-credentials-checkbox">
      <checkbox-input
        name="noSignInCredentialsRequired"
        :label="t('ftue.noSignInCredentialsRequired')"
        class="no-sign-in-credentials-checkbox"
      />
    </div>

    <div class="credentials-container">
      <text-input name="login" required>
        {{ t('label.logIn') }}
      </text-input>

      <text-input name="password" required>
        {{ t('label.password') }}
      </text-input>
    </div>

    <div class="buttons-container">
      <link-button :title="t('label.cancel')" @click="ftueStore.previousStep()">
        {{ t('label.cancel') }}
      </link-button>
      <primary-button :title="t('label.continue')" @click="ftueStore.nextStep()">
        {{ t('label.continue') }}
      </primary-button>
    </div>
  </form>
</template>

<style scoped>
h2 {
  font-size: 2.25rem;
  font-family: metropolis;
  font-weight: normal;
  letter-spacing: -0.36px;
  line-height: 1.2;
  color: var(--colour-ti-highlight);
  margin: 0 0 1.5rem 0;
}

.calendar-url-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-block-end: 1rem;

  .calendar-url-input {
    width: 100%;
  }
}

.no-sign-in-credentials-checkbox {
  margin-block-end: 2.25rem;
}

.credentials-container {
  display: flex;
  gap: 1.5rem;

  .text-input {
    width: 100%;
  }
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;
  margin-block-start: 10.45rem;

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>