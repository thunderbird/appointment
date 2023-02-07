<template>
  <div v-if="open" class="bg-gray-800/50 w-screen h-screen fixed top-0 left-0 z-40" @click="emit('close')"></div>
  <div v-if="open" class="bg-white fixed z-50 position-center position-center rounded-xl p-12 max-w-lg w-full">
    <div class="absolute top-8 right-8 cursor-pointer" @click="emit('close')">
      <x-icon class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
    </div>
    <div class="text-xl text-teal-500 text-center font-semibold mb-4">
      {{ !bookingDone ? t('heading.bookSelection') : t('heading.eventBooked') }}
    </div>
    <div class="text-gray-500 text-center mb-4">
      <div>{{ event.title }}:</div>
      <div>{{ time }}</div>
    </div>
    <div v-if="!bookingDone" class="text-xs text-teal-500 text-center underline mb-8">Time zone: Pacific Standart Time</div>
    <div v-if="!bookingDone" class="flex flex-col gap-4 mb-8">
      <label>
        <div class="font-medium text-gray-500 mb-1">{{ t('label.name') }}</div>
        <input
          type="text"
          v-model="attendee.name"
          :placeholder="t('placeholder.firstAndLastName')"
          class="rounded-md bg-gray-50 border-gray-200 w-full"
        />
      </label>
      <label>
        <div class="font-medium text-gray-500 mb-1">{{ t('label.email') }} <span class="text-red-600">*</span></div>
        <input
          type="text"
          v-model="attendee.email"
          :placeholder="t('placeholder.emailAddress')"
          class="rounded-md bg-gray-50 border-gray-200 w-full"
          required
        />
      </label>
    </div>
    <div v-else class="mb-8 mt-8">
      <art-confetti class="h-52 w-52 stroke-none fill-transparent mb-8 mx-auto" />
      <div class="text-xs text-gray-500 w-4/5 mx-auto text-center">{{ t('text.invitationSentToAddress', { address: attendee.email }) }}</div>
    </div>
    <div class="flex gap-8 w-4/5 mx-auto justify-center items-stretch">
      <secondary-button
        :label="t('label.close')"
        @click="emit('close')"
      />
      <primary-button
        v-if="!bookingDone"
        :label="t('label.bookEvent')"
        :disabled="!validAttendee"
        @click="bookIt"
      />
      <primary-button
        v-else
        :label="t('label.downloadIcs')"
        @click="downloadIcs"
      />
    </div>
  </div>
</template>

<script setup>
import { inject, computed, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import ArtConfetti from '@/elements/arts/ArtConfetti';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';

// icons
import { XIcon } from "vue-tabler-icons";

// component constants
const { t } = useI18n();
const dj = inject("dayjs");

// component properties
const props = defineProps({
  open: Boolean, // modal state
  event: Object  // event data to display and book
});

// format time
const time = computed(() => {
  return dj(props.event.start).format('LLLL')
});

// attendee data
const attendee = reactive({
  name: '',
  email: '',
});
const validAttendee = computed(() => {
  return attendee.email.length > 2;
});

// actual booking
const bookingDone = ref(false);
const bookIt = () => {
  if (validAttendee.value) {
    emit('booked', attendee);
  }
  bookingDone.value = true;
};

// download calendar event as .ics
const downloadIcs = () => {
  // TODO: create ICS file
  console.log(props.event);
};

// component emits
const emit = defineEmits(['booked', 'close']);
</script>
