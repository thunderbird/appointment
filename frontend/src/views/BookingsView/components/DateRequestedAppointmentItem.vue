<script setup lang="ts">
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { BaseBadge, BaseBadgeTypes } from '@thunderbirdops/services-ui';
import type { Appointment } from '@/models';
import { isUnconfirmed } from '@/utils';

const props = defineProps<{
  appointment: Appointment;
}>();

const dj = inject(dayjsKey);
const { t } = useI18n();

const appointmentItem = computed(() => {
  return {
    name: props.appointment.slots[0].attendee.name,
    email: props.appointment.slots[0].attendee.email,
    requestDate: props.appointment.time_created,
    meetingDate: props.appointment.slots[0].start,
    needsConfirmation: isUnconfirmed(props.appointment),
  }
});

const formattedRequestDate = computed(() => dj(appointmentItem.value.requestDate).format('L, LT'));
const formattedMeetingDate = computed(() => dj(appointmentItem.value.meetingDate).format('L, LT'));

const emit = defineEmits(['select-appointment']);
</script>

<template>
  <button class="appointment-item" @click="emit('select-appointment', appointment)">
    <div>
      <strong>{{ appointmentItem.name }}</strong>
      <p>{{ appointmentItem.email }}</p>
    </div>

    <div>
      <p>{{ t('label.requestDate') }}</p>
      <strong>{{ formattedRequestDate }}</strong>
    </div>

    <div>
      <p>{{ t('label.meetingDate') }}</p>
      <strong>{{ formattedMeetingDate }}</strong>
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
  background-color: var(--colour-neutral-lower);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;

  div {
    text-align: center;
  }

  strong {
    font-weight: 600;
    font-size: 1rem;
  }
}

@media (--md) {
  .appointment-item {
    grid-template-columns: 300px 1fr 1fr 1fr;
    gap: 0;

    div {
      text-align: left;
    }
  }

  .badge-column {
    justify-self: flex-end;
  }
}
</style>
