<script setup lang="ts">
import { inject, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { callKey, dayjsKey, refreshKey } from '@/keys';
import { ScheduleAppointment } from '@/models';

import { createScheduleStore } from '@/stores/schedule-store';
import { createCalendarStore } from '@/stores/calendar-store';
import { createAvailabilityStore } from '@/stores/availability-store';

import ScheduleCreation from './components/ScheduleCreation.vue';
import BookingPageDetails from './components/BookingPageDetails.vue';
import BookingPageLink from './components/BookingPageLink.vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';

const { t } = useI18n();

const refresh = inject(refreshKey);
const call = inject(callKey);
const dj = inject(dayjsKey);

const schedulesReady = ref(false);
const scheduleStore = createScheduleStore(call);
const calendarStore = createCalendarStore(call);
const availabilityStore = createAvailabilityStore(call);
const { connectedCalendars } = storeToRefs(calendarStore);
const { firstSchedule } = storeToRefs(scheduleStore);

const activeDate = ref(dj());
const schedulesPreviews = ref([]);

const onScheduleCreationUpdated = (schedule: ScheduleAppointment) => {
  schedulesPreviews.value = schedule ? [schedule] : [];
};

const onSaveChanges = () => {
  console.log("Saved changes!");
}

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
  <h1 class="page-title">{{ t('label.availability') }}</h1>
  <form @submit.prevent>
    <div class="page-content">
      <section>
        <schedule-creation
          v-if="schedulesReady"
          :calendars="connectedCalendars"
          :schedule="firstSchedule"
          :active-date="activeDate"
          @created="scheduleStore.fetch(true)"
          @updated="onScheduleCreationUpdated"
        />
      </section>
  
      <div class="page-content-right">
        <section>
          <booking-page-details />
        </section>
  
        <section>
          <booking-page-link />
        </section>
      </div>
    </div>

    <div class="footer-save-panel" v-if="false">
      <primary-button
        @click="onSaveChanges()"
      >
        {{ t('label.saveChanges') }}
      </primary-button>
    </div>
  </form>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-title {
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

.page-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.page-content-right {
  display: grid;
  gap: 2rem;
  align-self: start;
}

.footer-save-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: flex-end;
  margin-inline-start: auto;
  padding: 1rem 1.5rem;
  margin: 0 0.5rem 0.5rem 0.5rem;
  border-radius: 8px;
  background-color: var(--colour-neutral-lower);
}

section {
  border: 1px solid var(--colour-neutral-border);
  border-radius: 8px;
  padding: 1.5rem;
}

@media (--md) {
  .page-content {
    grid-template-columns: 1fr 1fr;
  }
}
</style>