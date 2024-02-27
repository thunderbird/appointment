<template>
  <div v-if="open" class="fixed left-0 top-0 z-40 h-screen w-screen bg-gray-800/50" @click="emit('close')"></div>
  <div
    v-if="open"
    class="position-center fixed z-50 flex w-full max-w-lg flex-col items-center gap-6 rounded-xl bg-white p-12 dark:bg-gray-700"
  >
    <div class="absolute right-8 top-8 cursor-pointer" @click="emit('close')">
      <icon-x class="size-6 fill-transparent stroke-gray-700 stroke-1 dark:stroke-gray-400" />
    </div>
    <div class="text-2xl font-semibold text-teal-500">
      {{ t(isSchedule ? 'heading.scheduleCreated' : 'heading.appointmentCreated') }}
    </div>
    <div class="max-w-xs text-center">
      {{ t('text.titleIsReadyForBookings', { title: title }) }}
    </div>
    <art-confetti class="mb-4 size-52 fill-transparent stroke-none" />
    <div class="flex gap-4">
      <secondary-button :label="t('label.close')" @click="emit('close')" />
      <primary-button :label="t('label.copyLink')" :copy="publicLink" />
    </div>
    <div>
      <a :href="publicLink" target="_blank" class="cursor-pointer text-sm text-teal-500">
        {{ t('label.viewBooking') }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import ArtConfetti from '@/elements/arts/ArtConfetti';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';

// icons
import { IconX } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();

// component properties
defineProps({
  open: Boolean, // modal state
  isSchedule: Boolean, // confirmation is for a schedule instead of a common appointment
  title: String, // title of created appointment
  publicLink: String, // public link of created appointment for sharing
});

// component emits
const emit = defineEmits(['close']);
</script>
