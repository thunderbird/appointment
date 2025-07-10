<script setup lang="ts">
import { ref, inject, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';

import {
  BookingStatus,
  BookingsTableColumns,
  BookingsViewTypes,
} from '@/definitions';
import { timeFormat, enumToObject } from '@/utils';
import AppointmentModal from '@/components/AppointmentModal.vue';
import BookingsMultiSelectFilter from '@/components/BookingsMultiSelectFilter.vue';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey, refreshKey } from '@/keys';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject(dayjsKey);
const refresh = inject(refreshKey);
const columns = enumToObject(BookingsTableColumns);

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

// Helper function to get display label for booking status
const getStatusLabel = (status: number) => {
  switch (status) {
    case BookingStatus.Requested:
      return t('label.pending');
    case BookingStatus.Booked:
      return t('label.confirmed');
    default:
      return t('label.unknown');
  }
};

// handle data view
const view = ref(BookingsViewTypes.List);

// handle view adjustments: column visibility
const visibleColumns = ref(Object.values(columns));
const columnVisible = (key: string) => visibleColumns.value.includes(columns[key]);

// handle filtered appointments list
const filteredAppointments = computed(() => {
  let list = appointments.value ? [...appointments.value] : [];

  // Filter by selected status filters
  if (selectedFilters.value.length > 0) {
    list = list.filter((a) => {
      const status = a.slots[0].booking_status;
      return selectedFilters.value.includes(status);
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
    <div class="mx-auto flex flex-col items-center gap-8 lg:mx-0 lg:flex-row">
      <bookings-multi-select-filter :options="filterOptions" :selected="selectedFilters"
        @update:selected="selectedFilters = $event" />
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
            <th class="py-1"></th>
            <template v-for="(_, key) in columns" :key="key">
              <th v-if="columnVisible(key)" class="group px-2 py-1 text-left font-normal">
                <div class="border-r border-gray-300 py-1 group-last:border-none dark:border-gray-500">
                  {{ t("label." + key) }}
                </div>
              </th>
            </template>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(appointment, i) in filteredAppointments" :key="i"
            class="cursor-pointer hover:bg-sky-400/10 hover:shadow-lg" @click="showAppointmentModal(appointment)">
            <td class="align-middle">
              <div class="mx-auto size-3 rounded-full bg-sky-400"
                :style="{ backgroundColor: appointment.calendar_color }">
              </div>
            </td>
            <td v-if="columnVisible('title')" class="max-w-2xs truncate p-2">
              <span>{{ appointment.title }}</span>
            </td>
            <td v-if="columnVisible('status')" class="p-2 text-sm">
              <span>{{ getStatusLabel(appointment?.slots[0].booking_status) }}</span>
            </td>
            <td v-if="columnVisible('calendar')" class="p-2 text-sm">
              <span>{{ appointment.calendar_title }}</span>
            </td>
            <td v-if="columnVisible('time')" class="p-2 text-sm">
              <div>{{ dj(appointment?.slots[0].start).format('LL') }}</div>
              <div>
                {{ dj(appointment?.slots[0].start).format(timeFormat()) }}
                {{ t('label.to') }}
                {{ dj(appointment?.slots[0].start).add(appointment?.slots[0].duration, 'minutes').format(timeFormat())
                }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <appointment-modal :open="showAppointment !== null" :appointment="showAppointment" @close="closeAppointmentModal" />
</template>
