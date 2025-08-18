<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useAppointmentStore } from '@/stores/appointment-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { createScheduleStore } from '@/stores/schedule-store';
import { callKey, dayjsKey } from '@/keys';

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

const call = inject(callKey);
const dj = inject(dayjsKey);

const appointmentStore = useAppointmentStore();
const calendarStore = useCalendarStore();
const scheduleStore = createScheduleStore(call);

const { remoteEvents } = storeToRefs(calendarStore);
const { pendingAppointments } = storeToRefs(appointmentStore);
const { firstSchedule } = storeToRefs(scheduleStore);

// Weekdays is an array of arrays like [["SUN", 17], ["MON", 18], ..., ["SAT", 23]]
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
      currentDate.date()                      // Get the day of the month (e.g., 17)
    ]);

    // Move to the next day
    currentDate = currentDate.add(1, 'day');
  }

  return days;
})

// schedule previews for showing corresponding placeholders in calendar views
const schedulesPreviews = ref([]);
</script>

<template>
  <div class="calendar-container">
    <!-- Header / First row -->
    <br />
    <div
      v-for="weekday in weekdays"
      :key="weekday[Weekday.DayOfTheMonth]"
    >
      <div class="calendar-weekday-header">
        <p>{{ weekday[Weekday.DayOfTheWeek] }}</p>
        <p>{{ weekday[Weekday.DayOfTheMonth] }}</p>
      </div>
    </div>

    <!-- Hourly blocks / From second row onwards -->
    <p>9AM</p>
    
  </div>
</template>

<style scoped>
.calendar-container {
  display: grid;
  grid-template-columns: min-content repeat(7, 1fr);
  justify-items: center;
  border: 1px solid red;

  .calendar-weekday-header {
    padding-block: 0.5rem;
    text-align: center;
  }
}
</style>