<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import { SegmentedControl, SelectInput } from '@thunderbirdops/services-ui';
import { useAppointmentStore } from '@/stores/appointment-store';
import { BookingsFilterOptions, BookingsSortOptions } from '@/definitions';
import AppointmentSlidingPanel from './components/AppointmentSlidingPanel.vue';
import DateRequestedAppointments from './components/DateRequestedAppointments.vue';
import MeetingDateAppointments from './components/MeetingDateAppointments.vue';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const appointmentStore = useAppointmentStore();
const { 
  appointments,
  selectedAppointment,
  isLoading,
} = storeToRefs(appointmentStore);

/* Appointment Sliding Panel */
const appointmentSlidingPanelRef = ref<InstanceType<typeof AppointmentSlidingPanel>>()

const showAppointmentSlidingPanel = async (appointment) => {
  selectedAppointment.value = appointment;
  appointmentSlidingPanelRef.value?.showPanel()

  router.replace({
    name: 'bookings',
    params: { slug: appointment.slug },
    query: route.query
  });
};

const handleCloseAppointmentSlidingPanel = () => {
  selectedAppointment.value = null;

  router.replace({
    path: '/bookings',
    query: route.query
  });
};

/* Filter Options */
const filterOptions = [{
  label: t('label.showAll'),
  value: BookingsFilterOptions.All,
}, {
  label: t('label.unconfirmed'),
  value: BookingsFilterOptions.Unconfirmed,
}];

const selectedFilter = ref<BookingsFilterOptions>(BookingsFilterOptions.All);

/* Sort Option */
const sortOptions = [{
  label: t('label.dateRequested'),
  value: BookingsSortOptions.DateRequested,
}, {
  label: t('label.meetingDate'),
  value: BookingsSortOptions.MeetingDate,
}];

const selectedSort = ref<BookingsSortOptions>(BookingsSortOptions.DateRequested);

onMounted(async () => {
  if (!appointmentStore.isLoaded) {
    await appointmentStore.fetch();
  }

  // If we've got a slug, already open the Appointment Sliding Panel
  if (route.params?.slug && appointments.value) {
    showAppointmentSlidingPanel(appointments.value.filter((appointment) => appointment.slug === route.params.slug)[0]);
  }
});
</script>

<script lang="ts">
export default {
  name: 'BookingsView'
}
</script>

<template>
  <div class="bookings-page-container">
    <!-- page title area -->
    <h1>{{ t('label.appointments') }}</h1>
  
    <div class="page-controls">
      <segmented-control
        name="unconfirmed-first"
        :required="false"
        :options="filterOptions"
        v-model="selectedFilter"
      />

      <div class="sort-by-container">
        <span>{{ t('label.sortBy') }}:</span>
        <select-input
          name="sort-select"
          :options="sortOptions"
          v-model="selectedSort"
        />
      </div>
    </div>
  
    <!-- page content -->
    <div class="page-content">
      <template v-if="isLoading">
        <loading-spinner />
      </template>

      <div v-else class="appointments-container">
        <date-requested-appointments
          v-if="selectedSort === BookingsSortOptions.DateRequested"
          :filter="selectedFilter"
          @select-appointment="showAppointmentSlidingPanel"
        />
        <meeting-date-appointments
          v-else-if="selectedSort === BookingsSortOptions.MeetingDate"
          :filter="selectedFilter"
          @select-appointment="showAppointmentSlidingPanel"
        />
      </div>
    </div>
  </div>

  <appointment-sliding-panel
    ref="appointmentSlidingPanelRef"
    :appointment="selectedAppointment"
    @close="handleCloseAppointmentSlidingPanel"
  />
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

h1 {
  margin-block-end: 2rem;
  font-family: metropolis;
  font-size: 2.25rem;
  color: var(--colour-ti-base);
}

.page-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 2rem;

  .sort-by-container {
    display: flex;
    align-items: center;
    gap: 0.625rem;
  }
}

.page-content {
  margin-block-start: 1.5rem;
  margin-block-end: 3rem;
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.appointments-container {
  width: 100%;
  box-shadow: 4px 4px 16px 0 rgba(0, 0, 0, 0.04);
  padding: 1rem 0.75rem;
  border-radius: 1.5rem;
  background-color: var(--colour-neutral-base);
}

@media (--md) {
  .bookings-page-container {
    width: 100%;
    max-width: 969px;
    margin: 0 auto;
  }

  .page-controls {
    gap: 0;
  }
}
</style>
