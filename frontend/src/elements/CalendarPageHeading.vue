<template>
  <h2 v-if="title" class="flex flex-col">
    <div class="text-4xl font-light">{{ title }}</div>
    <div class="flex gap-2">
      <span class="text-xl font-semibold">{{ month }}</span>
      <span class="text-xl">{{ year }}</span>
    </div>
  </h2>
  <h2 v-else class="flex gap-3">
    <span class="text-4xl font-normal">{{ month }}</span>
    <span class="text-4xl font-light">{{ year }}</span>
  </h2>
</template>

<script setup>
// component properties
defineProps({
  month:  String, // month of active date
  year:   String, // year of active date
  title:  String, // title of current calendar view (optional)
});
</script>
