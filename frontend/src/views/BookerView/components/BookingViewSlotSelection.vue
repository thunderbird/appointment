<script setup lang="ts">
import { inject, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { Dayjs } from 'dayjs';
import { useI18n } from 'vue-i18n';
import { PhGlobe } from '@phosphor-icons/vue';

import { useBookingViewStore } from '@/stores/booking-view-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store';
import { Slot, TimeFormatted } from '@/models';
import { dayjsKey } from '@/keys';
import { getStartOfWeek, getEndOfWeek } from '@/utils';

import WeekPicker from '@/views/DashboardView/components/WeekPicker.vue';
import WeekCalendar from '@/views/DashboardView/components/WeekCalendar.vue';
import SlotSelectionAside from './SlotSelectionAside.vue';
import SlotSelectionHeader from './SlotSelectionHeader.vue';

const { t } = useI18n();
const calendarStore = useCalendarStore();
const userStore = useUserStore();
const { appointment, activeDate, selectedEvent } = storeToRefs(useBookingViewStore());
const dj = inject(dayjsKey);

// current selected date, defaults to now
const activeDateRange = computed(() => {
  const startOfWeek = userStore.data.settings.startOfWeek ?? 7;
  return {
    start: getStartOfWeek(activeDate.value, startOfWeek).format('YYYY-MM-DD'),
    end: getEndOfWeek(activeDate.value, startOfWeek).format('YYYY-MM-DD'),
  };
});

const timezone = computed(() => dj.tz.guess());

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
  <template v-if="appointment">
    <slot-selection-header />

    <div class="week-picker-container">
      <week-picker
        :active-date-range="activeDateRange"
        :onDateChange="onDateChange"
      />
    </div>

    <div class="booker-view-container">
      <div class="calendar-container">
        <week-calendar
          :active-date-range="activeDateRange"
          :selectable-slots="appointment.slots"
          @event-selected="selectEvent"
        />

        <div class="calendar-footer">
          <ph-globe size="16" />
          <span>{{ t('label.timeZone') }}: {{ timezone }}</span>
        </div>
      </div>

      <slot-selection-aside />
    </div>
  </template>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.booker-view-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.week-picker-container {
  margin-block-end: 2rem;
}

.calendar-container {
  flex: 1;
}

.calendar-footer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-block: 1.25rem;
  font-size: 0.6875rem;
}

@media (--md) {
  .booker-view-container {
    position: relative;
    flex-direction: row;
    align-items: flex-start;
  }
}

</style>
