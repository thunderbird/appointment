<template>
  <div v-if="open" class="w-screen h-screen fixed top-0 left-0 z-40 bg-gray-800/50" @click="emit('close')"></div>
  <div
    v-if="open"
    class="fixed z-50 position-center position-center rounded-xl p-12 max-w-lg w-full bg-white dark:bg-gray-700"
  >
    <div class="absolute top-8 right-8 cursor-pointer" @click="emit('close')">
      <icon-x class="h-6 w-6 stroke-1 fill-transparent stroke-gray-700 dark:stroke-gray-400" />
    </div>
    <div class="text-2xl text-center font-semibold mb-4 text-teal-500">
      <span v-if="!success">{{ t('heading.bookSelection') }}</span>
      <span v-else-if="success && !request">{{ t('heading.eventBooked') }}</span>
      <span v-else-if="success && request">{{ t('info.bookingSuccessfullyRequested') }}</span>
    </div>
    <div class="text-center mb-4 text-gray-500 dark:text-gray-300">
      <div>{{ event.title }}:</div>
      <div>{{ time }}</div>
    </div>
    <div v-if="!success" class="text-sm text-center underline underline-offset-2 mb-4 text-teal-500">
      {{ t('label.timeZone') }}: {{ dj.tz.guess() }}
    </div>
    <div v-if="!success && route.name === 'availability'" class="text-sm text-center font-semibold">
      {{ t('text.disclaimerGABooking') }}
    </div>
    <form v-if="!success" ref="bookingForm" class="flex flex-col gap-4 my-8">
      <label>
        <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
          {{ t('label.name') }}
        </div>
        <input
          type="text"
          v-model="attendee.name"
          :placeholder="t('placeholder.firstAndLastName')"
          class="rounded-md w-full"
        />
      </label>
      <label>
        <div class="font-medium mb-1 text-gray-500 dark:text-gray-300">
          {{ t('label.email') }} <span class="text-rose-600">*</span>
        </div>
        <input
          type="email"
          v-model="attendee.email"
          :placeholder="t('placeholder.emailAddress')"
          class="rounded-md w-full"
          required
        />
      </label>
    </form>
    <div v-else class="mb-8 mt-8">
      <art-confetti class="h-52 w-52 stroke-none fill-transparent mb-8 mx-auto" />
      <div class="text-sm w-4/5 mx-auto text-center text-gray-500">
        <span v-if="!request">{{ t('text.invitationSentToAddress', { address: attendee.email }) }}</span>
        <span v-else>{{ t('text.requestInformationSentToOwner') }}</span>
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
        v-else-if="!request"
        :label="t('label.downloadInvitation')"
        @click="emit('download')"
      />
    </div>
  </div>
</template>

<script setup>
import { inject, computed, reactive, ref, onMounted } from 'vue';
import { timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import ArtConfetti from '@/elements/arts/ArtConfetti';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';

// icons
import { IconX } from '@tabler/icons-vue';

// component constants
const user = useUserStore();
const { t } = useI18n();
const route = useRoute();
const dj = inject('dayjs');

// component properties
const props = defineProps({
  open: Boolean, // modal state
  event: Object, // event data to display and book
  success: Boolean, // true if booking was successful
  request: Boolean, // true if booking was only requested instead of executed directly
});

// component emits
const emit = defineEmits(['book', 'download', 'close']);

// format time
const time = computed(() => dj(props.event.start).format(`dddd, MMMM D, YYYY ${timeFormat()}`));

// attendee data
const attendee = reactive({
  name: '',
  email: '',
});
onMounted(() => {
  if (user.exists()) {
    attendee.name = user.data.name;
    attendee.email = user.data.email;
  }
});
const validAttendee = computed(() => attendee.email.length > 2);

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
</script>
