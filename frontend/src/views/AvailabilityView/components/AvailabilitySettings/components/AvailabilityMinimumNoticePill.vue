<script setup lang="ts">
import { inject, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { SelectOption } from '@/models';
import { useAvailabilityStore } from '@/stores/availability-store';
import { SegmentedControl } from '@thunderbirdops/services-ui';

const { t } = useI18n();
const dj = inject(dayjsKey);

const availabilityStore = useAvailabilityStore();
const { currentState } = storeToRefs(availabilityStore);

const minimumNotice = computed({
  get: () => currentState.value.earliest_booking,
  set: (value) => {
    availabilityStore.$patch({ currentState: { earliest_booking: value }})
  }
})

const earliestOptions: SelectOption[] = [0, 0.5, 1, 2, 3, 4, 5].map((d) => {
  // Special case to avoid "in a few seconds"
  if (d === 0) {
    return {
      label: t('label.immediately'),
      value: 0,
    };
  }

  return {
    label: dj.duration(d, 'days').humanize(),
    value: (d * 60 * 24),
  };
});
</script>

<template>
  <segmented-control
    class="minimum-notice-segment-control"
    v-model="minimumNotice"
    name="minimum-notice"
    required
    :legend="t('label.minimumNotice')"
    :options="earliestOptions"
    :disabled="!currentState.active"
  >
    {{ t('label.minimumNotice') }}
  </segmented-control>
</template>
