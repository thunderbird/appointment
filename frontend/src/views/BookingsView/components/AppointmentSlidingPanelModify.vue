<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { timeFormat } from '@/utils';
import { IconCalendarEvent, IconNotes } from '@tabler/icons-vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import { dayjsKey } from '@/keys';
import { BookingStatus } from '@/definitions';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';

export interface ModifyFormData {
  notes: string;
}

const props = defineProps<{
  appointment: Appointment | null;
  initialData: ModifyFormData;
  title: string;
  hideModifyFieldsAndCTA: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'update:hideModifyFieldsAndCTA', value: boolean): void;
}>();

const dj = inject(dayjsKey);
const { t } = useI18n();

const form = ref<ModifyFormData>({ ...props.initialData });
const isSuccess = ref<boolean>(false);
const isError = ref<boolean>(false);

const status = computed(() => props.appointment?.slots[0].booking_status);
const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));
const bookingStatusInfo = computed(() => {
  switch (status.value) {
    case BookingStatus.Booked:
      return {
        label: t('label.confirmed'),
        color: 'status-confirmed'
      }
    case BookingStatus.Declined:
      return {
        label: t('label.declined'),
        color: 'status-unconfirmed'
      }
    case BookingStatus.Cancelled:
      return {
        label: t('label.cancelled'),
        color: 'status-unconfirmed'
      }
    default:
      return {
        label: t('label.unconfirmed'),
        color: 'status-unconfirmed'
      };
  }
});

const handleModifyFormSubmit = async () => {
  try {
    emit('update:hideModifyFieldsAndCTA', true);

    const payload = {
      title: props.title,
      ...form.value,
    };

    // TODO: The updateAppointment action does not exist on the store.
    // It needs to be implemented.
    // await apmtStore.updateAppointment(props.appointment?.id, payload);
    console.log('Submitting from child:', {
      id: props.appointment?.id,
      ...payload,
    })

    isSuccess.value = true;
    // emit('close');
  } catch (error) {
    console.error('Failed to update appointment:', error);
  }
}

defineExpose({
  handleModifyFormSubmit
});
</script>

<template>
  <!-- Default state -->
  <template v-if="!isError && !isSuccess">
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
  
      <div class="attendees-section">
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
  
      <form id="appointment-modify-form" class="notes-form" @submit.prevent="handleModifyFormSubmit">
        <label for="notes" class="notes-label">
          {{ t('label.notes') }}
          <textarea name="notes" v-model="form.notes"
            :placeholder="t('placeholder.bookingNotesPlaceholder')" class="notes-textarea"
            data-testid="appointment-modal-modify-notes-input">
          </textarea>
        </label>
  
        <!-- Future form fields will go here -->
        </form>
    </div>
  </template>

  <!-- Error state -->
  <template v-else-if="isError">
    <div class="error-message">
      {{ t('info.bookingModifiedFailed') }}
    </div>
  </template>
  
  <!-- Success state -->
  <template v-else-if="isSuccess">
    <div class="confirmation-container">
      <div class="confirmation-header">
        <h2 class="confirmation-title">{{ t('info.bookingModified') }}</h2>
        <p class="confirmation-text">{{ t('info.bookingModifiedSuccess') }}</p>
      </div>
      <secondary-button
        data-testid="appointment-modal-modify-close-btn"
        @click="emit('close')"
        :title="t('label.close')"
      >
        {{ t('label.close') }}
      </secondary-button>
    </div>
  </template>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

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

/* Notes form */
.notes-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notes-label {
  display: block;
}

.notes-textarea {
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

.dark .notes-textarea {
  border-color: var(--colour-neutral-border);
  background-color: var(--colour-neutral-lower);
  color: var(--colour-ti-base);
}

/* Confirmation container */
.confirmation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  flex-direction: column;
  gap: 2rem;
  padding: 0 1rem;
  text-align: center;
}

.confirmation-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.confirmation-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--colour-ti-success);
}

.confirmation-text {
  font-size: 1rem;
  color: var(--colour-ti-base);
}
</style>