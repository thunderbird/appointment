<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import ToolTip from '@/elements/ToolTip.vue';

// icons
import { IconCopy, IconClipboardCheck } from '@tabler/icons-vue';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';

// component constants
const { t } = useI18n();

// component properties
interface Props {
  uid: string; // id for this button
  label?: string; // button text
  tooltip?: string, // optional tooltip
  copy?: string; // text to copy to clipboard
}
const props = defineProps<Props>();

// state for copy click
const copied = ref(false);
const hover = ref(false);

// copy text to clipboard
const copyToClipboard = async () => {
  await navigator.clipboard.writeText(props.copy);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 4000);

  if (usePosthog) {
    posthog.capture(MetricEvents.CopyToClipboard, {
      uid: props.uid,
      label: props.label,
    });
  }
};
</script>

<template>
  <button
    class="
      relative flex h-7 items-center justify-center gap-1 whitespace-nowrap rounded-md border border-gray-400 px-2
      text-sm font-semibold text-gray-500 transition-all ease-in-out hover:bg-gray-50
      hover:shadow-md dark:text-gray-400 dark:hover:bg-gray-800
    "
    @click.stop="copy ? copyToClipboard() : null"
    @mouseover="hover = true"
    @mouseout="hover = false"
    @focusin="hover = true"
    @focusout="hover = false"
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
    <transition v-if="tooltip">
      <tool-tip class="w-24" v-show="hover && tooltip && !copied" :content="tooltip" />
    </transition>
  </button>
</template>
