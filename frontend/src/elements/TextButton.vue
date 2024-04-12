<template>
  <button
    class="
      relative flex h-7 items-center justify-center gap-1 whitespace-nowrap rounded-md border border-gray-400 px-2
      text-sm font-semibold text-gray-500 transition-all ease-in-out hover:bg-gray-50
      hover:shadow-md dark:text-gray-400 dark:hover:bg-gray-800
    "
    @click.stop="copy ? copyToClipboard() : null"
  >
    <icon-copy
      v-if="copy && !copied"
      class="size-4 fill-transparent stroke-gray-500 stroke-2 dark:stroke-gray-400"
    />
    <icon-clipboard-check
      v-if="copy && copied"
      class="size-4 fill-transparent stroke-teal-500 stroke-2"
    />
    {{ label }}
    <transition>
      <tool-tip v-show="copied" :content="t('info.copiedToClipboard')" />
    </transition>
  </button>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import ToolTip from '@/elements/ToolTip';

// icons
import { IconCopy, IconClipboardCheck } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();

// component properties
const props = defineProps({
  label: String, // button text
  copy: String, // text to copy to clipboard
});

// state for copy click
const copied = ref(false);

// copy text to clipboard
const copyToClipboard = async () => {
  await navigator.clipboard.writeText(props.copy);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 4000);
};
</script>
