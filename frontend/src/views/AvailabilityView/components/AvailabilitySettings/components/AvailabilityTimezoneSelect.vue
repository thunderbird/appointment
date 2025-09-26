<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { SelectInput } from '@thunderbirdops/services-ui';
import { useI18n } from 'vue-i18n';
import { useAvailabilityStore } from '@/stores/availability-store';

const { t } = useI18n();
const availabilityStore = useAvailabilityStore();

const { currentState } = storeToRefs(availabilityStore);

// Time Zone
// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone: string) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

const defaultTimeZone = computed({
  get: () => currentState.value.defaultTimeZone,
  set: (value) => {
    availabilityStore.$patch({ currentState: { defaultTimeZone: value }})
  }
})
</script>

<template>
  <select-input
    name="timezone"
    class="select-input"
    :options="timezoneOptions"
    v-model="defaultTimeZone"
    :disabled="!currentState.active"
  >
    {{ t('label.timeZone') }}
  </select-input>
</template>

<style scoped>
.select-input {
  max-width: 388px;
  width: 100%;
}
</style>
