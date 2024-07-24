<script setup lang="ts">
import { IconX } from '@tabler/icons-vue';
import { AlertSchemes } from '@/definitions';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// component properties
interface Props {
  title?: string; // flag showing this event as busy and non-selectable
  canClose?: boolean; // flag for making this alert closable
  scheme?: AlertSchemes; // flag, are we in month view?
};
withDefaults(defineProps<Props>(), {
  canClose: true,
  scheme: AlertSchemes.Error,
})

const emit = defineEmits(['close']);

</script>

<template>
<div
  class="flex items-center p-2 leading-none text-white shadow-md shadow-black/30 dark:shadow-lg lg:inline-flex lg:rounded-xl"
  role="alert"
  :class="{
    'bg-rose-600 dark:bg-rose-900': scheme === AlertSchemes.Error,
    'bg-orange-400 dark:bg-orange-700': scheme === AlertSchemes.Warning,
    'bg-green-400 dark:bg-green-700': scheme === AlertSchemes.Success,
    'bg-teal-400 dark:bg-teal-700': scheme === AlertSchemes.Info,
  }"
>
  <span
    v-if="title"
    class="mr-3 flex rounded-full px-2 py-1 text-center text-xs font-bold uppercase"
    :class="{
      'bg-rose-500 dark:bg-rose-800': scheme === AlertSchemes.Error,
      'bg-orange-500 dark:bg-orange-800': scheme === AlertSchemes.Warning,
      'bg-green-500 dark:bg-green-800': scheme === AlertSchemes.Success,
      'bg-teal-500 dark:bg-teal-800': scheme === AlertSchemes.Info,
    }"
  >
    {{ title }}
  </span>
  <span class="ml-1 block sm:inline">
    <slot></slot>
  </span>
  <span v-if="canClose" class="btn-close ml-auto" @click="emit('close')" :title="t('label.close')">
    <icon-x class="size-6 cursor-pointer fill-transparent stroke-white stroke-1" />
  </span>
</div>
</template>
