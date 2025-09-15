<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { dayjsKey } from '@/keys';
import { useAppointmentStore } from '@/stores/appointment-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useScheduleStore } from '@/stores/schedule-store';
import { useUserStore } from '@/stores/user-store';
import EventPopup from '@/elements/EventPopup.vue';
import { initialEventPopupData, showEventPopup, darkenColor, hexToRgba } from '@/utils';
import { EventPopup as EventPopupType } from '@/models';
import { ColourSchemes } from '@/definitions';

enum Weekday {
  DayOfTheWeek = 0,
  DayOfTheMonth = 1,
}

const props = defineProps<{
  activeDateRange: {
    start: string,
    end: string
  }
}>();

const dj = inject(dayjsKey);

const userStore = useUserStore();
const appointmentStore = useAppointmentStore();
const scheduleStore = useScheduleStore();
const calendarStore = useCalendarStore();

const { remoteEvents } = storeToRefs(calendarStore);
const { pendingAppointments } = storeToRefs(appointmentStore);
const { firstSchedule } = storeToRefs(scheduleStore);

const popup = ref<EventPopupType>({ ...initialEventPopupData });

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
 */
function calculateEventGridPosition(eventStart, eventEnd, slots) {
  if (!slots.length) return null;

  // Create a quick lookup map for slot start times to grid rows
  const timeToRowMap = new Map(slots.map(s => [s.startTime, s.gridRowStart]));
  const lastRow = slots[slots.length - 1].gridRowEnd;

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

  // 2. Calculate the Start Row
  const startHourMinute = eventStart.format('HH:mm');
  const gridRowStart = timeToRowMap.get(startHourMinute);

  // 3. Calculate the End Row
  // Find the first slot that starts AT or AFTER the event ends
  const endSlot = slots.find(slot => slot.startTime >= eventEnd.format('HH:mm'));
  const gridRowEnd = endSlot ? endSlot.gridRowStart : lastRow;

  // Return the positioning data, only if it's within calendar hours
  if (gridRowStart && gridRowEnd) {
    return {
      gridColumn,
      gridRowStart,
      gridRowEnd,
    };
  }

  return null;
}

/**
 * Weekdays is an array of arrays like [["SUN", 17], ["MON", 18], ..., ["SAT", 23]]
 */
const weekdays = computed(() => {
  const { start, end } = props.activeDateRange;

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
 * Generates an array of time slot objects, each with grid positioning info
 */
const timeSlotsForGrid = computed(() => {
  const slots = [];

  // For FTUE for example, we don't have a firstSchedule yet,
  // so we can initialize the time with a default 9-5 in 24 hrs format, 30 min duration
  const { start_time, end_time, slot_duration } = firstSchedule.value || {
    start_time: '9:00',
    end_time: '17:00',
    slot_duration: 30
  };

  if (!start_time || !end_time || !slot_duration) return [];

  const startTime = dj(start_time, 'H:mm');
  let endTime = dj(end_time, 'H:mm');

  // If the end time is before the start time (slot spans midnight), add a day to the end time
  if (endTime.isBefore(startTime) || endTime.isSame(startTime)) {
    endTime = endTime.add(1, 'day');
  }

  let currentTime = startTime;

  // Start grid rows at 2 to leave space for the header row
  let rowIndex = 2;

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

    currentTime = currentTime.add(slot_duration, 'minute');
    rowIndex++;
  }

  return slots;
});

/**
 * Generates an array of remote events that fall within the active week with grid positioning info
 * Note we are still fetching monthly events to reduce the roundtrips
 */
const filteredRemoteEventsForGrid = computed(() => {
  const slots = timeSlotsForGrid.value;
  if (!slots.length) return [];

  const { start, end } = props.activeDateRange;
  const remoteEventsWithinActiveWeek = remoteEvents.value.filter((remoteEvent) => dj(remoteEvent.start).isBetween(start, end))

  return remoteEventsWithinActiveWeek.map(remoteEvent => {
    const eventStart = dj(remoteEvent.start);
    const eventEnd = dj(remoteEvent.end);

    const gridPosition = calculateEventGridPosition(eventStart, eventEnd, slots);

    if (gridPosition) {
      return {
        ...remoteEvent,
        ...gridPosition,
      };
    }
  }).filter(Boolean)
})

/**
 * Generates an array of pending appointments that fall within the active week with grid positioning info
 */
const filteredPendingAppointmentsForGrid = computed(() => {
  const slots = timeSlotsForGrid.value;
  if (!slots.length) return [];

  const { start, end } = props.activeDateRange;
  const pendingAppointmentsWithinActiveWeek = pendingAppointments.value.filter((appointment) => {
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
})
</script>

<template>
  <div class="calendar-container" :style="{ 'grid-template-rows': `auto repeat(${timeSlotsForGrid.length}, minmax(50px, min-content))` }">
    <!-- Header / First row -->
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

    <!-- Left-side hourly blocks -->
    <div
      v-for="timeSlot in timeSlotsForGrid"
      class="time-slot-cell"
      :key="timeSlot.startTime"
      :style="{ gridRow: `${timeSlot.gridRowStart} / ${timeSlot.gridRowEnd}`, gridColumn: 1 }"
    >
      {{  timeSlot.text }}
    </div>

    <!-- Remote events -->
    <div
      v-for="remoteEvent in filteredRemoteEventsForGrid"
      :key="remoteEvent?.start"
      class="event-item"
      :style="{
        gridColumn: remoteEvent?.gridColumn,
        gridRow: `${remoteEvent?.gridRowStart} / ${remoteEvent?.gridRowEnd}`,
        backgroundColor: remoteEvent?.calendar_color,
        borderLeftColor: darkenColor(remoteEvent?.calendar_color, 30)
      }"
      @mouseenter="(event) => onRemoteEventMouseEnter(event, remoteEvent)"
      @mouseleave="onRemoteEventMouseLeave"
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
        gridRow: `${pendingAppointment?.gridRowStart} / ${pendingAppointment?.gridRowEnd}`,
        backgroundColor: hexToRgba(pendingAppointment?.calendar_color, 0.4),
        borderColor: darkenColor(pendingAppointment?.calendar_color, 30),
      }"
      @mouseenter="(event) => onRemoteEventMouseEnter(event, pendingAppointment)"
      @mouseleave="onRemoteEventMouseLeave"
    >
      {{ pendingAppointment?.title }}
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
    <!-- 8 instead of 7 here because we want to add border to the right most edge and we start at 2 -->
    <div
      v-for="n in 8"
      :key="`line-${n}`"
      class="vertical-line"
      :style="{ gridColumn: n + 1, gridRow: '2 / -1' }"
    ></div>

    <!-- Inner grid horizontal lines -->
    <div
      v-for="timeSlot in timeSlotsForGrid"
      :key="`h-line-${timeSlot.startTime}`"
      class="horizontal-line"
      :style="{ gridRow: timeSlot.gridRowStart, gridColumn: '2 / -1' }"
    ></div>

    <!-- Last horizontal line, dynamically calculated based on time schedule -->
    <div
      class="horizontal-line"
      :style="{
        gridRow: timeSlotsForGrid[timeSlotsForGrid.length - 1]?.gridRowStart + 1,
        gridColumn: '2 / -1'
      }"
    ></div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.calendar-container {
  display: grid;
  grid-template-columns: max-content repeat(7, 200px);
  justify-items: center;
  border: 1px solid var(--colour-neutral-border);
  border-radius: 1.5rem;
  background-color: var(--colour-neutral-base);
  margin-block-end: 2rem;
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
  width: 100%;
  max-width: 100%;
}

.calendar-weekday-header {
  grid-row: 1;
  position: sticky;
  top: 0;
  z-index: 3;
  padding-block: 1rem;
  text-align: center;
  font-weight: bold;
  width: 100%;
  background-color: var(--colour-neutral-base);
  color: var(--colour-ti-secondary);
  position: sticky;
  left: 0;
  min-width: 200px;

  /* Weekday */
  & :first-child {
    font-weight: normal;
    font-size: 0.68rem;
  }
}

.corner-cell-block {
  background-color: var(--colour-neutral-base);
  grid-row: 1;
  grid-column: 1;
  position: sticky;
  top: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  position: sticky;
  left: 0;
}

.time-slot-cell {
  padding-inline: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  position: sticky;
  left: 0;
  background-color: var(--colour-neutral-base);
  color: var(--colour-ti-secondary);
  font-size: 0.68rem;
  z-index: 9;
}

.event-item {
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0.5rem;
  color: #4C4D58; /* TODO: should be --colour-ti-secondary but we don't have dark mode defined yet */
  font-size: 0.68rem;
  border-left: solid 3px;
  border-top: 1px solid var(--colour-neutral-border);
  border-radius: 3px;
  cursor: pointer;
  z-index: 1;
  min-width: 200px;
}

.pending-appointment {
  border: 2px dashed;

  &.dark {
    color: var(--colour-ti-black);
  }
}

.vertical-line {
  justify-self: flex-start;
  border-left: 1px solid var(--colour-neutral-border);
  z-index: 1;
}

.horizontal-line {
  height: 1px;
  background-color: var(--colour-neutral-border);
  width: 100%;
}

@media (--md) {
  .calendar-container {
    grid-template-columns: max-content repeat(7, minmax(0, 1fr));
    overflow-x: visible;
    padding: 1rem 1rem 1.5rem 1rem;
  }

  .calendar-weekday-header {
    position: sticky;
    left: auto;
    min-width: auto;
  }

  .corner-cell-block {
    position: sticky;
    left: auto;
    z-index: 3;
  }

  .time-slot-cell {
    position: static;
    left: auto;
    background-color: transparent;
    z-index: auto;
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