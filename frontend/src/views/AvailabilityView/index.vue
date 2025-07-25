<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { callKey, dayjsKey, refreshKey } from '@/keys';
import { ScheduleAppointment } from '@/models';
import { createScheduleStore } from '@/stores/schedule-store';
import { createCalendarStore } from '@/stores/calendar-store';

import ScheduleCreation from './components/ScheduleCreation.vue';

const refresh = inject(refreshKey);
const call = inject(callKey);
const dj = inject(dayjsKey);

const schedulesReady = ref(false);
const scheduleStore = createScheduleStore(call);
const calendarStore = createCalendarStore(call);
const { connectedCalendars } = storeToRefs(calendarStore);
const { firstSchedule } = storeToRefs(scheduleStore);

const activeDate = ref(dj());
const schedulesPreviews = ref([]);

const onScheduleCreationUpdated = (schedule: ScheduleAppointment) => {
  schedulesPreviews.value = schedule ? [schedule] : [];
};

onMounted(async () => {
  await refresh();

  scheduleStore.fetch();
  schedulesReady.value = true;
});
</script>

<script lang="ts">
export default {
  name: 'AvailabilityView'
}
</script>

<template>
  <section class="availability-section">
    <schedule-creation
      v-if="schedulesReady"
      :calendars="connectedCalendars"
      :schedule="firstSchedule"
      :active-date="activeDate"
      @created="scheduleStore.fetch(true)"
      @updated="onScheduleCreationUpdated"
    />
  </section>
</template>

<style scoped>
.availability-section {
  width: 50%;
}
</style>