<script setup lang="ts">
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { BaseBadge, BaseBadgeTypes } from '@thunderbirdops/services-ui';
import type { Appointment } from '@/models';
import { isUnconfirmed } from '@/utils';

const { t } = useI18n();
const dj = inject(dayjsKey);

const props = defineProps<{ appointment: Appointment }>();

const appointmentItem = computed(() => {
  return {
    name: props.appointment.slots[0].attendee.name,
    email: props.appointment.slots[0].attendee.email,
    startTime: props.appointment.slots[0].start,
    duration: props.appointment.slots[0].duration,
    needsConfirmation: isUnconfirmed(props.appointment),
  }
})

const emit = defineEmits(['select-appointment']);
</script>

<template>
  <button class="appointment-item" @click="emit('select-appointment', appointment)">
    <div class="user-info">
      <strong>{{ appointmentItem.name }}</strong>
      <p>{{ appointmentItem.email }}</p>
    </div>

    <div class="time-range">
      <span>{{ dj(appointmentItem.startTime).format('LT') }}</span> - <span>{{ dj(appointmentItem.startTime).add(appointmentItem.duration, 'minutes').format('LT') }}</span>
    </div>

    <div class="badge-column">
      <base-badge v-if="appointmentItem.needsConfirmation" :type="BaseBadgeTypes.NotSet">
        {{ t('label.needsConfirmation') }}
      </base-badge>
    </div>
  </button>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.appointment-item {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
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
}

@media (--md) {
  .appointment-item {
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0;
  }

  .user-info {
    text-align: left;
  }

  .time-range {
    justify-self: center;
  }

  .badge-column {
    justify-self: flex-end;
  }
}
</style>
