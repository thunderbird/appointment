<template>
  <div v-if="open" class="bg-gray-800/50 w-screen h-screen fixed top-0 left-0 z-40" @click="emit('close')"></div>
  <div v-if="open" class="bg-white fixed z-50 position-center position-center rounded-xl p-12 max-w-lg w-full">
    <div class="absolute top-8 right-8 cursor-pointer" @click="emit('close')">
      <icon-x class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
    </div>
    <div class="text-2xl text-teal-500 text-center font-semibold mb-4">
      {{ !success ? t('heading.bookSelection') : t('heading.eventBooked') }}
    </div>
    <div class="text-gray-500 text-center mb-4">
      <div>{{ event.title }}:</div>
      <div>{{ time }}</div>
    </div>
    <div v-if="!success" class="text-sm text-teal-500 text-center underline underline-offset-2 mb-8">
      Time zone: Pacific Standart Time
    </div>
    <form v-if="!success" ref="bookingForm" class="flex flex-col gap-4 mb-8">
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
        <div class="font-medium text-gray-500 mb-1">
          {{ t('label.email') }} <span class="text-red-600">*</span>
        </div>
        <input
          type="email"
          v-model="attendee.email"
          :placeholder="t('placeholder.emailAddress')"
          class="rounded-md bg-gray-50 border-gray-200 w-full"
          required
        />
      </label>
    </form>
    <div v-else class="mb-8 mt-8">
      <art-confetti class="h-52 w-52 stroke-none fill-transparent mb-8 mx-auto" />
      <div class="text-sm text-gray-500 w-4/5 mx-auto text-center">
        {{ t('text.invitationSentToAddress', { address: attendee.email }) }}
      </div>
    </div>
    <div class="flex gap-8 w-4/5 mx-auto justify-center items-stretch">
      <secondary-button
        :label="t('label.close')"
        @click="emit('close')"
      />
      <primary-button
        v-if="!success"
        :label="t('label.bookEvent')"
        :waiting="waiting"
        :disabled="!validAttendee || waiting"
        @click="bookIt"
      />
      <primary-button
        v-else
        :label="t('label.downloadInvitation')"
        @click="emit('download')"
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
import { IconX } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const dj = inject('dayjs');

// component properties
const props = defineProps({
  open: Boolean,    // modal state
  event: Object,    // event data to display and book
  success: Boolean, // true if booking was successful
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

// actual event booking
const bookingForm = ref();
const bookingDone = ref(false);
const bookIt = () => {
  if (bookingForm.value.reportValidity() && validAttendee.value) {
    emit('book', attendee);
    bookingDone.value = true;
  }
};

// loading indication
const waiting = computed(() => bookingDone.value && !props.success);

// component emits
const emit = defineEmits(['book', 'download', 'close']);
</script>
