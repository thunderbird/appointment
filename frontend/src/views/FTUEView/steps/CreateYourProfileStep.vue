<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { PhArrowRight } from '@phosphor-icons/vue';
import { BaseButton, SelectInput, TextInput } from '@thunderbirdops/services-ui';
import { callKey, dayjsKey, shortUrlKey } from '@/keys';
import { createUserStore } from '@/stores/user-store';
import { useFTUEStore } from '@/stores/ftue-store';

import StepTitle from '../components/StepTitle.vue';

const { t } = useI18n();

const shortUrl = inject(shortUrlKey);
const call = inject(callKey);
const dj = inject(dayjsKey);

const user = createUserStore(call);
const ftueStore = useFTUEStore();

const timezone = ref(user.data.settings.timezone ?? dj.tz.guess());

// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone: string) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

const quickLink = shortUrl.substring(shortUrl.indexOf('//')+2) + '/';

const onSubmit = async () => {
  await ftueStore.nextStep();
};
</script>

<template>
  <step-title :title="t('ftue.createYourProfile')" />

  <form @submit.prevent @keyup.enter="onSubmit">
    <text-input
      name="fullName"
      placeholder="Giles Bernam"
      required
    >
      {{ t('ftue.fullName') }}
    </text-input>
  
    <text-input
      name="username"
      placeholder="Giles"
      required
      :outer-prefix="quickLink"
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

    <base-button type="brand" @click="onSubmit">
      {{ t('ftue.createAccount') }}

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