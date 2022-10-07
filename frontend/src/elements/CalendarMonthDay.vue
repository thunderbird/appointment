<template>
  <div
    class="h-24 p-1"
    :class="{
      'bg-white': isActive,
      'bg-gray-50 text-gray-400': !isActive,
    }"
  >
    <div
      class="w-6 h-6 rounded-full text-center"
      :class="{'bg-teal-500 text-white font-semibold': isToday}"
    >
      {{ day }}
    </div>
  </div>
</template>

<script setup>
// component properties
defineProps({
  day: String,       // number of day in its month
  isActive: Boolean, // flag showing if the day belongs to active month
  isToday: Boolean   // flag showing if the day is today
});
</script>
