<script setup lang="ts">
import { ref, inject, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { BaseBadge, BaseBadgeTypes, SegmentedControl, SelectInput, VisualDivider } from '@thunderbirdops/services-ui';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey } from '@/keys';
import AppointmentSlidingPanel from './components/AppointmentSlidingPanel.vue';
import { BookingsFilterOptions, BookingsSortOptions } from '@/definitions';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject(dayjsKey);

const appointmentStore = useAppointmentStore();
const { 
  appointments, 
  selectedAppointment, 
  isLoading, 
  hasMorePages
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
const filterOptions = computed(() => [{
  label: t('label.showAll'),
  value: BookingsFilterOptions.All,
}, {
  label: t('label.unconfirmed'),
  value: BookingsFilterOptions.Unconfirmed,
}])

const selectedFilter = ref<string>(BookingsFilterOptions.All);

/* Sort Option */
const sortOptions = computed(() => [{
  label: t('label.showAll'),
  value: BookingsSortOptions.DateRequested,
}, {
  label: t('label.unconfirmed'),
  value: BookingsSortOptions.MeetingTime,
}])

const selectedSort = ref<string>(BookingsSortOptions.DateRequested);

console.log(appointments.value);

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
        <p class="loading-indicator">{{ t('label.loading') }}</p>
      </template>

      <div v-else class="appointments-container">
        <template v-if="selectedSort === BookingsSortOptions.DateRequested">
          <h2>{{ t('label.today') }}</h2>

          <visual-divider />

          <div class="appointment-item">
            <div>
              <strong>Ben S</strong>
              <p>ben@lumoncorp.com</p>
            </div>

            <div>
              <p>Request date</p>
              <strong>8/12/2025, 11:17 am</strong>
            </div>

            <div>
              <p>Meeting date</p>
              <strong>8/12/2025, 11:17 am</strong>
            </div>

            <base-badge :type="BaseBadgeTypes.NotSet">
              NEEDS CONFIRMATION
            </base-badge>
          </div>
        </template>

        <template v-else-if="selectedSort === BookingsSortOptions.MeetingTime">
        </template>
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

  .sort-by-container {
    display: flex;
    align-items: center;
    gap: 0.625rem;
  }
}

.page-content {
  margin-block: 1.5rem;
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
}

.appointments-container {
  width: 100%;
  box-shadow: 4px 4px 16px 0 rgba(0, 0, 0, 0.04);
  padding: 1rem 0.75rem;
  border-radius: 1.5rem;
  background-color: var(--colour-neutral-base);

  h2 {
    font-size: 1.5rem;
    font-family: metropolis;
    text-align: center;
    margin-bottom: 0.5rem;
  }

  .appointment-item {
    display: grid;
    grid-template-columns: 300px 1fr 1fr auto;
    align-items: center;
    background-color: var(--colour-neutral-lower);
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    font-size: 0.875rem;

    strong {
      font-weight: 600;
      font-size: 1rem;
    }
  }
}

@media (--md) {
  .bookings-page-container {
    width: 100%;
    max-width: 969px;
    margin: 0 auto;
  }
}
</style>
