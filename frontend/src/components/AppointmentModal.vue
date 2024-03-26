<template>
  <transition>
    <div v-show="open" class="fixed left-0 top-0 z-40 h-screen w-screen bg-gray-800/50" @click="emit('close')"></div>
  </transition>
  <transition>
    <div
      v-if="open"
      class=" position-center fixed z-50 w-full max-w-3xl rounded-xl bg-white
        p-12 text-gray-500 dark:bg-gray-700 dark:text-gray-300
      "
    >
      <div class="absolute right-8 top-8 cursor-pointer" @click="emit('close')">
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
            <icon-map-pin class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
            {{ t('label.location') }}
          </div>
          <div class="pl-6">{{ t('label.' + keyByValue(locationTypes, appointment.location_type)) }}</div>
        </div>
        <div>
          <div class="mb-1 flex items-center gap-2 font-semibold">
            <icon-video class="size-4 shrink-0 fill-transparent stroke-gray-500 stroke-2"/>
            {{ t('label.videoLink') }}
          </div>
          <div class="pl-6">
            <a :href="appointment.location_url" class="text-teal-500 underline underline-offset-2" target="_blank">
              {{ appointment.location_url }}
            </a>
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
      <div class="p-6" v-if="appointment?.slots[0].booking_status === bookingStatus.requested">
        <p>{{ attendeesSlots.map((s) => s.attendee.email).join(', ') }} have requested a booking at this time.</p>
        <div class="mt-4 flex justify-center gap-4">
          <primary-button @click="answer(true)">Confirm Booking</primary-button>
          <caution-button @click="answer(false)">Deny Booking</caution-button>
        </div>
      </div>
      <div class="p-6" v-if="appointment?.slots[0].booking_status === bookingStatus.booked">
        <p>This booking is confirmed.</p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { bookingStatus, locationTypes } from '@/definitions';
import { keyByValue, timeFormat } from '@/utils';
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';

// icons
import {
  IconCalendar,
  IconCalendarEvent,
  IconClock,
  IconMapPin,
  IconNotes,
  IconUsers,
  IconVideo,
  IconX,
} from '@tabler/icons-vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import CautionButton from '@/elements/CautionButton.vue';
import { useUserStore } from '@/stores/user-store';

const user = useUserStore();

// component constants
const { t } = useI18n();
const dj = inject('dayjs');

// component properties
const props = defineProps({
  open: Boolean, // modal state
  appointment: Object, // appointment data to display
});

// attendees list
const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));

// calculate initials
const initials = (name) => name.split(' ').map((p) => p[0]).join('');

const confirmationUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/1`);
const denyUrl = computed(() => `${user.data.signedUrl}/confirm/${props.appointment.slots[0].id}/${props.appointment.slots[0].booking_tkn}/0`);

const answer = (isConfirmed) => {
  window.location.href = isConfirmed ? confirmationUrl.value : denyUrl.value;
};

// component emits
const emit = defineEmits(['close']);

</script>
