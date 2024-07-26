<script setup lang="ts">
import { bookingStatus } from '@/definitions';
import { computed, inject, ref, toRefs } from 'vue';
import { timeFormat, initialEventPopupData, showEventPopup } from '@/utils';
import CalendarEventPlaceholder from '@/elements/calendar/CalendarEventPlaceholder.vue';
import CalendarEventPreview from '@/elements/calendar/CalendarEventPreview.vue';
import CalendarEventRemote from '@/elements/calendar/CalendarEventRemote.vue';
import CalendarEventScheduled from '@/elements/calendar/CalendarEventScheduled.vue';
import EventPopup from '@/elements/EventPopup.vue';
import { CalendarEvent, EventPopup as EventPopupType } from "@/models";
import { dayjsKey } from "@/keys";

const dj = inject(dayjsKey);

// component properties
interface Props {
  day?: string; // number of day in its month
  isSelected: boolean; // flag showing if the event is currently selected by user
  placeholder: boolean; // flag formating events as placeholder
  monthView: boolean; // flag, are we in month view?
  event: CalendarEvent; // the event to show
  showDetails: boolean; // flag enabling event popups with details
  popupPosition?: string; // currently supported: right, left, top
  disabled: boolean; // flag making this day non-selectable and inactive
  timeSlotDuration?: number; // minimum time shown: [15, 30, 60]
  timeSlotHeight?: number; // height in pixels of each minimum time instance.
}
const props = defineProps<Props>();

const { event, timeSlotDuration, timeSlotHeight } = toRefs(props);

const eventData = event.value.customData;
const elementHeight = computed(() => (eventData.duration / timeSlotDuration.value) * timeSlotHeight.value);
const isBusy = computed(() => eventData.slot_status === bookingStatus.booked);

// component emits
const emit = defineEmits(['eventSelected']);

// event details
const popup = ref<EventPopupType>({ ...initialEventPopupData });
const resetPopup = () => {
  popup.value = { ...initialEventPopupData };
};

// formatted time range
const formattedTimeRange = (eventObj: CalendarEvent) => {
  const start = dj(eventObj.time.start);
  const end = dj(eventObj.time.end);
  return `${start.format(timeFormat())} - ${end.format(timeFormat())}`;
};
</script>

<template>
  <div
    :class="{ 'cursor-not-allowed text-gray-400': disabled, 'h-full': !monthView }"
    @mouseleave="resetPopup"
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
        :event-data="eventData"
        :label="event.title"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      />

      <!-- live preview event (e.g. for schedule calendar) -->
      <calendar-event-preview
        v-else-if="eventData.preview"
        :is-month-view="monthView"
        :event-data="eventData"
        :label="formattedTimeRange(event)"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      />

      <!-- scheduled event -->
      <calendar-event-scheduled
        v-else
        :is-month-view="monthView"
        :event-data="eventData"
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
        right: popup.right ?? 'initial',
      }"
      :event="popup.event"
      :position="popupPosition"
    />
  </div>
</template>
