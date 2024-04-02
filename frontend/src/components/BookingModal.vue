<template>
  <div v-if="open">
    <div class="fixed left-0 top-0 z-40 h-screen w-screen bg-gray-800/50" @click="emit('close')"></div>
    <div
      class="position-center fixed z-50 w-full max-w-lg rounded-xl bg-white p-12 dark:bg-gray-700"
    >
      <div class="absolute right-8 top-8 cursor-pointer" @click="emit('close')">
        <icon-x class="size-6 fill-transparent stroke-gray-700 stroke-1 dark:stroke-gray-400"/>
      </div>
      <div class="mb-4 text-center text-2xl font-semibold text-teal-500">
        <span v-if="isEditable">{{ t('heading.bookSelection') }}</span>
        <span v-else-if="isFinished && !requiresConfirmation">{{ t('heading.eventBooked') }}</span>
        <span v-else-if="isFinished && requiresConfirmation">{{ t('info.bookingSuccessfullyRequested') }}</span>
      </div>
      <div class="mb-4 text-center text-gray-500 dark:text-gray-300">
        <div>{{ event.title }}:</div>
        <div>{{ time }}</div>
      </div>
      <div v-if="!isFinished" class="mb-4 text-center text-sm text-teal-500 underline underline-offset-2">
        {{ t('label.timeZone') }}: {{ dj.tz.guess() }}
      </div>
      <div v-if="!isFinished && route.name === 'availability'" class="text-center text-sm font-semibold">
        {{ t('text.disclaimerGABooking') }}
      </div>
      <form v-if="!isFinished" ref="bookingForm" class="my-8 flex flex-col gap-4">
        <label v-if="hasErrors" class="text-center">
          <span class="font-medium text-red-600 dark:text-red-300">
            {{ stateData }}
          </span>
        </label>
        <label>
          <span class="mb-1 font-medium text-gray-500 dark:text-gray-300">
            {{ t('label.name') }}
          </span>
          <input
            type="text"
            v-model="attendee.name"
            :disabled="isLoading"
            :placeholder="t('placeholder.firstAndLastName')"
            class="w-full rounded-md"
          />
        </label>
        <label>
          <span class="mb-1 font-medium text-gray-500 dark:text-gray-300">
            {{ t('label.email') }} <span class="text-rose-600">*</span>
          </span>
          <input
            type="email"
            v-model="attendee.email"
            :disabled="isLoading"
            :placeholder="t('placeholder.emailAddress')"
            class="w-full rounded-md"
            required
          />
        </label>
      </form>
      <div v-else class="my-8">
        <art-confetti class="mx-auto mb-8 size-52 fill-transparent stroke-none"/>
        <div class="mx-auto w-4/5 text-center text-sm text-gray-500">
          <span v-if="!requiresConfirmation">{{ t('text.invitationSentToAddress', {address: attendee.email}) }}</span>
          <span v-else>{{ t('text.requestInformationSentToOwner') }}</span>
        </div>
      </div>
      <div class="mx-auto flex w-4/5 items-stretch justify-center gap-8">
        <secondary-button
          :label="t('label.close')"
          @click="emit('close')"
        />
        <primary-button
          v-if="!isFinished"
          :label="t('label.bookEvent')"
          :waiting="isLoading"
          :disabled="!validAttendee || isLoading"
          @click="bookIt"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  inject, computed, reactive, ref, onMounted,
} from 'vue';
import { timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import ArtConfetti from '@/elements/arts/ArtConfetti';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';

// icons
import { IconX } from '@tabler/icons-vue';
import { useBookingModalStore } from '@/stores/booking-modal-store';
import { storeToRefs } from 'pinia';
import { modalStates } from '@/definitions';

// component constants
const user = useUserStore();
const { t } = useI18n();
const route = useRoute();
const dj = inject('dayjs');

const emit = defineEmits(['book', 'close']);

const props = defineProps({
  event: Object, // event data to display and book
  requiresConfirmation: Boolean, // Are we requesting a booking (availability) or booking it (one-off appointment.)
});

// Store
const bookingModalStore = useBookingModalStore();
const {
  open, state, stateData, isLoading, hasErrors, isFinished, isEditable,
} = storeToRefs(bookingModalStore);

// Refs

const attendee = reactive({
  name: '',
  email: '',
});

const bookingForm = ref();

// Computed

const time = computed(() => dj(props.event.start).format(`dddd, MMMM D, YYYY ${timeFormat()}`));
const validAttendee = computed(() => attendee.email.length > 2);

// Functions

/**
 * Submit the booking details
 */
const bookIt = () => {
  if (bookingForm.value.reportValidity() && validAttendee.value) {
    state.value = modalStates.loading;
    emit('book', attendee);
  }
};

onMounted(() => {
  if (user.exists()) {
    attendee.name = user.data.name;
    attendee.email = user.data.email;
  }
});
</script>
