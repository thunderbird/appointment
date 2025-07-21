<script setup lang="ts">
import { computed, inject } from 'vue';
import { timeFormat } from '@/utils';
import { IconCalendarEvent, IconNotes } from '@tabler/icons-vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import { dayjsKey } from '@/keys';
import { BookingStatus } from '@/definitions';

interface Props {
  appointment: Appointment | null;
  cancelReason: string;
}
const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:cancelReason', value: string): void;
}>();

const dj = inject(dayjsKey);
const { t } = useI18n();

const status = computed(() => props.appointment?.slots[0].booking_status);
const isPast = computed(() => props.appointment?.slots[0].start < dj());
const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));
const bookingStatusInfo = computed(() => {
  if (status.value === BookingStatus.Booked && !isPast.value) {
    return {
      label: t('label.confirmed'),
      color: 'status-confirmed'
    };
  }

  return {
    label: t('label.unconfirmed'),
    color: 'status-unconfirmed'
  };
});
</script>

<template>
  <div class="appointment-content">
    <!-- Appointment status, first focusable content for back-to-top screen reader button -->
    <p :class="['status-label', bookingStatusInfo.color]" tabindex="-1">
      {{ bookingStatusInfo.label }}
    </p>

    <div class="time-slots">
      <template v-for="s in appointment.slots" :key="s.start">
        <div class="time-slot">
          <icon-calendar-event class="time-icon" :aria-label="t('label.timeOfTheEvent')" />
          <div class="time-details">
            <p class="date">{{ dj(s.start).format('LL') }}</p>
            <div class="time-range">
              {{ dj(s.start).format(timeFormat()) }} - {{ dj(s.start).add(s.duration, 'minutes').format(timeFormat()) }}
              ({{ dj.duration(s.duration, 'minutes').humanize() }})
            </div>
          </div>
        </div>
      </template>
    </div>

    <div class="appointment-info">
      <div class="info-row">
        <span class="info-label">
          {{ t('label.calendar') }}:
        </span>
        {{ appointment.calendar_title }}
      </div>
      <div class="info-row">
        <div class="info-row">
          <span class="info-label">
            {{ t('label.videoLink') }}:
          </span>
          <a v-if="appointment.location_url" :href="appointment.location_url" class="video-link" target="_blank">
            {{ appointment.location_url }}
          </a>
          <span v-else>
            {{ t('label.notProvided') }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="attendeesSlots.length > 0" class="attendees-section">
      <div class="attendees-header">
        {{ t('label.attendees') }}:
      </div>
      <template v-for="s in attendeesSlots" :key="s.start">
        <div class="attendee-item">
          {{ s.attendee.email }}
        </div>
      </template>
    </div>

    <div v-if="appointment.details" class="notes-section">
      <div class="notes-header">
        <icon-notes class="notes-icon" />
        {{ t('label.notes') }}
      </div>
      <div class="notes-content">{{ appointment.details }}</div>
    </div>

    <div v-if="status === BookingStatus.Booked">
      <form v-if="!isPast" class="cancel-form" @submit.prevent>
        <label for="cancelReason" class="cancel-label">
          {{ t('label.cancelReason') }}
          <textarea 
            name="cancelReason" 
            :value="cancelReason"
            @input="emit('update:cancelReason', ($event.target as HTMLTextAreaElement).value)"
            :placeholder="t('placeholder.writeHere')"
            class="cancel-textarea" 
            data-testid="appointment-modal-cancel-reason-input">
          </textarea>
        </label>
      </form>
    </div>
  </div>
</template>

<style scoped>
.appointment-content {
  color: var(--colour-ti-base);
}

/* Status labels */
.status-label {
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-confirmed {
  color: var(--colour-ti-success);
}

.status-requested {
  color: var(--colour-ti-warning);
}

.status-unconfirmed {
  color: var(--colour-ti-critical);
}

/* Status labels */
.status-label {
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-confirmed {
  color: var(--colour-ti-success);
}

.status-requested {
  color: var(--colour-ti-warning);
}

.status-unconfirmed {
  color: var(--colour-ti-critical);
}

/* Time slots section */
.time-slots {
  margin-bottom: 1.5rem;
  width: max-content;
  max-width: 100%;
  font-size: 0.875rem;
}

.time-slot {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.time-icon {
  width: 2rem;
  height: 2rem;
  fill: transparent;
  stroke: var(--colour-ti-muted);
  stroke-width: 2;
}

.time-details .date {
  margin: 0;
}

.time-range {
  margin-top: 0.25rem;
}

/* Appointment info section */
.appointment-info {
  margin-bottom: 1.5rem;
  width: max-content;
  max-width: 100%;
  font-size: 0.875rem;
}

.info-row {
  margin-bottom: 0.25rem;
}

.info-label {
  font-weight: 600;
}

.video-link {
  color: var(--colour-accent-teal);
  text-decoration: underline;
  text-underline-offset: 2px;

  &:hover {
    color: var(--colour-apmt-primary);
  }
}

/* Attendees section */
.attendees-section {
  margin-bottom: 1.5rem;
  width: max-content;
  max-width: 100%;
  font-size: 0.875rem;
}

.attendees-header {
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.attendee-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Notes section */
.notes-section {
  width: 100%;
  padding-left: 1rem;
  font-size: 0.875rem;
}

.notes-header {
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.notes-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  fill: transparent;
  stroke: var(--colour-ti-muted);
  stroke-width: 2;
}

.notes-content {
  border-radius: 0.5rem;
  border: 1px solid var(--colour-neutral-border);
  padding: 1rem;
}

.dark .notes-content {
  border-color: var(--colour-neutral-border);
}

/* Cancel form */
.cancel-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cancel-label {
  display: block;
}

.cancel-textarea {
  width: 100%;
  height: 6rem;
  margin-top: 0.5rem;
  margin-bottom: 2rem;
  border-radius: 0.375rem;
  resize: none;
  border: 1px solid var(--colour-neutral-border);
  padding: 0.5rem;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: var(--colour-primary-default);
    box-shadow: 0 0 0 3px var(--colour-primary-soft);
  }
}

.dark .cancel-textarea {
  border-color: var(--colour-neutral-border);
  background-color: var(--colour-neutral-lower);
  color: var(--colour-ti-base);
}
</style>