<script setup lang="ts">
import { inject, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { SelectOption } from '@/models';
import { useAvailabilityStore } from '@/stores/availability-store';

import RadioGroupPill from '../../RadioGroupPill.vue';

const { t } = useI18n();
const dj = inject(dayjsKey);

const availabilityStore = useAvailabilityStore();
const { currentState } = storeToRefs(availabilityStore);

const bookingWindow = computed({
  get: () => currentState.value.farthest_booking,
  set: (value) => {
    availabilityStore.$patch({ currentState: { farthest_booking: value }})
  }
})

const bookingWindowOptions: SelectOption[] = [1, 2, 3, 4].map((d) => ({
  label: dj.duration(d, 'weeks').humanize(),
  value: (d * 60 * 24 * 7),
}));
</script>

<template>
  <radio-group-pill
    v-model="bookingWindow"
    name="booking-window"
    :legend="t('label.bookingWindow')"
    :options="bookingWindowOptions"
    :disabled="!currentState.active"
  />
</template>