<!-- This is currently (as of Jul-25-2025) being scoped so this component is unused
Do not delete though! It will be useful once this ticket is tackled:
https://github.com/thunderbird/appointment/issues/1146 -->
<!-- Also during a revamp of the calendar implementation (Sep-17-2025), the calendar-mini-month component
was removed and might be re-implemented if needed in the future. -->

<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Appointment, SelectOption } from '@/models';
import { dayjsKey } from '@/keys';
import { timeFormat } from '@/utils';
import { PrimaryButton, SelectInput } from '@thunderbirdops/services-ui';
import { useAppointmentStore } from '@/stores/appointment-store';
import { useUserStore } from '@/stores/user-store';

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
const user = useUserStore();
const appointmentStore = useAppointmentStore();

const form = ref<ModifyFormData>({ ...props.initialData });
const isSuccess = ref<boolean>(false);
const isError = ref<boolean>(false);

const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));

const handleTryAgainClicked = () => {
  isSuccess.value = false;
  isError.value = false;
  emit('update:hideModifyFieldsAndCTA', false);
}

const handleModifyFormSubmit = async () => {
  try {
    emit('update:hideModifyFieldsAndCTA', true);

    const slotTimeInUTC = dj(selectedBookingSlot.value)
      .tz(user.data.settings.timezone ?? dj.tz.guess(), true)
      .utc().format()

    const payload = {
      appointmentId: props.appointment?.id,
      title: props.title,
      start: slotTimeInUTC,
      slotId: props.appointment?.slots[0].id,
      notes: form.value.notes,
    };

    const { error } = await appointmentStore.modifyBookingAppointment(payload);

    if (error.value) {
      isError.value = true;
      return;
    }

    isError.value = false;
    isSuccess.value = true;

    // Close panel automatically after 7 seconds
    setTimeout(() => {
      emit('close');
    }, 7000);
  } catch (error) {
    console.error('Failed to update appointment:', error);
  }
}

// Mini calendar refs and functions
const activeDate = ref(dj(props.appointment?.slots[0].start));

const populateTimeSlots = async () => {
  isLoadingSlots.value = true;

  const { data, error } = await appointmentStore.fetchAvailabilityForDay(activeDate.value.format('YYYY-MM-DD'));

  if (error.value) {
    console.error('Failed to fetch available slots:', error.value);

    isError.value = true;
    emit('update:hideModifyFieldsAndCTA', true);

    return;
  }

  isLoadingSlots.value = false;
  availableSlots.value = data.value;

  // If no available slots are returned, pre-select the "No bookings available" option
  // otherwise, pre-select the first available slot
  if (!availableSlots.value.length) {
    selectedBookingSlot.value = null
  } else {
    selectedBookingSlot.value = availableSlots.value[0].start
  }
}

// Booking slot refs and functions
const isLoadingSlots = ref<boolean>(false);
const availableSlots = ref([]);
const selectedBookingSlot = ref<string>();
const earliestOptions = computed<SelectOption[]>(() => {
  if (!availableSlots.value || availableSlots.value.length === 0) {
    return [{ label: t('label.noSlotsAvailable'), value: null }];
  }

  // Note that the label shows the time formatted as 9:00 AM
  // but the underlying value will be 2025-07-29T09:00:00-06:00
  return availableSlots.value.map((slot) => ({
    label: dj(slot.start).format(timeFormat()),
    value: slot.start,
  }));
});

onMounted(async () => {
  await populateTimeSlots();
})

defineExpose({
  handleModifyFormSubmit
});
</script>

<template>
  <!-- Default state -->
  <template v-if="!isError && !isSuccess">
    <div class="appointment-content">
      <div class="calendar-booking-slot-container">
        <div class="booking-slot-container">
          <label class="booking-slot-label" for="bookingSlotSelect">{{ t('label.bookingSlot') }}</label>
          <select-input
            name="bookingSlotSelect"
            v-model="selectedBookingSlot"
            data-testid="dashboard-scheduling-details-earliest-booking-input"
            :options="earliestOptions"
            :disabled="isLoadingSlots || availableSlots.length === 0"
          />
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
  
      <form id="appointment-modify-form" class="notes-form" @submit.prevent="handleModifyFormSubmit">
        <label for="notes" class="notes-label">
          {{ t('label.notes') }}
          <textarea name="notes" v-model="form.notes"
            :placeholder="t('placeholder.bookingNotesPlaceholder')" class="notes-textarea"
            data-testid="appointment-modal-modify-notes-input">
          </textarea>
        </label>
      </form>
    </div>
  </template>

  <!-- Error state -->
  <template v-else-if="isError">
    <div class="confirmation-container">
      <div class="confirmation-header">
        <h2 class="confirmation-title error">{{ t('info.bookingModifiedFailed') }}</h2>
        <p class="confirmation-text">{{ t('info.bookingModifiedError') }}</p>
      </div>
      <div class="confirmation-button-container">
        <primary-button
          variant="outline"
          data-testid="appointment-modal-modify-close-btn"
          @click="emit('close')"
          :title="t('label.close')"
        >
          {{ t('label.close') }}
        </primary-button>
        <primary-button
          data-testid="appointment-modal-modify-try-again-btn"
          @click="handleTryAgainClicked()"
          :title="t('label.tryAgain')"
        >
        {{ t('label.tryAgain') }}
        </primary-button>
      </div>
    </div>
  </template>
  
  <!-- Success state -->
  <template v-else-if="isSuccess">
    <div class="confirmation-container">
      <div class="confirmation-header">
        <h2 class="confirmation-title">{{ t('info.bookingModified') }}</h2>
        <p class="confirmation-text">{{ t('info.bookingModifiedSuccess') }}</p>
      </div>
      <primary-button
        variant="outline"
        data-testid="appointment-modal-modify-close-btn"
        @click="emit('close')"
        :title="t('label.close')"
      >
        {{ t('label.close') }}
      </primary-button>
    </div>
  </template>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.appointment-content {
  color: var(--colour-ti-base);
}

.calendar-booking-slot-container {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 1.5rem;

  .calendar {
    width: 100%;
  }

  .booking-slot-container {
    width: 100%;

    .booking-slot-label {
      display: block;
      margin: 0.2rem 0 0.5rem 0;
    }
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

  &.error {
    color: var(--colour-ti-critical);
  }
}

.confirmation-button-container {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;

  button {
    width: 100%;
  }

  @media (--sm) {
    button {
      width: auto;
    }
  }
}

.confirmation-text {
  font-size: 1rem;
  color: var(--colour-ti-base);
}
</style>
