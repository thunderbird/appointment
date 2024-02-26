<template>
  <div
    class="group/day p-1"
    :class="{
      'cursor-pointer py-2': mini,
      'h-32': !mini,
      'bg-white dark:bg-gray-700': isActive,
      'bg-gray-50 text-gray-400 dark:bg-gray-600': !isActive || disabled,
      'cursor-not-allowed': disabled
    }"
    @mouseleave="popup = {...initialEventPopupData}"
  >
    <div
      class="relative w-6 rounded-full text-center"
      :class="{
        'bg-teal-500 font-semibold text-white': isToday,
        'text-teal-500': isSelected && !isToday,
        'mx-auto': mini,
        'group-hover/day:bg-sky-600': mini && isToday && !disabled,
        'group-hover/day:text-sky-600': mini && !isToday && !disabled,
      }"
    >
      {{ dj(day).format('D') }}
      <div
        v-if="mini && events"
        class="absolute -bottom-1 left-1/2 size-1.5 -translate-x-1/2 rounded-full bg-teal-600"
      ></div>
    </div>
    <div v-if="events && !mini" class="flex h-24 flex-col gap-1.5 overflow-y-auto">
      <div
        v-for="event in sortedEvents"
        :key="event"
        class="shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200"
        :class="{
          'rounded border-2 border-dashed border-sky-400 bg-sky-400/10 px-2 py-0.5': !placeholder && !event.remote && !event.preview,
          'group/event cursor-pointer rounded-md p-1 hover:bg-gradient-to-b hover:shadow-lg': placeholder,
          'bg-teal-50 hover:from-teal-500 hover:to-sky-600 hover:!text-white dark:bg-teal-800': placeholder,
          'flex items-center gap-1.5 px-2 py-0.5': event.remote,
          'flex items-center rounded border-l-4 border-teal-400 px-2': event.preview,
          '!border-solid text-black': event.attendee !== null,
          'rounded bg-amber-400/80 dark:text-white': event.all_day
        }"
        :style="{
          borderColor: eventColor(event, placeholder).border,
          backgroundColor: eventColor(event, placeholder).background,
        }"
        @click="emit('eventSelected', day)"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      >
        <div
          v-if="event.remote && !event.all_day"
          class="mt-0.5 size-2.5 shrink-0 rounded-full"
          :class="{
            'bg-sky-400': !event.tentative,
            'border border-dashed border-sky-400/70': event.tentative,
          }"
          :style="{
            borderColor: event.tentative ? event.calendar_color : null,
            backgroundColor: !event.tentative ? event.calendar_color : null,
          }"
        ></div>
        <div
          class="truncate rounded"
          :class="{
            'h-10 border-2 border-dashed border-teal-500 p-1 font-semibold group-hover/event:border-white': placeholder,
          }"
        >
          <span v-if="event.preview">{{ formattedTimeRange(event) }}</span>
          <span v-else>{{ event.title }}</span>
        </div>
      </div>
    </div>
    <event-popup
      v-if="(events && showDetails)"
      :style="{
        display: popup.display,
        top: popup.top,
        left: popup.left,
        right: popup.right,
      }"
      :event="popup.event"
      :position="popupPosition"
    />
  </div>
</template>

<script setup>
import {
  eventColor, timeFormat, initialEventPopupData, showEventPopup,
} from '@/utils';
import { inject, computed, ref } from 'vue';
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
  popupPosition: String, // currently supported: right, left, top
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
  if ((a.all_day && b.all_day) || dj(a.start).isSame(dj(b.start))) {
    return a.title.localeCompare(b.title);
  }
  return dj(a.start).isAfter(dj(b.start));
}));

// event details
const popup = ref({ ...initialEventPopupData });

// formatted time range
const formattedTimeRange = (event) => {
  const start = dj(event.start);
  const end = start.add(event.duration, 'minutes');
  return start.format(`${timeFormat()} - `) + end.format(timeFormat());
};
</script>
