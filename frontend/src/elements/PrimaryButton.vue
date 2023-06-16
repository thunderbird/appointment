<template>
  <button
    class="
      relative h-10 text-base font-semibold whitespace-nowrap rounded-full bg-gradient-to-br
      hover:shadow-md hover:scale-102 active:scale-98 disabled:scale-100 disabled:shadow-none disabled:opacity-50 px-6
      transition-all ease-in-out flex items-center justify-center gap-2
      text-white from-teal-400 to-sky-600 enabled:hover:from-sky-400 enabled:hover:to-teal-600
    "
    :class="{ 'text-transparent': waiting }"
    @click="copy ? copyToClipboard() : null"
  >
    <div
      v-if="waiting"
      class="absolute w-5 h-5 animate-spin rounded-full border-2 border-white border-t-transparent"
    ></div>
    <icon-copy
      v-if="copy && !copied"
      class="h-6 w-6 stroke-2 stroke-current fill-transparent"
    />
    <icon-check
      v-if="copy && copied"
      class="h-6 w-6 stroke-2 stroke-current fill-transparent"
    />
    {{ label }}
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
