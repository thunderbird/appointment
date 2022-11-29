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
    hover:scale-105
    active:scale-95
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
    <icon-copy v-if="iconCopy" class="h-6 w-6 stroke-2 stroke-white fill-transparent" />
    {{ label }}
  </button>
</template>

<script setup>
import IconCopy from '@/elements/icons/IconCopy.vue';

// component properties
defineProps({
  label: String,    // button text
  iconCopy: Boolean // optional copy icon displayed before label
});
</script>
