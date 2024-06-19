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

const dj = inject('dayjs');
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

const onSubmit = async () => {
  if (!formRef.value.checkValidity()) {
    console.log('Nope!');
    return;
  }

  await nextStep();
};

</script>

<template>
  <div class="flex w-full max-w-sm flex-col gap-4">
    <form ref="formRef" class="flex flex-col" autocomplete="off" autofocus>
      <text-input name="full-name" v-model="fullName" required>Full Name</text-input>
      <text-input name="username" v-model="username" required>Username</text-input>
      <select-input name="timezone" :options="timezoneOptions" v-model="timezone" required>Timezone</select-input>
    </form>
  </div>
  <div class="absolute bottom-[5.75rem] flex w-full justify-end gap-4">
    <primary-button
      class="btn-continue"
      title="Continue"
      v-if="hasNextStep"
      @click="onSubmit()"
    >Continue</primary-button>
  </div>
</template>

<style scoped>
form {
  gap: 1.875rem;
}
</style>
