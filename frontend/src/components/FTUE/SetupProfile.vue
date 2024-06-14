<script setup>

import TextInput from '@/components/inputs/TextInput.vue';
import SelectInput from '@/components/inputs/SelectInput.vue';
import { inject } from 'vue';

const dj = inject('dayjs');

const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

const timezone = dj.tz.guess();
</script>

<template>
  <div class="flex w-full max-w-sm flex-col gap-8">
    <TextInput name="full-name">Full Name</TextInput>
    <TextInput name="username">Username</TextInput>
    <SelectInput name="timezone" :options="timezoneOptions" :model-value="timezone">Timezone</SelectInput>
  </div>
</template>

<style scoped>

</style>
