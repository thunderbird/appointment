<script setup lang="ts">
import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { BaseBadge, BaseBadgeTypes } from '@thunderbirdops/services-ui';

const { t } = useI18n();
const dj = inject(dayjsKey);

defineProps<{
  name: string;
  email: string;
  startTime: string;
  duration: number;
  needsConfirmation: boolean;
}>();
</script>

<template>
  <div class="appointment-item">
    <div>
      <strong>{{ name }}</strong>
      <p>{{ email }}</p>
    </div>

    <div class="time-range">
      <span>{{ dj(startTime).format('LT') }}</span> - <span>{{ dj(startTime).add(duration, 'minutes').format('LT') }}</span>
    </div>

    <base-badge class="badge" :type="BaseBadgeTypes.NotSet" v-if="needsConfirmation">
      {{ t('label.needsConfirmation') }}
    </base-badge>
  </div>
</template>

<style scoped>
.appointment-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: center;
  justify-content: space-between;
  background-color: var(--colour-neutral-lower);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;

  strong {
    font-weight: 600;
    font-size: 1rem;
  }

  .time-range {
    justify-self: center;
  }

  .badge {
    justify-self: flex-end;
  }
}
</style>