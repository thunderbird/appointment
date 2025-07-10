<script setup lang="ts">
import { ref, inject, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';

import {
  BookingStatus,
  BookingsViewTypes,
} from '@/definitions';
import { timeFormat } from '@/utils';
import AppointmentModal from '@/components/AppointmentModal.vue';
import BookingsMultiSelectFilter from '@/components/BookingsMultiSelectFilter.vue';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey, refreshKey } from '@/keys';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject(dayjsKey);
const refresh = inject(refreshKey);

const appointmentStore = useAppointmentStore();
const { appointments } = storeToRefs(appointmentStore);

// Define filter options mapping to existing BookingStatus
const filterOptions = [
  { value: BookingStatus.Requested, label: t('label.pending') },
  { value: BookingStatus.Booked, label: t('label.confirmed') },
  { value: 'declined', label: t('label.declined') }, // Placeholder
  { value: 'cancelled', label: t('label.cancelled') }, // Placeholder
];

// Default selected filters: Pending and Confirmed
const selectedFilters = ref([BookingStatus.Requested, BookingStatus.Booked]);

// Handle sorting by unconfirmed first
const unconfirmedFirst = ref(false);

// Handle data view
const view = ref(BookingsViewTypes.List);

// Handle filtered appointments list
const filteredAppointments = computed(() => {
  let list = appointments.value ? [...appointments.value] : [];

  // Filter by selected status filters
  if (selectedFilters.value.length > 0) {
    list = list.filter((a) => {
      const status = a.slots[0].booking_status;
      return selectedFilters.value.includes(status);
    });
  }

  // Sort by unconfirmed first if checkbox is checked
  if (unconfirmedFirst.value) {
    list.sort((a, b) => {
      const aIsUnconfirmed = a.slots[0].booking_status === BookingStatus.Requested;
      const bIsUnconfirmed = b.slots[0].booking_status === BookingStatus.Requested;

      if (aIsUnconfirmed && !bIsUnconfirmed) return -1;
      if (!aIsUnconfirmed && bIsUnconfirmed) return 1;

      return 0;
    });
  }

  return list;
});

// handle single appointment modal
const showAppointment = ref(null);
const showAppointmentModal = (appointment) => {
  showAppointment.value = appointment;
  router.replace(`/appointments/${appointment.slug}`);
};
const closeAppointmentModal = () => {
  showAppointment.value = null;

  // Shuffle them back to the appointments route.
  router.replace(`/appointments`);
};

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();

  // If we've got a slug
  if (route.params?.slug) {
    showAppointmentModal(appointments.value.filter((appointment) => appointment.slug === route.params.slug)[0]);
  }
});
</script>

<template>
  <!-- page title area -->
  <div class="flex select-none flex-col items-center justify-between text-center lg:flex-row">
    <div class="mb-8 text-4xl font-light lg:mb-0">{{ t('label.appointments') }}</div>
    <div class="mx-auto flex flex-col items-center gap-4 lg:mx-0 lg:flex-row">
      <bookings-multi-select-filter :options="filterOptions" :selected="selectedFilters"
        @update:selected="selectedFilters = $event" />
      <label class="flex items-center gap-2 cursor-pointer">
        <input 
          type="checkbox" 
          v-model="unconfirmedFirst"
          class="sort-checkbox"
        />
        <span class="sort-label">{{ t('label.unconfirmedFirst') }}</span>
      </label>
    </div>
  </div>
  <!-- page content -->
  <div class="mt-8 flex flex-col justify-between gap-4 lg:flex-row xl:gap-24">
    <!-- main section: list/grid of appointments with filter -->
    <div class="w-full">
      <!-- appointments list -->
      <table v-show="view === BookingsViewTypes.List" class="mt-4 w-full"
        data-testid="bookings-appointments-list-table">
        <thead>
          <tr class="bg-gray-100 dark:bg-gray-600">
            <th class="group px-2 py-1 text-left font-normal">
              <div class="border-r border-gray-300 py-1 dark:border-gray-500">
                {{ t("label.date") }}
              </div>
            </th>
            <th class="group px-2 py-1 text-left font-normal">
              <div class="border-r border-gray-300 py-1 dark:border-gray-500">
                {{ t("label.time") }}
              </div>
            </th>
            <th class="group px-2 py-1 text-left font-normal">
              <div class="border-r border-gray-300 py-1 capitalize dark:border-gray-500">
                {{ t("label.meetingTitle") }}
              </div>
            </th>
            <th class="group px-2 py-1 text-left font-normal min-w-[120px]">
              <div class="border-r border-gray-300 py-1 dark:border-gray-500">
                &nbsp;
              </div>
            </th>
            <th class="group px-2 py-1 text-left font-normal">
              <div class="py-1">
                {{ t("label.calendar") }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(appointment, i) in filteredAppointments" :key="i"
            class="cursor-pointer hover:bg-sky-400/10 hover:shadow-lg" @click="showAppointmentModal(appointment)">
            <td class="p-2 text-sm">
              <span>{{ dj(appointment?.slots[0].start).format('LL') }}</span>
            </td>
            <td class="p-2 text-sm">
              <span>
                {{ dj(appointment?.slots[0].start).format(timeFormat()) }}
                {{ t('label.to') }}
                {{ dj(appointment?.slots[0].start).add(appointment?.slots[0].duration, 'minutes').format(timeFormat()) }}
              </span>
            </td>
            <td class="max-w-2xs truncate p-2">
              <span>{{ appointment.title }}</span>
            </td>
            <td class="p-2 text-sm uppercase text-center min-w-[120px]">
              <span v-if="appointment?.slots[0].booking_status === BookingStatus.Requested">{{ t('label.unconfirmed') }}</span>
            </td>
            <td class="p-2 text-sm">
              <span>{{ appointment.calendar_title }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <appointment-modal :open="showAppointment !== null" :appointment="showAppointment" @close="closeAppointmentModal" />
</template>

<style scoped>
.sort-checkbox {
  height: 1rem;
  width: 1rem;
  border-radius: 0.25rem;
  border: 1px solid var(--colour-neutral-border);
  background-color: var(--colour-neutral-base);
  color: var(--colour-primary-default);
  cursor: pointer;
  transition: all 0.2s;
}

.sort-checkbox:focus {
  outline: 2px solid var(--colour-primary-default);
  outline-offset: 2px;
}

.sort-checkbox:checked {
  background-color: var(--colour-primary-default);
  border-color: var(--colour-primary-default);
}

.sort-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--colour-ti-base);
  cursor: pointer;
}
</style>
