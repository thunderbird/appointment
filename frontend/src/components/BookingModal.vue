<template>
  <div v-if="open">
    <div class="w-screen h-screen fixed top-0 left-0 z-40 bg-gray-800/50" @click="emit('close')"></div>
    <div
      class="fixed z-50 position-center position-center rounded-xl p-12 max-w-lg w-full bg-white dark:bg-gray-700"
    >
      <div class="absolute top-8 right-8 cursor-pointer" @click="emit('close')">
        <icon-x class="h-6 w-6 stroke-1 fill-transparent stroke-gray-700 dark:stroke-gray-400"/>
      </div>
      <div class="text-2xl text-center font-semibold mb-4 text-teal-500">
        <span v-if="isEditable">{{ t('heading.bookSelection') }}</span>
        <span v-else-if="isFinished && !requiresConfirmation">{{ t('heading.eventBooked') }}</span>
        <span v-else-if="isFinished && requiresConfirmation">{{ t('info.bookingSuccessfullyRequested') }}</span>
      </div>
      <div class="text-center mb-4 text-gray-500 dark:text-gray-300">
        <div>{{ event.title }}:</div>
        <div>{{ time }}</div>
      </div>
      <div v-if="!isFinished" class="text-sm text-center underline underline-offset-2 mb-4 text-teal-500">
        {{ t('label.timeZone') }}: {{ dj.tz.guess() }}
      </div>
      <div v-if="!isFinished && route.name === 'availability'" class="text-sm text-center font-semibold">
        {{ t('text.disclaimerGABooking') }}
      </div>
      <form v-if="!isFinished" ref="bookingForm" class="flex flex-col gap-4 my-8">
        <label v-if="hasErrors" class="text-center">
          <span class="font-medium text-red-600 dark:text-red-300">
            {{ stateData }}
          </span>
        </label>
        <label>
          <span class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t('label.name') }}
          </span>
          <input
            type="text"
            v-model="attendee.name"
            :disabled="isLoading"
            :placeholder="t('placeholder.firstAndLastName')"
            class="rounded-md w-full"
          />
        </label>
        <label>
          <span class="font-medium mb-1 text-gray-500 dark:text-gray-300">
            {{ t('label.email') }} <span class="text-rose-600">*</span>
          </span>
          <input
            type="email"
            v-model="attendee.email"
            :disabled="isLoading"
            :placeholder="t('placeholder.emailAddress')"
            class="rounded-md w-full"
            required
          />
        </label>
      </form>
      <div v-else class="mb-8 mt-8">
        <art-confetti class="h-52 w-52 stroke-none fill-transparent mb-8 mx-auto"/>
        <div class="text-sm w-4/5 mx-auto text-center text-gray-500">
          <span v-if="!requiresConfirmation">{{ t('text.invitationSentToAddress', {address: attendee.email}) }}</span>
          <span v-else>{{ t('text.requestInformationSentToOwner') }}</span>
        </div>
      </div>
      <div class="flex gap-8 w-4/5 mx-auto justify-center items-stretch">
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
        <primary-button
          v-else-if="!requiresConfirmation"
          :label="t('label.downloadInvitation')"
          @click="emit('download')"
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

const emit = defineEmits(['book', 'download', 'close']);

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
