<template>
  <div
    class="group/day"
    :class="{
      'cursor-pointer py-2': mini,
      'bg-white dark:bg-gray-700': isActive,
      'bg-gray-50 dark:bg-gray-600 text-gray-400': !isActive || disabled,
      'cursor-not-allowed': disabled
    }"
    @mouseleave="popup = {...initialEventPopupData}">
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
      <div
        v-if="mini"
        class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 bg-teal-600 rounded-full"
      ></div>
    </div>
    <div v-if="!mini" class="flex flex-col gap-1.5 overflow-y-auto" :style="`height: ${elementHeight}px`">
      <div
        class="h-[95%] w-[95%] shrink-0 text-sm text-gray-700 dark:text-gray-200 hover:shadow-md m-auto"
        :class="{
          'rounded border-2 border-dashed px-2 py-0.5 border-sky-400 bg-sky-400/10': !placeholder && !eventData.remote && !eventData.preview,
          'group/event rounded-md p-1 cursor-pointer hover:shadow-lg hover:bg-gradient-to-b': placeholder,
          'shadow-lg bg-gradient-to-b from-teal-500 to-sky-600': isSelected,
          'hover:!text-white bg-teal-50 dark:bg-teal-800 hover:from-teal-500 hover:to-sky-600': placeholder,
          'flex items-center gap-1.5 px-2 py-0.5': eventData.remote,
          'flex items-center rounded border-l-4 px-2 border-teal-400': eventData.preview,
          '!border-solid text-black': eventData.attendee !== null,
          'rounded bg-amber-400/80 dark:text-white': eventData.all_day
        }"
        :style="{
          borderColor: eventColor(eventData, placeholder).border,
          backgroundColor: eventColor(eventData, placeholder).background,
        }"
        @click="emit('eventSelected', day)"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      >
        <div
          v-if="eventData.remote && !eventData.all_day"
          class="w-2.5 h-2.5 mt-0.5 shrink-0 rounded-full"
          :class="{
            'bg-sky-400': !eventData.tentative,
            'border border-dashed border-sky-400/70': eventData.tentative,
          }"
          :style="{
            borderColor: eventData.tentative ? eventData.calendar_color : null,
            backgroundColor: !eventData.tentative ? eventData.calendar_color : null,
          }"
        ></div>
        <div
          class="truncate rounded"
          :class="{
            'h-full p-1 font-semibold border-2 border-dashed border-teal-500 group-hover/event:border-white': placeholder,
            'border-white': isSelected,
          }"
        >
          <span v-if="eventData.preview">{{ formattedTimeRange(event) }}</span>
          <span v-else>{{ event.title }}</span>
        </div>
      </div>
    </div>
    <event-popup
      v-if="(event && showDetails)"
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
import {
  computed, inject, ref, toRefs,
} from 'vue';
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
  event: Object, // the event to show
  showDetails: Boolean, // flag enabling event popups with details
  popupPosition: String, // currently supported: right, left, top
  disabled: Boolean, // flag making this day non-selectable and inactive
});

const { event } = toRefs(props);

const eventData = event.value.customData;
// TODO: Fix this, right now we are hard coded to 15 minute intervals at 40px per interval.
const elementHeight = computed(() => (eventData.duration / 15) * 40);

// component emits
const emit = defineEmits(['eventSelected']);

// event details
const popup = ref({ ...initialEventPopupData });

// formatted time range
const formattedTimeRange = (event) => {
  const start = dj(event.time.start);
  const end = dj(event.time.end);
  return start.format(`${timeFormat()} - `) + end.format(timeFormat());
};
</script>
