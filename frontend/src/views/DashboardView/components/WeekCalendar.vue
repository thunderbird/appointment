<script setup lang="ts">
import { computed, inject, nextTick, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { dayjsKey } from '@/keys';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { useUserStore } from '@/stores/user-store';
import EventPopup from '@/elements/EventPopup.vue';
import { initialEventPopupData, showEventPopup } from '@/utils';
import { Appointment, EventPopup as EventPopupType, RemoteEvent, Slot } from '@/models';
import { BookingStatus, ColourSchemes, DateFormatStrings } from '@/definitions';
import { Dayjs } from 'dayjs';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';

// Constants for grid calculations
const ROW_HEIGHT_PX = 60; // Matches minmax(60px, min-content) in grid-template-rows

enum Weekday {
  DayOfTheWeek = 0,
  DayOfTheMonth = 1,
}

interface Props {
  activeDateRange: {
    start: string,
    end: string
  },
  events?: RemoteEvent[],
  pendingAppointments?: Appointment[],
  selectableSlots?: Slot[],
  isLoading?: boolean,
}

const props = withDefaults(defineProps<Props>(), {
  events: () => [] as RemoteEvent[],
  pendingAppointments: () => [] as Appointment[],
  selectableSlots: () => [] as Slot[],
  isLoading: false,
});

const emit = defineEmits(['event-selected'])

const dj = inject(dayjsKey);

const userStore = useUserStore();

const { selectedEvent } = storeToRefs(useBookingViewStore());

const calendarContainerRef = ref<HTMLElement | null>(null);
const calendarHeaderRef = ref<HTMLElement | null>(null);
const popup = ref<EventPopupType>({ ...initialEventPopupData });

// Scroll sync state
let pendingScrollSync: number | null = null;
let lastScrollSource: 'header' | 'body' | null = null;
let isProgrammaticScroll = false;

/**
 * Syncs horizontal scroll between header and body for mobile
 * Uses requestAnimationFrame to batch updates and prevent layout thrashing
 */
function syncScroll(source: 'header' | 'body') {
  // Ignore scroll events triggered by our own programmatic updates
  if (isProgrammaticScroll) return;

  lastScrollSource = source;

  // If we already have a pending frame, don't schedule another
  if (pendingScrollSync !== null) return;

  pendingScrollSync = requestAnimationFrame(() => {
    const header = calendarHeaderRef.value;
    const body = calendarContainerRef.value;

    if (header && body && lastScrollSource) {
      isProgrammaticScroll = true;

      if (lastScrollSource === 'header') {
        body.scrollLeft = header.scrollLeft;
      } else {
        header.scrollLeft = body.scrollLeft;
      }

      // Reset flag after a microtask to allow the scroll event to fire and be ignored
      queueMicrotask(() => {
        isProgrammaticScroll = false;
      });
    }

    pendingScrollSync = null;
    lastScrollSource = null;
  });
}

const isDarkMode = computed(() => userStore.myColourScheme === ColourSchemes.Dark);

function onRemoteEventMouseEnter(event: MouseEvent, remoteEvent) {
  const popupEvent = {
    ...remoteEvent,
    time: {
      start: remoteEvent.start,
      end: remoteEvent.end
    },
    customData: {
      calendar_title: remoteEvent.calendar_title,
    }
  }

  popup.value = showEventPopup(event as any, popupEvent, 'right')
}

function onRemoteEventMouseLeave() {
  popup.value = { ...initialEventPopupData };
}

/**
 * Calculates grid positioning for calendar events
 * Returns position info including calculated height based on duration
 */
function calculateEventGridPosition(eventStart: Dayjs, eventEnd: Dayjs, slots) {
  if (!slots.length) return null;

  // 1. Calculate grid column based on the event's position within the week
  // Get the weekdays array to determine the correct column position
  const { start } = props.activeDateRange;
  const startDate = dj(start);

  // Find the day of the week for this event (0-6, where 0 is the first day of the week)
  const eventDayOfWeek = eventStart.diff(startDate, 'day');

  // Safety check: ensure the event is within the displayed week range
  if (eventDayOfWeek < 0 || eventDayOfWeek > 6) {
    return null;
  }

  const gridColumn = eventDayOfWeek + 2; // +2 to account for the time column (column 1)

  // 2. Calculate the Start Row based on the hour
  const startHour = eventStart.hour();
  const gridRowStart = startHour + 1; // Row 1 is 00:00, Row 2 is 01:00, etc.

  // 3. Calculate vertical offset within the starting row (for events not starting on the hour)
  const startMinutes = eventStart.minute();
  const topOffset = (startMinutes / 60) * ROW_HEIGHT_PX;

  // 4. Calculate event duration and height
  // Handle events that cross midnight
  let durationMinutes = eventEnd.diff(eventStart, 'minute');
  if (durationMinutes <= 0) {
    // Event crosses midnight, calculate duration to end of day
    durationMinutes = (24 * 60) - (startHour * 60 + startMinutes);
  }

  // Height based on duration with minimum of 1.25rem (approximately 20px, 1rem for text and 0.25rem for padding)
  const calculatedHeight = (durationMinutes / 60) * ROW_HEIGHT_PX;
  const height = `max(1.25rem, ${calculatedHeight}px)`;

  // Return the positioning data if the event falls within calendar hours
  if (gridRowStart >= 1 && gridRowStart <= 24) {
    return {
      gridColumn,
      gridRowStart,
      topOffset: `${topOffset}px`,
      height,
    };
  }

  return null;
}

/**
 * Weekdays is an array of arrays like [["SUN", 17], ["MON", 18], ..., ["SAT", 23]]
 */
const weekdays = computed(() => {
  const { start, end } = props.activeDateRange;

  // Access language setting to trigger recomputation when locale changes
  // The actual locale is set globally on dayjs, but we need this reactive dependency
  void userStore.data.settings.language;

  // Parse the start and end dates using dayjs's automatic parsing
  const startDate = dj(start);
  const endDate = dj(end);

  const days = [];
  let currentDate = startDate;

  // Loop from the start date until it's the same as the end date, inclusive
  while (!currentDate.isAfter(endDate, 'day')) {
    days.push([
      currentDate.format('ddd').toUpperCase(), // Format to 'SUN', 'MON', etc.
      currentDate.date() // Get the day of the month (e.g., 17)
    ]);

    // Move to the next day
    currentDate = currentDate.add(1, 'day');
  }

  return days;
})

/**
 * Generates an array of time slot objects for a full 24-hour day with grid positioning info
 */
const timeSlotsForGrid = computed(() => {
  const slots = [];

  // Always show full 24-hour day with 60-minute intervals
  const startTime = dj('00:00', 'HH:mm');
  const endTime = dj('00:00', 'HH:mm').add(1, 'day');
  const slotDuration = 60;

  let currentTime = startTime;

  // Start grid rows at 1
  let rowIndex = 1;

  while (currentTime.isBefore(endTime)) {
    // Create the slot for the current time
    slots.push({
      // The text to display (e.g., "9 AM" or empty for non-hour slots)
      text: currentTime.minute() === 0 ? currentTime.format('h A') : '',
      // The start time in a consistent format, useful for keys
      startTime: currentTime.format('HH:mm'),
      // Grid properties
      gridRowStart: rowIndex,
      gridRowEnd: rowIndex + 1,
    });

    currentTime = currentTime.add(slotDuration, 'minute');
    rowIndex++;
  }

  return slots;
});

/**
 * Generates an array of pending appointments that fall within the active week with grid positioning info
 */
const filteredPendingAppointmentsForGrid = computed(() => {
  const slots = timeSlotsForGrid.value;
  if (!slots.length) return [];

  const { start, end } = props.activeDateRange;
  const pendingAppointmentsWithinActiveWeek = props.pendingAppointments.filter((appointment) => {
    const appointmentStart = dj(appointment.slots[0].start);
    return appointmentStart.isBetween(start, end, 'day', '[]');
  });

  return pendingAppointmentsWithinActiveWeek.map(appointment => {
    const appointmentStart = dj(appointment.slots[0].start);
    const appointmentEnd = appointmentStart.add(appointment.duration, 'minute');

    const gridPosition = calculateEventGridPosition(appointmentStart, appointmentEnd, slots);

    if (gridPosition) {
      return {
        ...appointment,
        ...gridPosition,

        // Add properties to match the remote event structure for consistent rendering
        title: appointment.title,
        start: appointment.slots[0].start,
        end: appointmentEnd.format(),
        calendar_title: appointment.calendar_title,
        calendar_color: appointment.calendar_color,
      };
    }
  }).filter(Boolean)
});

/**
 * Generates an array of remote events that fall within the active week with grid positioning info
 * Note we are still fetching monthly events to reduce the roundtrips
 */
const filteredRemoteEventsForGrid = computed(() => {
  const slots = timeSlotsForGrid.value;
  if (!slots.length) return [];

  const { start, end } = props.activeDateRange;
  const remoteEventsWithinActiveWeek = props.events.filter((remoteEvent) => dj(remoteEvent.start).isBetween(start, end))

  return remoteEventsWithinActiveWeek.map(remoteEvent => {
    const eventStart = dj(remoteEvent.start);
    const eventEnd = dj(remoteEvent.end);

    const gridPosition = calculateEventGridPosition(eventStart, eventEnd, slots);
    const hasPendingPlaceholder = filteredPendingAppointmentsForGrid.value.find(
      (a) => a.title === remoteEvent.title && eventStart.isSame(a.start)
    );

    // Only show remote event, if we have a valid grid position and if we don't already have calculated
    // a placeholder for a pending (HOLD) event
    if (gridPosition && !hasPendingPlaceholder) {
      return {
        ...remoteEvent,
        ...gridPosition,
      };
    }
  }).filter(Boolean);
});

/**
 * Generates an array of selectable time slots that fall within the active week with grid positioning info
 */
const filteredSelectableSlotsForGrid = computed(() => {
  const slots = timeSlotsForGrid.value;
  if (!slots.length) return [];

  const { start, end } = props.activeDateRange;
  const selectableSlotsWithinActiveWeek = props.selectableSlots
    .filter((slot) => {
      const slotStart = dj(slot.start);
      return slotStart.isBetween(start, end, 'day', '[]');
    })
    .filter((slot) => slot.booking_status !== BookingStatus.Booked);

  return selectableSlotsWithinActiveWeek.map(slot => {
    const slotStart = dj(slot.start);
    const slotEnd = slotStart.add(slot.duration, 'minute');

    const gridPosition = calculateEventGridPosition(slotStart, slotEnd, slots);

    if (gridPosition) {
      return {
        ...slot,
        ...gridPosition,

        // Add properties to match the remote event structure for consistent rendering
        title: slotStart.format('LT'),
        start: slot.start,
        end: slotEnd.format(),
        calendar_title: '',
      };
    }
  }).filter(Boolean)
});

/**
 * Scrolls the calendar to the current time position
 */
function scrollToCurrentTime() {
  if (!calendarContainerRef.value) return;

  const now = dj();
  const currentHour = now.hour();

  // Find the slot that corresponds to the current hour
  const targetTime = `${String(currentHour).padStart(2, '0')}:00`;

  // Find the time slot element using its data-testid
  const targetElement = calendarContainerRef.value.querySelector(`[data-testid="time-${targetTime}"]`);

  if (targetElement) {
    // Get the element's offset position within the container
    const elementTop = (targetElement as HTMLElement).offsetTop;

    // Scroll to position the current time near the top (with some padding for the weekday header)
    calendarContainerRef.value.scrollTop = elementTop - 80;
  }
}

onMounted(() => {
  nextTick(() => {
    scrollToCurrentTime();
  });
});
</script>

<template>
  <div class="calendar-wrapper" :class="{ 'loading': isLoading }">
    <div class="calendar-loading" v-if="isLoading">
      <loading-spinner />
    </div>

    <!-- Header row (separate from scrollable grid) -->
    <div ref="calendarHeaderRef" class="calendar-header" @scroll="syncScroll('header')">
      <div class="corner-cell-block"></div>
      <div
        class="calendar-weekday-header"
        v-for="(weekday, index) in weekdays"
        :key="weekday[Weekday.DayOfTheMonth]"
        :style="{ gridColumn: index + 2 }"
      >
        <p>{{ weekday[Weekday.DayOfTheWeek] }}</p>
        <p>{{ weekday[Weekday.DayOfTheMonth] }}</p>
      </div>
    </div>

    <!-- Scrollable grid body -->
    <div
      ref="calendarContainerRef"
      class="calendar-body"
      :style="{ 'grid-template-rows': `repeat(${timeSlotsForGrid.length}, minmax(60px, min-content))` }"
      @scroll="syncScroll('body')"
    >
      <!-- Left-side hourly blocks -->
      <div
        v-for="timeSlot in timeSlotsForGrid"
        class="time-slot-cell"
        :key="timeSlot.startTime"
        :style="{ gridRow: `${timeSlot.gridRowStart} / ${timeSlot.gridRowEnd}`, gridColumn: 1 }"
        :data-testid="`time-${timeSlot.startTime}`"
      >
        <!-- Omit 12 AM (00:00) label, show other hours at the top of the row -->
        <span v-if="timeSlot.text && timeSlot.startTime !== '00:00'" class="time-label">
          {{ timeSlot.text }}
        </span>
      </div>

      <!-- Remote events -->
      <div
        v-for="remoteEvent in filteredRemoteEventsForGrid"
        :key="remoteEvent?.start"
        class="event-item"
        :class="{ 'dark': isDarkMode }"
        :style="{
          gridColumn: remoteEvent?.gridColumn,
          gridRowStart: remoteEvent?.gridRowStart,
          marginTop: remoteEvent?.topOffset,
          height: remoteEvent?.height,
        }"
        @mouseenter="(event) => onRemoteEventMouseEnter(event, remoteEvent)"
        @mouseleave="onRemoteEventMouseLeave"
        :data-testid="`remote-event-${dj(remoteEvent.start).format(DateFormatStrings.Qalendar)}`"
      >
        {{ remoteEvent?.title }}
      </div>

      <!-- Pending appointments -->
      <div
        v-for="pendingAppointment in filteredPendingAppointmentsForGrid"
        :key="pendingAppointment?.id"
        class="event-item pending-appointment"
        :class="{ 'dark': isDarkMode }"
        :style="{
          gridColumn: pendingAppointment?.gridColumn,
          gridRowStart: pendingAppointment?.gridRowStart,
          marginTop: pendingAppointment?.topOffset,
          height: pendingAppointment?.height,
        }"
        @mouseenter="(event) => onRemoteEventMouseEnter(event, pendingAppointment)"
        @mouseleave="onRemoteEventMouseLeave"
        :data-testid="`pending-appointment-${dj(pendingAppointment.start).format(DateFormatStrings.Qalendar)}`"
      >
        {{ pendingAppointment?.title }}
      </div>

      <!-- Selectable time slots -->
      <div
        v-for="slot in filteredSelectableSlotsForGrid"
        :key="slot?.id"
        class="event-item selectable-slot"
        :class="{ 'dark': isDarkMode, 'selected': (selectedEvent?.start as Dayjs)?.isSame(slot?.start) }"
        :style="{
          gridColumn: slot?.gridColumn,
          gridRowStart: slot?.gridRowStart,
          marginTop: slot?.topOffset,
          height: slot?.height,
        }"
        @click="emit('event-selected', slot.start)"
        :data-testid="`event-${dj(slot.start).format(DateFormatStrings.Qalendar)}`"
      >
        {{ slot?.title }}
      </div>

      <!-- Event popup (appears on remote event hover) -->
      <event-popup
        v-if="(popup.event)"
        :style="{
          display: popup.display,
          top: popup.top,
          left: popup.left,
          right: popup.right ?? 'initial',
          position: 'fixed',
          zIndex: 10,
        }"
        :event="popup.event"
        :position="popup.position || 'right'"
      />

      <!-- Inner grid vertical lines -->
      <div
        v-for="n in 8"
        :key="`line-${n}`"
        class="vertical-line"
        :style="{ gridColumn: n + 1, gridRow: '1 / -1' }"
      ></div>

      <!-- Inner grid horizontal lines (skip first since header has border-block-end) -->
      <div
        v-for="timeSlot in timeSlotsForGrid.slice(1)"
        :key="`h-line-${timeSlot.startTime}`"
        class="horizontal-line"
        :style="{ gridRow: timeSlot.gridRowStart, gridColumn: '2 / -1' }"
      ></div>
    </div>

    <div class="calendar-footer">
      <div class="corner-cell-block"></div>
      <hr class="calendar-container-bottom-border" />
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.calendar-wrapper {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--colour-neutral-border);
  border-radius: 1.5rem;
  background-color: var(--colour-neutral-base);
  width: 100%;
  max-width: 100%;
  min-height: 505px;
  max-height: calc(100dvh - 400px);
  overflow: hidden;
  padding: 1rem;
  padding-block-start: 0;
  position: relative;

  &.loading {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }

  .calendar-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10;
  }
}

.calendar-header {
  display: grid;
  grid-template-columns: 4rem repeat(7, 200px);
  justify-items: center;
  background-color: var(--colour-neutral-base);
  flex-shrink: 0;
  overflow-x: auto;

  /* Hide scrollbar but keep scrolling functional */
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.calendar-body {
  display: grid;
  grid-template-columns: 4rem repeat(7, 200px);
  justify-items: center;
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
  position: relative;

  /* Hide scrollbar but keep scrolling functional */
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.calendar-weekday-header {
  padding-block-start: 2rem;
  padding-block-end: 1rem;
  text-align: center;
  font-weight: bold;
  width: 100%;
  background-color: var(--colour-neutral-base);
  color: var(--colour-ti-secondary);
  min-width: 200px;
  border-block-end: 1px solid var(--colour-neutral-border);

  /* Weekday */
  & :first-child {
    font-weight: normal;
    font-size: 0.68rem;
  }
}

.corner-cell-block {
  background-color: var(--colour-neutral-base);
  grid-column: 1;
  width: 100%;
  height: 100%;
  position: sticky;
  left: 0;
  z-index: 2;
}

.time-slot-cell {
  padding-inline: 1rem;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  width: 100%;
  height: 100%;
  position: sticky;
  left: 0;
  background-color: var(--colour-neutral-base);
  color: var(--colour-ti-secondary);
  font-size: 0.68rem;
  z-index: 9;

  .time-label {
    transform: translateY(-50%);
  }
}

.event-item {
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-block-start: 0.125rem;
  padding-inline-start: 0.25rem;
  color: var(--colour-ti-secondary);
  font-size: 0.68rem;
  border-left: solid 3px var(--colour-primary-default);
  border-top: 1px solid var(--colour-neutral-border);
  border-radius: 3px;
  background-color: #d4ebfa; /* One-off colour not in design system */
  cursor: pointer;
  z-index: 1;
  min-width: 200px;
  align-self: start;
  box-sizing: border-box;

  &.dark {
    background-color: #d4ebfa19; /* One-off colour not in design system */
  }
}

.pending-appointment {
  border: 1px dashed color-mix(in srgb, var(--colour-primary-default) 66%, transparent);
  background-color: color-mix(in srgb, var(--colour-primary-default) 19%, transparent);

  &.dark {
    border-color: var(--colour-primary-default);
  }
}

.selectable-slot {
  border: 1px dashed color-mix(in srgb, var(--colour-primary-default) 66%, transparent);
  margin: .125rem;
  width: 90%;

  &.selected {
    background-color: var(--colour-accent-blue) !important; /* TODO: Update this once design is ready */
  }
}

.vertical-line {
  justify-self: flex-start;
  border-left: 1px solid var(--colour-neutral-border);
  position: relative;
  z-index: 1;
}

.horizontal-line {
  height: 1px;
  background-color: var(--colour-neutral-border);
  width: 100%;
  position: relative;
  z-index: 1;
}

.calendar-footer {
  display: grid;
  grid-template-columns: 4rem repeat(7, minmax(0, 1fr));

  .calendar-container-bottom-border {
    border: none;
    border-block-end: 1px solid var(--colour-neutral-border);
    grid-column: 2 / -1;
  }
}

@media (--md) {
  .calendar-header {
    grid-template-columns: 4rem repeat(7, minmax(0, 1fr));
    overflow-x: visible;
  }

  .calendar-body {
    grid-template-columns: 4rem repeat(7, minmax(0, 1fr));
    overflow-x: visible;
  }

  .calendar-weekday-header {
    min-width: auto;
  }

  .time-slot-cell {
    position: static;
    left: auto;
    background-color: transparent;
    z-index: auto;

    .time-label {
      transform: translateY(-50%);
    }
  }

  .event-item {
    min-width: auto;
    z-index: 4;
  }

  .vertical-line {
    z-index: 3;
  }
}
</style>
