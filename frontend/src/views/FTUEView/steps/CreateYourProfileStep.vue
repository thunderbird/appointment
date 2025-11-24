<script setup lang="ts">
import { inject, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { PhArrowRight } from '@phosphor-icons/vue';
import { BaseButton, SelectInput, TextInput } from '@thunderbirdops/services-ui';
import { dayjsKey, shortUrlKey } from '@/keys';
import { useUserStore } from '@/stores/user-store';
import { useFTUEStore } from '@/stores/ftue-store';
import { FtueStep } from '@/definitions';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();

const shortUrl = inject(shortUrlKey);
const dj = inject(dayjsKey);

const user = useUserStore();
const ftueStore = useFTUEStore();

const fullName = ref(null);
const username = ref(null);
const timezone = ref(user.data.settings.timezone ?? dj.tz.guess());
const isLoading = ref(false);
const errorMessage = ref(null);
const formRef = useTemplateRef('formRef');

// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone: string) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

const quickLink = shortUrl.substring(shortUrl.indexOf('//')+2) + '/';

const onSubmit = async () => {
  isLoading.value = true;

  try {
    const payload = {
      name: fullName.value,
      username: username.value,
      timezone: timezone.value,
    }

    if (!formRef.value.checkValidity()) {
      return;
    }

    const response = await user.updateUser(payload);

    if (response.error) {
      errorMessage.value = response.error;
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

  <form ref="formRef" @submit.prevent @keyup.enter="onSubmit">
    <text-input
      name="fullName"
      placeholder="Giles Bernam"
      required
      v-model="fullName"
    >
      {{ t('ftue.fullName') }}
    </text-input>
  
    <text-input
      name="username"
      placeholder="Giles"
      required
      :outer-prefix="quickLink"
      v-model="username"
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