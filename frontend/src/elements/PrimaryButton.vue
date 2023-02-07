<template>
  <button class="
    h-10
    text-xl
    font-semibold
    whitespace-nowrap
    text-white
    rounded-full
    bg-gradient-to-br
    from-teal-400
    to-sky-600
    hover:from-sky-400
    hover:to-teal-600
    hover:shadow-md
    hover:scale-102
    active:scale-98
    disabled:from-teal-200
    disabled:to-sky-300
    disabled:scale-100
    disabled:shadow-none
    px-6
    transition-all
    ease-in-out
    flex
    items-center
    justify-center
    gap-2
  ">
    <copy-icon v-if="icon === 'copy'" class="h-6 w-6 stroke-2 stroke-white fill-transparent" />
    <check-icon v-if="icon === 'check'" class="h-6 w-6 stroke-2 stroke-white fill-transparent" />
    {{ label }}
  </button>
</template>

<script setup>
// icons
import {
  CheckIcon,
  CopyIcon,
} from "vue-tabler-icons";

// component properties
defineProps({
  label: String, // button text
  icon: String   // optional icon displayed before label
});
</script>
