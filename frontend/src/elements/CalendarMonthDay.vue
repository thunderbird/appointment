<template>
  <div
    class="p-1 group/day"
    :class="{
      'cursor-pointer py-2': mini,
      'h-32': !mini,
      'bg-white': isActive,
      'bg-gray-50 text-gray-400': !isActive || disabled,
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
        v-for="event in events"
        :key="event"
        class="shrink-0 text-sm text-gray-700 hover:shadow-md"
        :class="{
          'rounded bg-sky-400/10 border-2 border-dashed border-sky-400 px-2 py-0.5': !placeholder && !event.remote,
          'group/event rounded-md bg-teal-50 p-1 cursor-pointer hover:shadow-lg hover:text-white hover:bg-gradient-to-b hover:from-teal-500 hover:to-sky-600': placeholder,
          'flex items-center gap-2 px-2 py-0.5': event.remote,
          '!border-solid text-black': event.attendee !== null
        }"
        :style="{
          'border-color': eventColor(event).border,
          'background-color': eventColor(event).background,
        }"
        @click="emit('eventSelected', day)"
        @mouseenter="element => showDetails ? showEventPopup(element, event) : null"
      >
        <div
          v-if="event.remote"
          class="w-2 h-2 shrink-0 rounded-full bg-sky-400"
          :style="{ 'background-color': event.calendar_color }"
        ></div>
        <div
          class="truncate rounded"
          :class="{
            'h-10 p-1 font-semibold border-2 border-dashed border-teal-500 group-hover/event:border-white': placeholder
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
import { inject, reactive } from 'vue';
import EventPopup from '@/elements/EventPopup';

const dj = inject("dayjs");

// component properties
const props = defineProps({
  day:         String,  // number of day in its month
  isActive:    Boolean, // flag showing if the day belongs to active month
  isSelected:  Boolean, // flag showing if the day is currently selected by user
  isToday:     Boolean, // flag showing if the day is today
  mini:        Boolean, // flag showing if this is a day cell of a small calendar
  placeholder: Boolean, // flag formating events as placeholder
  events:      Array,   // list of events to show on this day or null
  showDetails: Boolean, // flag enabling event popups with details
  disabled:    Boolean, // flag making this day non-selectable and inactive
});

// component emits
const emit = defineEmits(['eventSelected']);

// create event color for border and background, inherited from calendar color
const eventColor = (event) => {
  const color = {
    border:     null,
    background: null,
  };
  // only color appointment slots
  if (!props.placeholder && !event.remote) {
    color.border = event.calendar_color;
    color.background = event.calendar_color;
    // keep solid background only for slots with attendee
    if (!event.attendee) {
      color.background += '22';
    }
  }
  return color;
};

// event details
const popup = reactive({
  event:   null,
  display: 'none',
  top:     0,
  left:    0,
});
const showEventPopup = (element, event) => {
  popup.event = event;
  popup.display = 'block';
  popup.top = element.target.offsetTop + element.target.clientHeight/2 - element.target.parentElement.scrollTop + 'px';
  popup.left = element.target.offsetLeft + element.target.clientWidth + 8 + 'px';
};
const hideEventPopup = () => {
  popup.event = null;
  popup.display = 'none';
};

</script>
