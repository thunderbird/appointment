<template>
  <button
    class="flex h-7 items-center justify-center gap-1 whitespace-nowrap rounded-md border border-gray-400 px-2 text-sm font-semibold text-gray-500 transition-all ease-in-out hover:bg-gray-50 hover:shadow-md dark:text-gray-400 dark:hover:bg-gray-800"
    @click.stop="copy ? copyToClipboard() : null"
  >
    <icon-copy
      v-if="copy && !copied"
      class="size-4 fill-transparent stroke-gray-500 stroke-2 dark:stroke-gray-400"
    />
    <icon-check
      v-if="copy && copied"
      class="size-4 fill-transparent stroke-green-500 stroke-2"
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
