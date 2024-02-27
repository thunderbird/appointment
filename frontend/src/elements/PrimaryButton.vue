<template>
  <button
    class="relative flex h-10 items-center justify-center gap-2 whitespace-nowrap rounded-full bg-gradient-to-br from-teal-400 to-sky-600 px-6 text-base font-semibold text-white transition-all ease-in-out hover:scale-102 hover:shadow-md active:scale-98 enabled:hover:from-sky-400 enabled:hover:to-teal-600 disabled:scale-100 disabled:opacity-50 disabled:shadow-none"
    :class="{ '!text-transparent': waiting }"
    @click="copy ? copyToClipboard() : null"
  >
    <div
      v-if="waiting"
      class="absolute size-5 animate-spin rounded-full border-2 border-white border-t-transparent"
    ></div>
    <icon-copy
      v-if="copy && !copied"
      class="size-6 fill-transparent stroke-current stroke-2"
    />
    <icon-check
      v-if="copy && copied"
      class="size-6 fill-transparent stroke-current stroke-2"
    />
    <template v-if="label">
      {{ label }}
    </template>
    <template v-else>
      <slot></slot>
    </template>
  </button>
</template>

<script setup>
import { ref } from 'vue';

// icons
import { IconCheck, IconCopy } from '@tabler/icons-vue';

// component properties
const props = defineProps({
  label: String, // button text
  copy: String, // text to copy to clipboard
  waiting: Boolean, // if true, spinning animation is shown instead of label
});

// state for copy click
const copied = ref(false);

// copy text to clipboard
const copyToClipboard = async () => {
  await navigator.clipboard.writeText(props.copy);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 3000);
};
</script>
