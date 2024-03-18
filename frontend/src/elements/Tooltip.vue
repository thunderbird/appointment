<template>
  <div
    class="
      absolute bottom-full -translate-y-2 z-50 whitespace-nowrap rounded-lg bg-black/75 py-1.5 px-3
      font-sans text-sm font-normal text-white focus:outline-none
    "
  >
    {{ content }}
    <svg viewBox="0 0 100 100" class="absolute top-full left-1/2 -translate-x-1/2 size-3 fill-black/75">
      <polygon points="0,0 50,60 100,0" />
    </svg>
  </div>
</template>

<script setup>
// component properties
const props = defineProps({
  content: String, // Tooltip text
});
</script>
