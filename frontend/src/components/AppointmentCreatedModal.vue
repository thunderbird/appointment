<template>
  <div v-if="open" class="bg-gray-800/50 w-screen h-screen fixed top-0 left-0 z-40" @click="emit('close')"></div>
  <div v-if="open" class="bg-white fixed z-50 position-center position-center rounded-xl p-12 max-w-lg w-full flex flex-col items-center gap-6">
    <div class="absolute top-8 right-8 cursor-pointer" @click="emit('close')">
      <icon-x class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
    </div>
    <div class="text-xl text-teal-500 font-semibold">{{ t('heading.appointmentCreated') }}</div>
    <div class="max-w-xs text-center">{{ t('text.titleIsReadyForBookings', { title: title }) }}</div>
    <art-confetti class="h-52 w-52 stroke-none fill-transparent mb-4" />
    <div class="flex gap-4">
      <secondary-button :label="t('label.close')" @click="emit('close')" />
      <primary-button :label="t('label.copyLink')" :icon-copy="true" @click="copy" />
    </div>
    <div>
      <router-link class="text-sm text-teal-500 cursor-pointer" :to="{ name: 'appointments', params: { 'view': 'pending' } }">
        {{ t('label.viewBooking') }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import IconX from '@/elements/icons/IconX.vue';
import ArtConfetti from '@/elements/arts/ArtConfetti.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();

// component properties
const props = defineProps({
  open: Boolean,      // modal state
  title: String,      // title of created appointment
  publicLink: String  // public link of created appointment for sharing
});

// component emits
const emit = defineEmits(['close']);

// copy link to clipboard
const copy = () => {
  console.log(props.publicLink);
};
</script>
