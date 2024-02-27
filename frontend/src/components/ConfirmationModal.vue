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
      {{ title }}
    </div>
    <div class="max-w-xs text-center">
      {{ message }}
    </div>
    <div class="flex gap-4">
      <secondary-button :label="cancelLabel" @click="emit('close')" />
      <primary-button v-if="!useCautionButton" :label="confirmLabel" @click="emit('confirm')" />
      <caution-button v-else :label="confirmLabel" @click="emit('confirm')" />
    </div>
  </div>
</template>

<script setup>
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';
import CautionButton from '@/elements/CautionButton';

// icons
import { IconX } from '@tabler/icons-vue';

// component properties
defineProps({
  open: Boolean, // modal state
  title: String,
  message: String,
  confirmLabel: String,
  cancelLabel: String,
  useCautionButton: Boolean,
});

// component emits
const emit = defineEmits(['close', 'confirm', 'error']);
</script>
