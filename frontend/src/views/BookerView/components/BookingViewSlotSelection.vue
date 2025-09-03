<script setup lang="ts">
import { inject } from 'vue';
import { storeToRefs } from 'pinia';

import { useBookingViewStore } from '@/stores/booking-view-store';
import { useScheduleStore } from '@/stores/schedule-store';
import { DateFormatStrings } from '@/definitions';
import { Slot } from '@/models';
import { dayjsKey } from '@/keys';

import CalendarQalendar from '@/components/CalendarQalendar.vue';
import SlotSelectionAside from './SlotSelectionAside.vue';

const { activeSchedules } = storeToRefs(useScheduleStore());
const { appointment, activeDate, selectedEvent } = storeToRefs(useBookingViewStore());
const dj = inject(dayjsKey);

/**
 * Select a specific time slot
 * @param day string
 */
const selectEvent = (day: string) => {
  // set event selected
  for (let i = 0; i < appointment.value.slots.length; i += 1) {
    const slot: Slot = appointment.value.slots[i];
    if (dj(slot.start).format(DateFormatStrings.Qalendar) === day) {
      slot.selected = true;
      const e = { ...appointment.value, ...slot };
      delete e.slots;
      selectedEvent.value = e;
    } else {
      slot.selected = false;
    }
  }
};

</script>

<template>
  <div v-if="appointment" class="booker-view-container">
    <calendar-qalendar
      class="w-full"
      :current-date="activeDate"
      :appointments="[appointment]"
      :is-booking-route="true"
      :fixed-duration="activeSchedules[0]?.slot_duration"
      @event-selected="selectEvent"
      data-testid="booking-view-calendar-div"
    >
    </calendar-qalendar>

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

@media (--md) {
  .booker-view-container {
    flex-direction: row;
  }
}

</style>