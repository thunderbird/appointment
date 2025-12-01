<script setup lang="ts">
import { ref, inject, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';
import { CheckboxInput, TextInput, PrimaryButton, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { CalendarListResponse, PydanticException } from '@/models';
import { useFTUEStore } from '@/stores/ftue-store';
import { FtueStep } from '@/definitions';
import { handleFormError } from '@/utils';

import StepTitle from '../components/StepTitle.vue';

const call = inject(callKey);

const ftueStore = useFTUEStore();
const { t } = useI18n();

const calendarUrl = ref(null);
const noSignInCredentialsRequired = ref(false);
const login = ref(null);
const password = ref(null);
const errorMessage = ref(null);
const isLoading = ref(false);
const formRef = useTemplateRef('formRef');

const onBackButtonClick = () => {
  ftueStore.moveToStep(FtueStep.ConnectCalendars, true);
};

const onContinueButtonClick = async () => {
  if (!formRef.value.checkValidity()) {
    return;
  }

  isLoading.value = true;
  errorMessage.value = null;

  try {
    const payload =  noSignInCredentialsRequired.value
      ? { url: calendarUrl.value }
      : { url: calendarUrl.value, user: login.value, password: password.value };

    const { error, data }: CalendarListResponse = await call('caldav/auth').post(payload).json();

    if (error.value) {
      const err = data?.value as PydanticException;
      const { title } = handleFormError(t, formRef, err);

      errorMessage.value = title;
      return;
    }

    ftueStore.clearMessages();
    await ftueStore.moveToStep(FtueStep.CreateBookingPage);
  } catch (error) {
    errorMessage.value = error ? error.message : t('error.somethingWentWrong');
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <step-title :title="t('ftue.connectWithCalDav')" />

  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage }}
  </notice-bar>

  <form ref="formRef" @submit.prevent @keyup.enter="onContinueButtonClick">
    <div class="calendar-url-container">
      <img src="@/assets/svg/icons/calendar.svg" :alt="t('ftue.calendarIcon')" :title="t('ftue.calendarIcon')"/>
      <text-input
        name="calendarUrl"
        :placeholder="t('ftue.calendarUrlPlaceholder')"
        required
        class="calendar-url-input"
        v-model="calendarUrl"
      >
        {{ t('ftue.calendarUrl') }}
      </text-input>
    </div>

    <div class="no-sign-in-credentials-checkbox">
      <checkbox-input
        name="noSignInCredentialsRequired"
        :label="t('ftue.noSignInCredentialsRequired')"
        class="no-sign-in-credentials-checkbox"
        v-model="noSignInCredentialsRequired"
      />
    </div>

    <div class="credentials-container">
      <text-input name="login" required v-model="login" :disabled="noSignInCredentialsRequired">
        {{ t('label.logIn') }}
      </text-input>

      <text-input name="password" type="password" required v-model="password" :disabled="noSignInCredentialsRequired">
        {{ t('label.password') }}
      </text-input>
    </div>

    <div class="buttons-container">
      <primary-button variant="outline" :title="t('label.back')" @click="onBackButtonClick" :disabled="isLoading">
        {{ t('label.back') }}
      </primary-button>
      <primary-button :title="t('label.continue')" @click="onContinueButtonClick" :disabled="isLoading">
        {{ isLoading ? t('label.connecting') : t('label.continue') }}
      </primary-button>
    </div>
  </form>
</template>

<style scoped>
.notice-bar {
  margin-block-end: 1.5rem;
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

  button {
    min-width: 123px;
  }

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>