<script setup lang="ts">
import {
  ref, inject, onMounted, computed,
} from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { dayjsKey, refreshKey } from '@/keys';
import { TimeFormatted } from '@/models';
import QuickActionsSideBar from './components/QuickActionsSideBar.vue';
import WeekPicker from './components/WeekPicker.vue';
import UserCalendarSync from './components/UserCalendarSync.vue';
import WeekCalendar from './components/WeekCalendar.vue';

// stores
import { useCalendarStore } from '@/stores/calendar-store';
import { useAppointmentStore } from '@/stores/appointment-store';

const route = useRoute();
const dj = inject(dayjsKey);
const refresh = inject(refreshKey);

const calendarStore = useCalendarStore();
const appointmentStore = useAppointmentStore();
const { remoteEvents } = storeToRefs(calendarStore);
const { pendingAppointments } = storeToRefs(appointmentStore);

// current selected date, defaults to now
const activeDate = ref(dj());
const activeDateRange = computed(() => ({
  start: activeDate.value.startOf('week').format('YYYY-MM-DD'),
  end: activeDate.value.endOf('week').format('YYYY-MM-DD'),
}));

async function onDateChange(dateObj: TimeFormatted) {
  const start = dj(dateObj.start);
  const end = dj(dateObj.end);

  activeDate.value = start.add(end.diff(start, 'minutes') / 2, 'minutes');

  await calendarStore.getRemoteEvents(activeDate.value);
};

onMounted(async () => {
  // Don't actually load anything during the FTUE
  if (route.name === 'setup') {
    return;
  }

  await refresh();
  await calendarStore.getRemoteEvents(activeDate.value, true);
});
</script>

<script lang="ts">
export default {
  name: 'DashboardView'
}
</script>

<template>
  <div class="main-container">
    <quick-actions-side-bar />
  
    <div class="main-calendar-container">
      <div class="calendar-header-container">
        <week-picker
          :active-date-range="activeDateRange"
          :onDateChange="onDateChange"
        />

        <user-calendar-sync />
      </div>

      <div class="calendar-container">
        <week-calendar
          :active-date-range="activeDateRange"
          :events="remoteEvents"
          :pending-appointments="pendingAppointments"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.main-container {
  display: flex;
  flex-direction: column;
  gap: 2.25rem;
}

.main-calendar-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-block-start: 0.25rem;

  .calendar-container {
    margin-block-end: 2rem;
  }
}

.calendar-header-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  margin-block-end: 1rem;
  gap: 2rem;
}

@media (--md) {
  .main-container {
    flex-direction: row;
    gap: 2rem;
    overflow-y: auto;
  }

  .calendar-header-container {
    flex-direction: row;
    justify-content: space-between;
    margin-block-end: 2.25rem;
    gap: 0;
  }
}
</style>
