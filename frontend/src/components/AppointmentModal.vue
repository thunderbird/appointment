<script setup lang="ts">
import { BookingStatus } from '@/definitions';
import { timeFormat } from '@/utils';
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';

// icons
import {
  IconCalendar,
  IconCalendarEvent,
  IconClock,
  IconNotes,
  IconUsers,
  IconVideo,
  IconX,
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
  open: boolean, // modal state
  appointment?: Appointment; // appointment data to display
}
const props = defineProps<Props>();

const cancelReason = ref<string>("");

// attendees list
const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));

// calculate initials
const initials = (name: string) => name.split(' ').map((p) => p[0]).join('');

const confirmationUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/1`);
const denyUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/0`);

const status = computed(() => props.appointment?.slots[0].booking_status);
const isExpired = computed(() => {
  return props.appointment?.slots.reduce((p, c) => dj.max(p, dj(c.start).add(c.duration, 'minutes')), dj('1970-01-01')) < dj();
});

// Handle decision
const answer = (isConfirmed: boolean) => {
  window.location.href = isConfirmed ? confirmationUrl.value : denyUrl.value;
};

// Handle deletion
const deleteAppointment = () => {
  apmtStore.deleteAppointment(props.appointment?.id);
  emit('close');
};

// Handle cancel
const cancelAppointment = () => {
  apmtStore.cancelAppointment(props.appointment?.id, cancelReason.value);
  cancelReason.value = "";
  emit('close');
};
</script>

<template>
  <transition>
    <div
      v-show="open"
      class="mdl-overlay-close fixed left-0 top-0 z-40 h-screen w-screen bg-gray-800/50"
      @click="emit('close')"
    ></div>
  </transition>
  <transition>
    <div
      v-if="open"
      class="
        position-center fixed z-50 w-full max-w-4xl rounded-xl bg-white
        p-12 text-gray-500 dark:bg-gray-700 dark:text-gray-300
      "
    >
      <div class="btn-close absolute right-8 top-8 cursor-pointer" @click="emit('close')" :title="t('label.close')">
        <icon-x class="size-6 fill-transparent stroke-gray-700 stroke-1 dark:stroke-gray-400"/>
      </div>
      <div class="mb-8 truncate text-xl">{{ appointment.title }}</div>
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
        <form class="gap-4" @submit.prevent>
          <label for="cancelReason">
            {{ t("label.cancelReason") }}
            <textarea
                name="cancelReason"
                v-model="cancelReason"
                :placeholder="t('placeholder.writeHere')"
                class="w-full h-24 rounded-md resize-none mt-2 mb-8"
                data-testid="appointment-modal-reason-input"
              ></textarea>
          </label>
          <danger-button data-testid="appointment-modal-cancel-btn" @click="cancelAppointment()" :title="t('label.cancel')" class="mx-auto">
            {{ t('label.cancelBooking') }}
          </danger-button>
        </form>
      </div>
      <div class="p-6" v-else-if="isExpired">
        <p>This booking is expired.</p>
        <div class="mt-4 flex justify-center gap-4">
          <danger-button class="btn-deny" @click="deleteAppointment()" :title="t('label.delete')">
            {{ t('label.deleteBooking') }}
          </danger-button>
        </div>
      </div>
      <div class="p-6" v-else-if="status === BookingStatus.Requested">
        <p>{{ attendeesSlots.map((s) => s.attendee.email).join(', ') }} have requested a booking at this time.</p>
        <div class="mt-4 flex justify-center gap-4">
          <primary-button class="btn-confirm" @click="answer(true)" :title="t('label.confirm')">
            {{ t('label.confirmBooking') }}
          </primary-button>
          <danger-button class="btn-deny" @click="answer(false)" :title="t('label.deny')">
            {{ t('label.denyBooking') }}
          </danger-button>
        </div>
      </div>
    </div>
  </transition>
</template>
