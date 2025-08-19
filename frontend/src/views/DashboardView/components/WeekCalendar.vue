<script setup lang="ts">
import { computed, inject } from 'vue';
import { storeToRefs } from 'pinia';
import { dayjsKey } from '@/keys';
import { useAppointmentStore } from '@/stores/appointment-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useScheduleStore } from '@/stores/schedule-store';

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

const appointmentStore = useAppointmentStore();
const scheduleStore = useScheduleStore();
const calendarStore = useCalendarStore();

const { remoteEvents } = storeToRefs(calendarStore);
const { pendingAppointments } = storeToRefs(appointmentStore);
const { firstSchedule } = storeToRefs(scheduleStore);

/**
 * Weekdays is an array of arrays like [["SUN", 17], ["MON", 18], ..., ["SAT", 23]]
 */
const weekdays = computed(() => {
  const { start, end } = props.activeDateRange;

  // Parse the start and end dates from the MM/DD/YYYY format
  const startDate = dj(start, 'MM/DD/YYYY');
  const endDate = dj(end, 'MM/DD/YYYY');

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
  const { start_time, end_time, slot_duration } = firstSchedule.value || {};

  if (!start_time || !end_time || !slot_duration) return [];

  let currentTime = dj(start_time, 'H:mm');
  const finalTime = dj(end_time, 'H:mm');

  // Start grid rows at 2 to leave space for the header row
  let rowIndex = 2;

  while (currentTime.isBefore(finalTime)) {
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

  // Create a quick lookup map for slot start times to grid rows
  const timeToRowMap = new Map(slots.map(s => [s.startTime, s.gridRowStart]));
  const lastRow = slots[slots.length - 1].gridRowEnd;

  return remoteEventsWithinActiveWeek.map(remoteEvent => {
    const eventStart = dj(remoteEvent.start);
    const eventEnd = dj(remoteEvent.end);

    // 1. isoWeekday() returns 1 being Monday and 7 being Sunday but Sunday is the second column
    // if not Sunday, we must offset the column by 2 to skip the time column and the Sunday column
    const isoWeekday = eventStart.isoWeekday();
    const gridColumn = isoWeekday === 7 ? 2 : isoWeekday + 2;

    // 2. Calculate the Start Row
    const startHourMinute = eventStart.format('HH:mm');
    const gridRowStart = timeToRowMap.get(startHourMinute);

    // 3. Calculate the End Row
    // Find the first slot that starts AT or AFTER the event ends
    const endSlot = slots.find(slot => slot.startTime >= eventEnd.format('HH:mm'));
    const gridRowEnd = endSlot ? endSlot.gridRowStart : lastRow;

    // Return the event with positioning data, only if it's within calendar hours
    if (gridRowStart && gridRowEnd) {
      return {
        ...remoteEvent,
        gridColumn,
        gridRowStart,
        gridRowEnd,
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
      v-for="event in filteredRemoteEventsForGrid"
      :key="event?.start"
      class="event-item"
      :style="{
        gridColumn: event?.gridColumn,
        gridRow: `${event?.gridRowStart} / ${event?.gridRowEnd}`,
        backgroundColor: `${event?.calendar_color}`
      }"
    >
      {{ event?.title }}
    </div>

    <!-- Inner grid vertical lines -->
    <div
      v-for="n in 7"
      :key="`line-${n}`"
      class="vertical-line"
      :style="{ gridColumn: n + 1, gridRow: '1 / -1' }"
    ></div>

    <!-- Inner grid horizontal lines -->
    <div
      v-for="timeSlot in timeSlotsForGrid"
      :key="`h-line-${timeSlot.startTime}`"
      class="horizontal-line"
      :style="{ gridRow: timeSlot.gridRowStart, gridColumn: '1 / -1' }"
    ></div>
  </div>
</template>

<style scoped>
.calendar-container {
  display: grid;
  grid-template-columns: max-content repeat(7, minmax(0, 1fr));
  justify-items: center;
  border: 1px solid var(--colour-neutral-border-intense);
  margin-block-end: 2rem;
  flex: 1;
  overflow-y: auto;

  .calendar-weekday-header {
    grid-row: 1;
    position: sticky;
    top: 0;
    z-index: 10;
    padding-block: 0.5rem;
    text-align: center;
    font-weight: bold;
    width: 100%;
    background-color: var(--colour-neutral-base);
    border-inline-start: 1px solid var(--colour-neutral-border-intense);
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
  }

  .time-slot-cell {
    padding-inline: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  .event-item {
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0.5rem;
    color: black;
    font-size: 0.875rem;
    border-top: 1px solid var(--colour-neutral-border-intense);
    cursor: pointer;
    z-index: 2;
  }

  .vertical-line {
    justify-self: flex-start;
    border-left: 1px solid var(--colour-neutral-border-intense);
    z-index: 3;
  }

  .horizontal-line {
    height: 1px;
    background-color: var(--colour-neutral-border-intense);
    width: 100%;
  }
}
</style>