<script setup lang="ts">
import { BookingStatus } from '@/definitions';
import { timeFormat } from '@/utils';
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import SlidingPanel from '@/elements/SlidingPanel.vue';
import { IconCalendarEvent, IconNotes } from '@tabler/icons-vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import DangerButton from '@/tbpro/elements/DangerButton.vue';
import { useUserStore } from '@/stores/user-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey } from '@/keys';

const user = useUserStore();
const apmtStore = useAppointmentStore();

// component emits
const emit = defineEmits(['close']);

// component constants
const { t } = useI18n();
const dj = inject(dayjsKey);

// component properties
interface Props {
  appointment: Appointment | null; // appointment data to display
  open: boolean; // panel visibility
}
const props = defineProps<Props>();

const cancelReason = ref<string>('');

const isOpen = computed({
  get: () => props.open && props.appointment !== null,
  set: (value) => {
    if (!value) {
      emit('close');
    }
  }
});
const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));
const confirmationUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/1`);
const denyUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/0`);
const status = computed(() => props.appointment?.slots[0].booking_status);
const isExpired = computed(() => {
  return props.appointment?.slots.reduce((p, c) => dj.max(p, dj(c.start).add(c.duration, 'minutes')), dj('1970-01-01')) < dj();
});
const isPast = computed(() => props.appointment?.slots[0].start < dj());
const bookingStatusLabel = computed(() => {
  if (status.value === BookingStatus.Booked && !isPast.value) {
    return t('label.confirmed');
  }

  if (status.value === BookingStatus.Requested) {
    return t('label.requested');
  }

  return t('label.unconfirmed');
});

const answer = (isConfirmed: boolean) => {
  window.location.href = isConfirmed ? confirmationUrl.value : denyUrl.value;
};

const deleteAppointment = () => {
  apmtStore.deleteAppointment(props.appointment?.id);
  emit('close');
};

const cancelAppointment = () => {
  apmtStore.cancelAppointment(props.appointment?.id, cancelReason.value);
  cancelReason.value = '';
  emit('close');
};
</script>

<template>
  <sliding-panel
    v-model:open="isOpen"
    :title="appointment?.title"
    @close="emit('close')"
  >
    <div v-if="appointment" class="appointment-content">
      <!-- Appointment status -->
      <p class="mb-6 font-semibold uppercase">
        {{ bookingStatusLabel }}
      </p>

      <div class="mb-6 w-max max-w-full text-sm">
        <template v-for="s in appointment.slots" :key="s.start">
          <div class="flex items-center gap-2 font-semibold">
            <icon-calendar-event class="size-8 fill-transparent stroke-gray-500 stroke-2"/>
            <div>
              <p>{{ dj(s.start).format('LL') }}</p>
              <div>
                {{ dj(s.start).format(timeFormat()) }} - {{ dj(s.start).add(s.duration, 'minutes').format(timeFormat()) }} ({{ dj.duration(s.duration, 'minutes').humanize() }})
              </div>
            </div>
          </div>
        </template>
      </div>
      <div class="mb-6 w-max max-w-full text-sm">
        <div class="mb-1">
          <span class="font-semibold">
            {{ t('label.calendar') }}:
          </span>
          {{ appointment.calendar_title }}
        </div>
        <div>
          <div class="mb-1">
            <span class="font-semibold">
              {{ t('label.videoLink') }}:
            </span>
            <a
              v-if="appointment.location_url"
              :href="appointment.location_url"
              class="text-teal-500 underline underline-offset-2"
              target="_blank"
            >
              {{ appointment.location_url }}
            </a>
            <span v-else>
              {{ t('label.notProvided') }}
            </span>
          </div>
        </div>
      </div>
      <div
        v-if="attendeesSlots.length > 0"
        class="mb-6 w-max max-w-full text-sm"
      >
        <div class="mb-1 flex items-center gap-2 font-semibold">
          {{ t('label.attendees') }}:
        </div>
        <template v-for="s in attendeesSlots" :key="s.start">
          <div class="flex items-center gap-2">
            {{ s.attendee.email }}
          </div>
        </template>
      </div>
      <div v-if="appointment.details" class="w-full pl-4 text-sm">
        <div class="mb-1 flex items-center gap-2 font-semibold">
          <icon-notes class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
          {{ t('label.notes') }}
        </div>
        <div class="rounded-lg border border-gray-400 p-4 dark:border-gray-600">{{ appointment.details }}</div>
      </div>
      <div v-if="status === BookingStatus.Booked">
        <form v-if="!isPast" class="gap-4" @submit.prevent>
          <label for="cancelReason">
            {{ t('label.cancelReason') }}
            <textarea
                name="cancelReason"
                v-model="cancelReason"
                :placeholder="t('placeholder.writeHere')"
                class="w-full h-24 rounded-md resize-none mt-2 mb-8"
                data-testid="appointment-modal-cancel-reason-input"
              ></textarea>
          </label>
        </form>
      </div>
      <div class="p-6" v-else-if="status === BookingStatus.Requested">
        <p>{{ attendeesSlots.map((s) => s.attendee.email).join(', ') }} have requested a booking at this time.</p>
      </div>
    </div>

    <!-- CTA buttons in the panel's CTA slot -->
    <template #cta>
      <div v-if="status === BookingStatus.Booked && !isPast" class="flex justify-end">
        <danger-button 
          data-testid="appointment-modal-cancel-btn" 
          @click="cancelAppointment()" 
          :title="t('label.cancel')"
        >
          {{ t('label.cancelBooking') }}
        </danger-button>
      </div>
      <div v-else-if="isExpired" class="flex justify-end">
        <danger-button 
          class="btn-deny" 
          @click="deleteAppointment()" 
          :title="t('label.delete')"
        >
          {{ t('label.deleteBooking') }}
        </danger-button>
      </div>
      <div v-else-if="status === BookingStatus.Requested" class="flex justify-end gap-4">
        <primary-button 
          class="btn-confirm" 
          @click="answer(true)" 
          :title="t('label.confirm')"
        >
          {{ t('label.confirmBooking') }}
        </primary-button>
        <danger-button 
          class="btn-deny" 
          @click="answer(false)" 
          :title="t('label.deny')"
        >
          {{ t('label.denyBooking') }}
        </danger-button>
      </div>
    </template>
  </sliding-panel>
</template>

<style scoped>
.appointment-content {
  color: #6b7280;
}

.appointment-content :deep(.dark) {
  color: #d1d5db;
}

.position-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style> 