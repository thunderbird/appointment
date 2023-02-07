<template>
  <button
    class="
      h-7
      font-semibold
      text-sm
      whitespace-nowrap
      text-slate-500
      border
      border-slate-400
      rounded-md
      hover:shadow-md
      hover:bg-slate-50
      px-2
      transition-all
      ease-in-out
      flex
      items-center
      justify-center
      gap-1
    "
    @click="copy ? copyToClipboard() : null"
  >
    <copy-icon v-if="copy && !copied" class="h-4 w-4 stroke-2 stroke-slate-500 fill-transparent" />
    <check-icon v-if="copy && copied" class="h-4 w-4 stroke-2 stroke-green-500 fill-transparent" />
    {{ label }}
  </button>
</template>

<script setup>
import { ref } from 'vue';

// icons
import {
  CheckIcon,
  CopyIcon,
} from "vue-tabler-icons";

// component properties
const props = defineProps({
  label: String, // button text
  copy: String   // text to copy to clipboard
});

// state for copy click
const copied = ref(false);

// copy text to clipboard
const copyToClipboard = () => {
  navigator.clipboard.writeText(props.copy).then(function() {
    copied.value = true;
    setInterval(() => { copied.value = false; }, 3000);
  });
};
</script>
