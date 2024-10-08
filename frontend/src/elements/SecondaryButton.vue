<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import ToolTip from '@/elements/ToolTip.vue';

// icons
import { IconClipboardCheck, IconCopy } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();

// component properties
interface Props {
  label?: string; // button text
  copy?: string; // text to copy to clipboard
  waiting?: boolean; // if true, spinning animation is shown instead of label
}
const props = defineProps<Props>();

// state for copy click
const copied = ref(false);

// copy text to clipboard
const copyToClipboard = async () => {
  await navigator.clipboard.writeText(props.copy);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 4000);
};
</script>

<template>
  <button
    class="
      relative flex h-10 items-center justify-center gap-2 whitespace-nowrap rounded-full border
      border-teal-500 bg-white px-6 text-base font-semibold text-gray-600 transition-all ease-in-out
      hover:scale-102 hover:shadow-md active:scale-98 disabled:scale-100 disabled:opacity-50 disabled:shadow-none
      dark:bg-gray-700 dark:text-gray-100
    "
    :class="{ '!text-transparent': waiting }"
    @click="copy ? copyToClipboard() : null"
  >
    <div
      v-if="waiting"
      class="absolute size-5 animate-spin rounded-full border-2 border-teal-500 border-t-transparent"
    ></div>
    <icon-copy
      v-if="copy && !copied"
      class="size-6 fill-transparent stroke-current stroke-2"
    />
    <icon-clipboard-check
      v-if="copy && copied"
      class="size-6 fill-transparent stroke-current stroke-2"
    />
    <template v-if="label">
      {{ label }}
    </template>
    <template v-else>
      <slot></slot>
    </template>
    <transition>
      <tool-tip v-show="copied" :content="t('info.copiedToClipboard')" />
    </transition>
  </button>
</template>
