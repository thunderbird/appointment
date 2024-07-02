<template>
  <div class="content">
    <form ref="formRef" autocomplete="off" autofocus @submit.prevent @keyup.enter="onSubmit">
      <text-input name="full-name" v-model="fullName" required>{{ t('ftue.fullName') }}</text-input>
      <text-input name="username" v-model="username" required>{{ t('label.username') }}</text-input>
      <select-input name="timezone" :options="timezoneOptions" v-model="timezone" required>{{ t('label.timeZone') }}</select-input>
    </form>
  </div>
  <div class="buttons">
    <primary-button
      class="btn-continue"
      :title="t('label.continue')"
      v-if="hasNextStep"
      @click="onSubmit"
    >
      {{ t('label.continue') }}
    </primary-button>
  </div>
</template>

<script setup>

import TextInput from '@/tbpro/elements/TextInput.vue';
import SelectInput from '@/tbpro/elements/SelectInput.vue';
import {
  inject, ref,
} from 'vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import { storeToRefs } from 'pinia';
import { useFTUEStore } from '@/stores/ftue-store';
import { useUserStore } from '@/stores/user-store';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from "@/keys";

const { t } = useI18n();
const dj = inject(dayjsKey);
const call = inject('call');
const ftueStore = useFTUEStore();
const {
  hasNextStep,
} = storeToRefs(ftueStore);
const { nextStep } = ftueStore;
const user = useUserStore();

const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

/**
 * @type {Ref<HTMLFormElement>}
 */
const formRef = ref();
const fullName = ref(user.data.name);
const username = ref(user.data.username);
const timezone = ref(user.data.timezone ?? dj.tz.guess());
const isLoading = ref(false);

const onSubmit = async () => {
  isLoading.value = true;

  if (!formRef.value.checkValidity()) {
    isLoading.value = false;
    return;
  }

  const response = await user.updateUser(call, {
    name: fullName.value,
    username: username.value,
    timezone: timezone.value,
  });

  if (response.error) {
    isLoading.value = false;
    return;
  }

  await nextStep();
};

</script>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.content {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 23.75rem;
  gap: 2rem;
}
form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}
@media (--md) {
  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
