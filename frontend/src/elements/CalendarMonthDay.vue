<template>
  <div
    class="p-1"
    :class="{
      'h-32': !mini,
      'bg-white': isActive,
      'bg-gray-50 text-gray-400': !isActive,
    }"
  >
    <div
      class="w-6 rounded-full text-center"
      :class="{
        'bg-teal-500 text-white font-semibold': isToday,
        'text-teal-500': isSelected && !isToday,
        'mx-auto': mini,
      }"
    >
      {{ day }}
    </div>
    <div v-if="(events && !mini)" class="flex flex-col gap-2">
      <div
        v-for="event in events"
        :key="event"
        class="whitespace-nowrap overflow-hidden overflow-ellipsis rounded border-2 border-dashed border-sky-400 px-2 py-1"
      >
        {{ event.title }}
      </div>
    </div>
  </div>
</template>

<script setup>
// component properties
defineProps({
  day: String,         // number of day in its month
  isActive: Boolean,   // flag showing if the day belongs to active month
  isSelected: Boolean, // flag showing if the day is currently selected by user
  isToday: Boolean,    // flag showing if the day is today
  mini: Boolean,       // flag showing if this is a day cell of a small calendar
  events: Array        // list of events to show on this day or null
});
</script>
