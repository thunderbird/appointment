<template>
  <div
    :class="{ 'text-gray-400 cursor-not-allowed': disabled, 'h-full': !monthView }"
    @mouseleave="popup = {...initialEventPopupData}"
  >
    <div
      class="flex flex-col gap-1.5 overflow-y-auto"
      :class="{ 'h-full': !monthView, 'px-1' : isBusy }"
      :style="`height: ${elementHeight}px`"
    >
      <!-- placeholder event for availability bookings -->
      <calendar-event-placeholder
        v-if="placeholder"
        :is-busy="isBusy"
        :is-selected="isSelected"
        :is-month-view="monthView"
        :label="formattedTimeRange(event)"
        @click="emit('eventSelected', day)"
      />

      <!-- remote event (can be normal, all_day or tentative) -->
      <calendar-event-remote
        v-else-if="eventData.remote"
        :is-month-view="monthView"
        :event="eventData"
        :label="event.title"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      />

      <!-- live preview event (e.g. for schedule calendar) -->
      <calendar-event-preview
        v-else-if="eventData.preview"
        :is-month-view="monthView"
        :event="eventData"
        :label="formattedTimeRange(event)"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      />

      <!-- scheduled event -->
      <calendar-event-scheduled
        v-else
        :is-month-view="monthView"
        :event="eventData"
        :label="event.title"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      />

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
import { bookingStatus } from '@/definitions';
import { computed, inject, ref, toRefs } from 'vue';
import { timeFormat, initialEventPopupData, showEventPopup } from '@/utils';
import CalendarEventPlaceholder from '@/elements/calendar/CalendarEventPlaceholder';
import CalendarEventPreview from '@/elements/calendar/CalendarEventPreview';
import CalendarEventRemote from '@/elements/calendar/CalendarEventRemote';
import CalendarEventScheduled from '@/elements/calendar/CalendarEventScheduled';
import EventPopup from '@/elements/EventPopup';

const dj = inject('dayjs');

// component properties
const props = defineProps({
  day: String, // number of day in its month
  isSelected: Boolean, // flag showing if the event is currently selected by user
  placeholder: Boolean, // flag formating events as placeholder
  monthView: Boolean, // flag, are we in month view?
  event: Object, // the event to show
  showDetails: Boolean, // flag enabling event popups with details
  popupPosition: String, // currently supported: right, left, top
  disabled: Boolean, // flag making this day non-selectable and inactive
  timeSlotDuration: Number, // minimum time shown: [15, 30, 60]
  timeSlotHeight: Number, // height in pixels of each minimum time instance.
});

const { event, timeSlotDuration, timeSlotHeight } = toRefs(props);

const eventData = event.value.customData;
const elementHeight = computed(() => (eventData.duration / timeSlotDuration.value) * timeSlotHeight.value);
const isBusy = computed(() => eventData.slot_status === bookingStatus.booked);

// component emits
const emit = defineEmits(['eventSelected']);

// event details
const popup = ref({ ...initialEventPopupData });

// formatted time range
const formattedTimeRange = (eventObj) => {
  const start = dj(eventObj.time.start);
  const end = dj(eventObj.time.end);
  return `${start.format(timeFormat())} - ${end.format(timeFormat())}`;
};
</script>
