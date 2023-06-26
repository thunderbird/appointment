<template>
  <div v-if="open" class="w-screen h-screen fixed top-0 left-0 z-40 bg-gray-800/50" @click="emit('close')"></div>
  <div
    v-if="open"
    class="
      fixed z-50 position-center position-center rounded-xl p-12 max-w-lg w-full flex flex-col items-center gap-6
      bg-white dark:bg-gray-700
    "
  >
    <div class="absolute top-8 right-8 cursor-pointer" @click="emit('close')">
      <icon-x class="h-6 w-6 stroke-1 fill-transparent stroke-gray-700 dark:stroke-gray-400" />
    </div>
    <div class="text-2xl font-semibold text-teal-500">
      {{ title }}
    </div>
    <div class="max-w-xs text-center">
      {{ message }}
    </div>
    <div class="flex gap-4">
      <secondary-button :label="cancelLabel" @click="emit('close')" />
      <primary-button :label="confirmLabel" @click="emit('confirm')" />
    </div>
  </div>
</template>

<script setup>
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';

// icons
import { IconX } from '@tabler/icons-vue';

// component properties
defineProps({
  open: Boolean, // modal state
  title: String,
  message: String,
  confirmLabel: String,
  cancelLabel: String,
});

// component emits
const emit = defineEmits(['close', 'confirm', 'error']);
</script>
