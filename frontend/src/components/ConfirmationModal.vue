<template>
  <div
    v-if="open"
    class="mdl-overlay-close fixed left-0 top-0 z-40 h-screen w-screen bg-gray-800/50"
    @click="emit('close')"
  ></div>
  <div
    v-if="open"
    class="position-center fixed z-50 flex w-full max-w-lg flex-col items-center gap-6 rounded-xl bg-white p-12 dark:bg-gray-700"
  >
    <div class="mdl-btn-close absolute right-8 top-8 cursor-pointer" @click="emit('close')" :title="t('label.close')">
      <icon-x class="size-6 fill-transparent stroke-gray-700 stroke-1 dark:stroke-gray-400" />
    </div>
    <div class="text-2xl font-semibold text-teal-500">
      {{ title }}
    </div>
    <div class="max-w-sm text-center">
      {{ message }}
    </div>
    <div class="flex gap-4">
      <secondary-button
        class="mdl-btn-close"
        :label="cancelLabel"
        @click="emit('close')"
        :title="t('label.close')"
      />
      <primary-button
        v-if="!useCautionButton"
        class="btn-confirm"
        :label="confirmLabel"
        @click="emit('confirm')"
        :title="t('label.confirm')"
      />
      <caution-button
        v-else
        class="btn-confirm"
        :label="confirmLabel"
        @click="emit('confirm')"
        :title="t('label.confirm')"
      />
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';
import CautionButton from '@/elements/CautionButton';

// icons
import { IconX } from '@tabler/icons-vue';

const { t } = useI18n();

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
