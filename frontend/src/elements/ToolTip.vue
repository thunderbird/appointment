<script setup lang="ts">
// component properties
interface Props {
  content: string; // Tooltip text
}
defineProps<Props>();
</script>

<template>
  <div
    class="
      absolute bottom-full z-50 -translate-y-2 whitespace-nowrap text-wrap rounded-lg bg-black/75 px-3
      py-1.5 font-sans text-sm font-normal text-white focus:outline-none
    "
  >
    {{ content }}
    <svg viewBox="0 0 100 100" class="absolute left-1/2 top-full size-3 -translate-x-1/2 fill-black/75">
      <polygon points="0,0 50,60 100,0" />
    </svg>
  </div>
</template>
