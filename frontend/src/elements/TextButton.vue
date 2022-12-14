<template>
  <button class="
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
  ">
    <icon-copy v-if="icon === 'copy'" class="h-4 w-4 stroke-2 stroke-slate-500 fill-transparent" />
    <icon-check v-if="icon === 'check'" class="h-4 w-4 stroke-2 stroke-slate-500 fill-transparent" />
    {{ label }}
  </button>
</template>

<script setup>
import IconCheck from '@/elements/icons/IconCheck.vue';
import IconCopy from '@/elements/icons/IconCopy.vue';

// component properties
defineProps({
  label: String, // button text
  icon: String   // optional icon displayed before label
});
</script>
