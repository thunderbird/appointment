<script setup lang="ts">
import { inject, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { PhArrowRight } from '@phosphor-icons/vue';
import { BaseButton, SelectInput, TextInput, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { dayjsKey, shortUrlKey } from '@/keys';
import { useUserStore } from '@/stores/user-store';
import { useFTUEStore } from '@/stores/ftue-store';
import { FtueStep } from '@/definitions';
import { handleFormError } from '@/utils';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();

const shortUrl = inject(shortUrlKey);
const dj = inject(dayjsKey);

const user = useUserStore();
const ftueStore = useFTUEStore();

const fullName = ref(user.data.name ?? '');
const username = ref(user.data.username ?? '');
const timezone = ref(user.data.settings.timezone ?? dj.tz.guess());
const isLoading = ref(false);
const errorMessage = ref(null);
const usernameError = ref(null);
const fullNameError = ref(null);
const formRef = useTemplateRef('formRef');

// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone: string) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

const quickLink = shortUrl.substring(shortUrl.indexOf('//')+2) + '/';

const onSubmit = async () => {
  ftueStore.clearMessages();
  isLoading.value = true;

  try {
    const payload = {
      name: fullName.value,
      username: username.value,
      timezone: timezone.value,
    }

    // Required values from an <input /> does not validate trim()
    // so we need to check it manually
    if (fullName.value.trim() === '') {
      fullNameError.value = t('error.fieldIsRequired', { field: t('ftue.fullName') });
    }

    if (username.value.trim() === '') {
      usernameError.value = t('error.fieldIsRequired', { field: t('ftue.urlUsername') });
    }

    // If there were errors detected, we short-circuit the flow
    if (fullNameError.value || usernameError.value) {
      return;
    }

    if (!formRef.value.checkValidity()) {
      return;
    }

    const response = await user.updateUser(payload);

    if (response.error) {
      const formattedError = handleFormError(t, formRef, response.error);
      errorMessage.value = formattedError?.title;
      return;
    }

    await ftueStore.moveToStep(FtueStep.ConnectCalendars);
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <step-title :title="t('ftue.createYourProfile')" />

  <notice-bar :type="NoticeBarTypes.Critical" v-if="errorMessage" class="notice-bar">
    {{ errorMessage }}
  </notice-bar>

  <form ref="formRef" @submit.prevent @keyup.enter="onSubmit">
    <text-input
      name="fullName"
      placeholder="Giles Bernam"
      required
      v-model="fullName"
      :error="fullNameError"
    >
      {{ t('ftue.fullName') }}
    </text-input>
  
    <text-input
      name="username"
      placeholder="Giles"
      required
      :outer-prefix="quickLink"
      v-model="username"
      :error="usernameError"
    >
      {{ t('ftue.urlUsername') }}
    </text-input>
  
    <select-input
      name="timezone"
      required
      :options="timezoneOptions"
      v-model="timezone"
    >
      {{ t('label.timeZone') }}
    </select-input>

    <base-button type="brand" @click="onSubmit" :disabled="isLoading">
      {{ isLoading ? t('label.loading') : t('ftue.createAccount') }}

      <template #iconRight>
        <ph-arrow-right />
      </template>
    </base-button>
  </form>
</template>

<style scoped>
.notice-bar {
  margin-block-end: 1.5rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  button {
    margin-block-start: 5.625rem;
    align-self: flex-end;
  }
}
</style>