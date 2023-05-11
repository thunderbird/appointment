<template>
  <div
    class="p-1 group/day"
    :class="{
      'cursor-pointer py-2': mini,
      'h-32': !mini,
      'bg-white dark:bg-gray-700': isActive,
      'bg-gray-50 dark:bg-gray-600 text-gray-400': !isActive || disabled,
      'cursor-not-allowed': disabled
    }"
    @mouseleave="hideEventPopup"
  >
    <div
      class="w-6 rounded-full text-center relative"
      :class="{
        'bg-teal-500 text-white font-semibold': isToday,
        'text-teal-500': isSelected && !isToday,
        'mx-auto': mini,
        'group-hover/day:bg-sky-600': mini && isToday && !disabled,
        'group-hover/day:text-sky-600': mini && !isToday && !disabled,
      }"
    >
      {{ dj(day).format('D') }}
      <div v-if="mini && events" class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 bg-teal-600 rounded-full"></div>
    </div>
    <div v-if="events && !mini" class="h-24 flex flex-col gap-1.5 overflow-y-auto">
      <div
        v-for="event in sortedEvents"
        :key="event"
        class="shrink-0 text-sm text-gray-700 dark:text-gray-200 hover:shadow-md"
        :class="{
          'rounded border-2 border-dashed px-2 py-0.5 border-sky-400 bg-sky-400/10': !placeholder && !event.remote,
          'group/event rounded-md p-1 cursor-pointer hover:shadow-lg hover:bg-gradient-to-b hover:!text-white bg-teal-50 dark:bg-teal-800 hover:from-teal-500 hover:to-sky-600': placeholder,
          'flex items-center gap-2 px-2 py-0.5': event.remote,
          '!border-solid text-black': event.attendee !== null,
          'rounded bg-amber-400/80 dark:text-white': event.all_day
        }"
        :style="{
          'border-color': eventColor(event, placeholder).border,
          'background-color': eventColor(event, placeholder).background,
        }"
        @click="emit('eventSelected', day)"
        @mouseenter="element => showDetails ? showEventPopup(element, event) : null"
      >
        <div
          v-if="event.remote && !event.all_day"
          class="w-2 h-2 shrink-0 rounded-full bg-sky-400"
          :style="{ 'background-color': event.calendar_color }"
        ></div>
        <div
          class="truncate rounded"
          :class="{
            'h-10 p-1 font-semibold border-2 border-dashed border-teal-500 group-hover/event:border-white': placeholder,
          }"
        >
          {{ event.title }}
        </div>
      </div>
    </div>
    <event-popup
      v-if="(events && showDetails)"
      :style="{
        'display': popup.display,
        'top': popup.top,
        'left': popup.left,
      }"
      :event="popup.event"
    />
  </div>
</template>

<script setup>
import { eventColor } from '@/utils';
import { inject, reactive, computed } from 'vue';
import EventPopup from '@/elements/EventPopup';

const dj = inject('dayjs');

// component properties
const props = defineProps({
  day: String, // number of day in its month
  isActive: Boolean, // flag showing if the day belongs to active month
  isSelected: Boolean, // flag showing if the day is currently selected by user
  isToday: Boolean, // flag showing if the day is today
  mini: Boolean, // flag showing if this is a day cell of a small calendar
  placeholder: Boolean, // flag formating events as placeholder
  events: Array, // list of events to show on this day or null
  showDetails: Boolean, // flag enabling event popups with details
  disabled: Boolean, // flag making this day non-selectable and inactive
});

// component emits
const emit = defineEmits(['eventSelected']);

// bring events to specific order: all day events first, than sorted by start date
const sortedEvents = computed(() => [...props.events].sort((a, b) => {
  if (a.all_day && !b.all_day) {
    return -1;
  }
  if (!a.all_day && b.all_day) {
    return 1;
  }
  if (a.all_day && b.all_day || dj(a.start).isSame(dj(b.start))) {
    return a.title.localeCompare(b.title);
  }
  return dj(a.start).isAfter(dj(b.start));
}));

// event details
const popup = reactive({
  event: null,
  display: 'none',
  top: 0,
  left: 0,
});
const showEventPopup = (element, event) => {
  popup.event = event;
  popup.display = 'block';
  popup.top = `${element.target.offsetTop + element.target.clientHeight / 2 - element.target.parentElement.scrollTop}px`;
  popup.left = `${element.target.offsetLeft + element.target.clientWidth + 8}px`;
};
const hideEventPopup = () => {
  popup.event = null;
  popup.display = 'none';
};

</script>
