<script setup lang="ts">
import { inject, computed } from 'vue';
import { storeToRefs } from 'pinia';

import { useBookingViewStore } from '@/stores/booking-view-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { Slot, TimeFormatted } from '@/models';
import { dayjsKey } from '@/keys';

import WeekPicker from '@/views/DashboardView/components/WeekPicker.vue';
import WeekCalendar from '@/views/DashboardView/components/WeekCalendar.vue';
import SlotSelectionAside from './SlotSelectionAside.vue';
import { Dayjs } from 'dayjs';

const calendarStore = useCalendarStore();
const { appointment, activeDate, selectedEvent } = storeToRefs(useBookingViewStore());
const dj = inject(dayjsKey);

// current selected date, defaults to now
const activeDateRange = computed(() => ({
  start: activeDate.value.startOf('week').format('YYYY-MM-DD'),
  end: activeDate.value.endOf('week').format('YYYY-MM-DD'),
}));

/**
 * Select a specific time slot
 * @param day string
 */
const selectEvent = (day: Dayjs) => {
  // set event selected
  for (let i = 0; i < appointment.value.slots.length; i += 1) {
    const slot: Slot = appointment.value.slots[i];
    if (dj(slot.start).isSame(day)) {
      slot.selected = true;
      const e = { ...appointment.value, ...slot };
      delete e.slots;
      selectedEvent.value = e;
    } else {
      slot.selected = false;
    }
  }
};

async function onDateChange(dateObj: TimeFormatted) {
  const start = dj(dateObj.start);
  const end = dj(dateObj.end);

  activeDate.value = start.add(end.diff(start, 'minutes') / 2, 'minutes');

  await calendarStore.getRemoteEvents(activeDate.value);
};

</script>

<template>
  <div v-if="appointment" class="booker-view-container">
    <div class="calendar-container">
      <week-picker
        :active-date-range="activeDateRange"
        :onDateChange="onDateChange"
      />
      <week-calendar
        :active-date-range="activeDateRange"
        :selectable-slots="appointment.slots"
        @event-selected="selectEvent"
      />
    </div>

    <slot-selection-aside />
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.booker-view-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.calendar-container {
  width: 100%;
}

@media (--md) {
  .booker-view-container {
    position: relative;
    flex-direction: row;
    align-items: flex-start;
  }
}

</style>
