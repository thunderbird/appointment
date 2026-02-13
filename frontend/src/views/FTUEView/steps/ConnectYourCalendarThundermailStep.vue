<script setup lang="ts">
import { ref, inject, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';
import { TextInput, PrimaryButton, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { CalendarListResponse, FormExceptionDetail, PydanticException } from '@/models';
import { useFTUEStore } from '@/stores/ftue-store';
import { useUserStore } from '@/stores/user-store';
import { FtueStep } from '@/definitions';
import { handleFormError } from '@/utils';

import StepTitle from '../components/StepTitle.vue';

const call = inject(callKey);

const ftueStore = useFTUEStore();
const userStore = useUserStore();
const { t } = useI18n();

const calendarUrl = ref(import.meta.env.VITE_THUNDERMAIL_CALDAV_URL || null);
const noSignInCredentialsRequired = ref(false);
const username = ref(userStore?.data?.email || null);
const password = ref(null);
const errorMessage = ref<{ title: string; details?: string } | null>(null);
const calendarUrlErrorMessage = ref<string | null>(null);
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
  calendarUrlErrorMessage.value = null;

  try {
    const payload =  noSignInCredentialsRequired.value
      ? { url: calendarUrl.value }
      : { url: calendarUrl.value, user: username.value, password: password.value };

    const { error, data }: CalendarListResponse = await call('caldav/auth').post(payload).json();

    if (error.value) {
      const err = data?.value as PydanticException;
      const formExceptionDetail = err?.detail as FormExceptionDetail;

      // This is related to the calendar url input so the error message should be there
      if (formExceptionDetail?.id === 'REMOTE_CALENDAR_CONNECTION_ERROR') {
        calendarUrlErrorMessage.value = t('ftue.calendarUrlErrorMessage');
        return;
      } else if (formExceptionDetail?.id === 'REMOTE_CALENDAR_AUTHENTICATION_ERROR') {
        errorMessage.value = { title: formExceptionDetail.reason };
        return;
      }

      // If it's a network or another type of backend error, show the notice bar
      const formError = handleFormError(t, formRef, err);

      if (formError) {
        errorMessage.value = {
          title: formError.title,
          details: formError.details,
        };
      }
      return;
    }

    ftueStore.clearMessages();
    await ftueStore.moveToStep(FtueStep.CreateBookingPage);
  } catch (error) {
    const message = error instanceof Error ? error.message : null;

    errorMessage.value = {
      title: message || t('error.somethingWentWrong'),
    };
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <step-title :title="t('ftue.connectWithThundermail')" />

  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage.title }}
    <template v-if="errorMessage.details">
      <br />
      <br />
    </template>
    {{ errorMessage.details }}
  </notice-bar>

  <form ref="formRef" @submit.prevent @keyup.enter="onContinueButtonClick">
    <div class="credentials-container">
      <text-input
        name="username"
        required
        v-model="username"
        :disabled="noSignInCredentialsRequired"
        class="username-input"
      >
        {{ t('label.username') }}
      </text-input>

      <text-input
        name="password"
        type="password"
        required
        v-model="password"
        :disabled="noSignInCredentialsRequired"
        class="app-password-input"
      >
        {{ t('label.appPassword') }}
      </text-input>

      <p class="app-password-info-text">{{ t('ftue.connectWithThundermailAppPasswordInfo') }} 
        <a href="https://support.tb.pro/hc/articles/46805020320275" target="_blank">
          {{ t('ftue.calDavLearnMoreAppPassword') }}
        </a>
      </p>

      <text-input
        name="calendarUrl"
        placeholder="https://calendar.example.com/caldav/"
        required
        class="calendar-url-input"
        v-model="calendarUrl"
        :error="calendarUrlErrorMessage"
        readonly
      >
        {{ t('ftue.calendarUrl') }}
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
form {
  margin-block-start: 2rem;
}

.info-text {
  margin-block-end: 2.25rem;
  color: var(--colour-ti-secondary);
  font-size: 0.875rem;
  line-height: 1.23;

  a {
    text-decoration: underline;
    font-size: 0.75rem;
  }
}

.notice-bar {
  margin-block-end: 1.5rem;
}

.no-sign-in-credentials-checkbox {
  margin-block-end: 2.25rem;
}

.credentials-container {
  margin-block-end: 2.25rem;

  .text-input {
    width: 100%;
  }

  .username-input, .app-password-info-text {
    margin-block-end: 1rem;
  }

  .app-password-input {
    margin-block-end: 0.5rem;
  }

  .app-password-info-text {
    color: var(--colour-ti-muted);
    font-size: 0.6875rem;

    a {
      color: var(--colour-ti-secondary);
      border-block-end: 1px solid var(--colour-ti-secondary);
    }
  }
}

.buttons-container {
  display: flex;
  justify-content: end;
  gap: 1.5rem;

  button {
    min-width: 123px;
  }

  .base.link.filled {
    font-size: 0.75rem;
    color: var(--colour-ti-highlight);
  }
}
</style>