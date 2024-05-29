<template>
  <div
    :class="{ 'text-gray-400 cursor-not-allowed': disabled, 'h-full': !monthView,
    }"
    @mouseleave="popup = {...initialEventPopupData}"
  >
    <div class="flex flex-col gap-1.5 overflow-y-auto"
      :class="{
        'h-full': !monthView,
        'px-1' : isBooked,
      }"
      :style="`height: ${elementHeight}px`"
    >
      <!-- placeholder event for availability bookings -->
      <div
        v-if="placeholder"
        class="m-auto size-[95%] shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200"
        :class="{
          'group/event cursor-pointer rounded-md p-1 hover:bg-gradient-to-b hover:shadow-lg': !isBooked,
          'bg-teal-50 hover:from-teal-500 hover:to-sky-600 hover:!text-white dark:bg-teal-800': !isBooked,
          'bg-gradient-to-b from-teal-500 to-sky-600 shadow-lg': isSelected,
          'h-full rounded': !monthView,
          '!cursor-not-allowed rounded-md bg-gray-100 p-1 dark:bg-gray-600': isBooked,
        }"
        @click="emit('eventSelected', day)"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      >
        <div class="grid">
          <div
            class="
              truncate rounded h-full p-1 font-semibold border-2 border-dashed 
              border-teal-500 group-hover/event:border-white"
            :class="{
              '!border-none': isBooked,
              'border-white': isSelected,
            }"
          >
            <template v-if="isBooked">{{ t('label.busy') }}</template>
            <template v-else>{{ formattedTimeRange(event) }}</template>
          </div>
        </div>
      </div>

      <!-- remote event (can be normal, all_day or tentative) -->
      <div
        v-else-if="eventData.remote"
        class="
          m-auto size-[95%] shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
          flex items-center gap-1.5 px-2 py-0.5
        "
        :class="{
          'rounded bg-amber-400/80 dark:text-white': eventData.all_day,
          'h-full rounded': !monthView,
        }"
        :style="{
          borderColor: eventColor(eventData, false).border,
          backgroundColor: monthView ? eventColor(eventData, false).background : eventData.calendar_color,
          color: !monthView ? getAccessibleColor(eventData.calendar_color) : null,
        }"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      >
        <div
          v-if="!eventData.all_day"
          class="mt-0.5 size-2.5 shrink-0 rounded-full"
          :class="{
            'bg-sky-400': !eventData.tentative,
            'border border-dashed border-sky-400/70': eventData.tentative,
          }"
          :style="{
            borderColor: eventData.tentative ? eventData.calendar_color : null,
            backgroundColor: !eventData.tentative ? eventData.calendar_color : null,
            color: !eventData.tentative ? getAccessibleColor(eventData.calendar_color) : null,
          }"
        ></div>
        <div class="grid">
          <div class="truncate rounded">
            {{ event.title }}
          </div>
        </div>
      </div>

      <!-- live preview event (e.g. for schedule calendar) -->
      <div
        v-else-if="eventData.preview"
        class="
          m-auto size-[95%] shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
          flex items-center rounded border-l-4 border-teal-400 px-2
        "
        :class="{ 'h-full': !monthView }"
        :style="{
          borderColor: eventColor(eventData, false).border,
          backgroundColor: monthView ? eventColor(eventData, false).background : eventData.calendar_color,
          color: !monthView ? getAccessibleColor(eventData.calendar_color) : null,
        }"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      >
        <div class="grid">
          <div class="truncate rounded">
            {{ formattedTimeRange(event) }}
          </div>
        </div>
      </div>

      <!-- scheduled event -->
      <div
        v-else
        class="
          m-auto size-[95%] shrink-0 text-sm text-gray-700 hover:shadow-md dark:text-gray-200
          rounded border-2 border-dashed border-sky-400 bg-sky-400/10 px-2 py-0.5
        "
        :class="{ 'h-full': !monthView }"
        :style="{
          borderColor: eventColor(eventData, false).border,
          backgroundColor: monthView ? eventColor(eventData, false).background : eventData.calendar_color,
          color: !monthView ? getAccessibleColor(eventData.calendar_color) : null,
        }"
        @mouseenter="element => showDetails ? popup=showEventPopup(element, event, popupPosition) : null"
      >
        <div class="grid">
          <div class="truncate rounded">
            {{ event.title }}
          </div>
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
  eventColor, timeFormat, initialEventPopupData, showEventPopup, getAccessibleColor,
} from '@/utils';
import {
  computed, inject, ref, toRefs,
} from 'vue';
import { useI18n } from 'vue-i18n';
import EventPopup from '@/elements/EventPopup';
import { bookingStatus } from '@/definitions';

const { t } = useI18n();
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
const isBooked = computed(() => eventData.slot_status === bookingStatus.booked);

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
