<script setup>

import TextInput from '@/components/inputs/TextInput.vue';
import SelectInput from '@/components/inputs/SelectInput.vue';
import {
  inject, ref,
} from 'vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { storeToRefs } from 'pinia';
import { useFTUEStore } from '@/stores/ftue-store';
import { useUserStore } from '@/stores/user-store';
import InfoBar from '@/elements/InfoBar.vue';

const ftueStore = useFTUEStore();
const dj = inject('dayjs');
const {
  hasNextStep,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;
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
    <InfoBar>
      <p>This is a test error, wooooo!</p>
    </InfoBar>
    <form ref="formRef" class="flex flex-col gap-4" autocomplete="off" autofocus>
      <TextInput name="full-name" v-model="fullName" required>Full Name</TextInput>
      <TextInput name="username" v-model="username" required>Username</TextInput>
      <SelectInput name="timezone" :options="timezoneOptions" v-model="timezone" required>Timezone</SelectInput>
    </form>
  </div>
  <div class="absolute bottom-0 flex gap-4">
    <primary-button
      class="btn-continue"
      label="Continue"
      title="Continue"
      v-if="hasNextStep"
      @click="onSubmit()"
    />
  </div>
</template>
