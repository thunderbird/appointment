<template>
  <button
    class="
      h-7 font-semibold text-sm whitespace-nowrap border rounded-md hover:shadow-md px-2 transition-all ease-in-out flex items-center justify-center gap-1
      text-gray-500 dark:text-gray-400 border-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800
    "
    @click="copy ? copyToClipboard() : null"
  >
    <icon-copy v-if="copy && !copied" class="h-4 w-4 fill-transparent stroke-2 stroke-gray-500 dark:stroke-gray-400" />
    <icon-check v-if="copy && copied" class="h-4 w-4 fill-transparent stroke-2 stroke-green-500" />
    {{ label }}
  </button>
</template>

<script setup>
import { ref } from 'vue';

// icons
import {
  IconCheck,
  IconCopy,
} from '@tabler/icons-vue';

// component properties
const props = defineProps({
  label: String, // button text
  copy: String, // text to copy to clipboard
});

// state for copy click
const copied = ref(false);

// copy text to clipboard
const copyToClipboard = () => {
  navigator.clipboard.writeText(props.copy).then(() => {
    copied.value = true;
    setInterval(() => { copied.value = false; }, 3000);
  });
};
</script>
