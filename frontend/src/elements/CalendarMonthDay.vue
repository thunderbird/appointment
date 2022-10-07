<template>
  <div
    class="p-1"
    :class="{
      'h-28': !mini,
      'bg-white': isActive,
      'bg-gray-50 text-gray-400': !isActive,
    }"
  >
    <div
      class="w-6 h-6 rounded-full text-center"
      :class="{
        'bg-teal-500 text-white font-semibold': isToday,
        'mx-auto': mini,
      }"
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
  isToday: Boolean,  // flag showing if the day is today
  mini: Boolean      // flag showing if this is a day cell of a small calendar
});
</script>
