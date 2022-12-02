<template>
  <div
    class="p-1"
    :class="{
      'cursor-pointer': mini,
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
    <div v-if="events && !mini" class="h-24 flex flex-col gap-1.5 overflow-y-auto">
      <div
        v-for="event in events"
        :key="event"
        class="shrink-0 text-sm text-gray-600 overflow-hidden"
        :class="{
          'rounded bg-sky-400/10 border-2 border-dashed border-sky-400 px-2 py-0.5': !placeholder,
          'group rounded-md bg-green-50 p-1 cursor-pointer hover:shadow-lg hover:text-white hover:bg-gradient-to-b hover:from-teal-500 hover:to-sky-600': placeholder
        }"
        @click="emit('eventSelected')"
      >
        <div
          class="whitespace-nowrap overflow-hidden overflow-ellipsis rounded"
          :class="{
            'h-10 p-1 font-semibold bg-sky-400/10 border-2 border-dashed border-teal-500 group-hover:border-white': placeholder
          }"
        >
          {{ event.title }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// component properties
defineProps({
  day: String,          // number of day in its month
  isActive: Boolean,    // flag showing if the day belongs to active month
  isSelected: Boolean,  // flag showing if the day is currently selected by user
  isToday: Boolean,     // flag showing if the day is today
  mini: Boolean,        // flag showing if this is a day cell of a small calendar
  placeholder: Boolean, // flag formating events as placeholder
  events: Array         // list of events to show on this day or null
});

// component emits
const emit = defineEmits(['eventSelected']);
</script>
