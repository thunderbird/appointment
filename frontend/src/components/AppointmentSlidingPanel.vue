<script setup lang="ts">
import { BookingStatus } from '@/definitions';
import { timeFormat } from '@/utils';
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import SlidingPanel from '@/elements/SlidingPanel.vue';
import {
  IconCalendar,
  IconCalendarEvent,
  IconClock,
  IconNotes,
  IconUsers,
  IconVideo,
} from '@tabler/icons-vue';
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

// attendees list
const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));

// Handle open state for v-model
const isOpen = computed({
  get: () => props.open && props.appointment !== null,
  set: (value) => {
    if (!value) {
      emit('close');
    }
  }
});

// calculate initials
const initials = (name: string) => name.split(' ').map((p) => p[0]).join('');

const confirmationUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/1`);
const denyUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/0`);
const status = computed(() => props.appointment?.slots[0].booking_status);
const isExpired = computed(() => {
  return props.appointment?.slots.reduce((p, c) => dj.max(p, dj(c.start).add(c.duration, 'minutes')), dj('1970-01-01')) < dj();
});
const isPast = computed(() => props.appointment?.slots[0].start < dj());

// Handle decision
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
      <p class="mb-8 font-semibold">
        {{ status }}
      </p>

      <div class="mb-8 grid w-max max-w-full grid-cols-4 gap-x-4 gap-y-2 pl-4 text-sm">
        <div class="flex items-center gap-2 font-semibold">
          <icon-calendar-event class="size-4 fill-transparent stroke-gray-500 stroke-2"/>
          {{ t('label.availabilityDay') }}
        </div>
        <div class="flex items-center gap-2 font-semibold">
          <icon-clock class="size-4 fill-transparent stroke-gray-500 stroke-2"/>
          {{ t('label.startTime') }}
        </div>
        <div class="flex items-center gap-2 font-semibold">
          <icon-clock class="size-4 fill-transparent stroke-gray-500 stroke-2"/>
          {{ t('label.endTime') }}
        </div>
        <div class="flex items-center gap-2 font-semibold">
          <icon-users class="size-4 fill-transparent stroke-gray-500 stroke-2"/>
          {{ t('label.bookings') }}
        </div>
        <template v-for="s in appointment.slots" :key="s.start">
          <div class="pl-6">{{ dj(s.start).format('LL') }}</div>
          <div class="pl-6">{{ dj(s.start).format(timeFormat()) }}</div>
          <div class="pl-6">{{ dj(s.start).add(s.duration, 'minutes').format(timeFormat()) }}</div>
          <div class="pl-6">{{ s.attendee?.email ?? '&mdash;' }}</div>
        </template>
      </div>
      <div class="mb-8 grid w-max max-w-full grid-cols-3 gap-x-12 gap-y-8 pl-4 text-sm">
        <div>
          <div class="mb-1 flex items-center gap-2 font-semibold">
            <icon-calendar class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
            {{ t('label.calendar') }}
          </div>
          <div class="flex items-center gap-3 pl-6">
            <div
              class="size-4 shrink-0 rounded-full bg-sky-400"
              :style="{ backgroundColor: appointment.calendar_color }"
            ></div>
            {{ appointment.calendar_title }}
          </div>
        </div>
        <div>
          <div class="mb-1 flex items-center gap-2 font-semibold">
            <icon-video class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
            {{ t('label.videoLink') }}
          </div>
          <div class="pl-6">
            <a
              v-if="appointment.location_url"
              :href="appointment.location_url"
              class="text-teal-500 underline underline-offset-2"
              target="_blank"
            >
              {{ appointment.location_url }}
            </a>
            <p v-else>
              {{ t('label.notProvided') }}
            </p>
          </div>
        </div>
      </div>
      <div
        v-if="attendeesSlots.length > 0"
        class="mb-8 grid w-max max-w-full grid-cols-[auto_1fr] items-center gap-x-8 gap-y-2 pl-4 text-sm"
      >
        <div class="mb-1 flex items-center gap-2 font-semibold">
          <icon-users class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
          {{ t('label.attendees') }}
        </div>
        <div class="mb-1 flex items-center gap-2 font-semibold">
          <icon-calendar-event class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
          {{ t('label.bookingSlot') }}
        </div>
        <template v-for="s in attendeesSlots" :key="s.start">
          <div class="flex items-center gap-2 pl-6">
            <div class="relative size-6 rounded-full bg-teal-500">
              <div class="position-center absolute text-xs text-white">{{ initials(s.attendee.name) }}</div>
            </div>
            {{ s.attendee.email }}
          </div>
          <div class="flex gap-4 pl-6">
            <div>{{ dj(s.start).format('LL') }}</div>
            <div>{{ dj(s.start).format(timeFormat()) }}</div>
            <div>{{ t('label.to') }}</div>
            <div>{{ dj(s.start).add(s.duration, 'minutes').format(timeFormat()) }}</div>
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
      <div class="px-4" v-if="status === BookingStatus.Booked">
        <p class="mb-8">This booking is confirmed.</p>
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
      <div class="p-6" v-else-if="isExpired">
        <p>This booking is expired.</p>
      </div>
      <div class="p-6" v-else-if="status === BookingStatus.Requested">
        <p>{{ attendeesSlots.map((s) => s.attendee.email).join(', ') }} have requested a booking at this time.</p>
      </div>
    </div>

    <!-- CTA buttons in the panel's CTA slot -->
    <template #cta>
      <div v-if="status === BookingStatus.Booked && !isPast" class="flex justify-center">
        <danger-button 
          data-testid="appointment-modal-cancel-btn" 
          @click="cancelAppointment()" 
          :title="t('label.cancel')"
        >
          {{ t('label.cancelBooking') }}
        </danger-button>
      </div>
      <div v-else-if="isExpired" class="flex justify-center">
        <danger-button 
          class="btn-deny" 
          @click="deleteAppointment()" 
          :title="t('label.delete')"
        >
          {{ t('label.deleteBooking') }}
        </danger-button>
      </div>
      <div v-else-if="status === BookingStatus.Requested" class="flex justify-center gap-4">
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