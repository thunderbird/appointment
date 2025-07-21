<script setup lang="ts">
import { ref, inject, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { IconCaretUpFilled, IconCaretDownFilled } from '@tabler/icons-vue';
import { CheckboxInput } from '@thunderbirdops/services-ui';
import {
  BookingStatus,
  BookingsViewTypes,
} from '@/definitions';
import { timeFormat } from '@/utils';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey, refreshKey } from '@/keys';

import AppointmentMultiSelectFilter from './components/AppointmentMultiSelectFilter.vue';
import AppointmentSlidingPanel from './components/AppointmentSlidingPanel.vue';

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
  { value: 'declined', label: t('label.declined') }, // TODO: Implement declined status on the backend
  { value: 'cancelled', label: t('label.cancelled') }, // TODO: Implement cancelled status on the backend
];

// Default selected filters: Pending and Confirmed
const selectedFilters = ref([BookingStatus.Requested, BookingStatus.Booked]);

// Handle sorting by unconfirmed first
const unconfirmedFirst = ref(false);

// Handle table column sorting
type TableColumn = 'date' | 'title' | 'calendar';
enum SortDirection {
  Ascending = 'asc',
  Descending = 'desc',
}
const sortColumn = ref<TableColumn>('date');
const sortDirection = ref<SortDirection>(SortDirection.Ascending);

// Handle data view
const view = ref(BookingsViewTypes.List);

// handle appointment sliding panel
const appointmentSlidingPanelRef = ref<InstanceType<typeof AppointmentSlidingPanel>>()

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

  // Sort by table column
  if (sortColumn.value) {
    list.sort((a, b) => {
      let aValue, bValue;

      switch (sortColumn.value) {
        case 'date':
          // Sort by date and time combined
          aValue = a.slots[0].start.valueOf();
          bValue = b.slots[0].start.valueOf();
          break;
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'calendar':
          aValue = a.calendar_title.toLowerCase();
          bValue = b.calendar_title.toLowerCase();
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortDirection.value === SortDirection.Ascending ? -1 : 1;
      if (aValue > bValue) return sortDirection.value === SortDirection.Ascending ? 1 : -1;

      return 0;
    });
  }

  if (unconfirmedFirst.value) {
    list = list.sort((a, b) => {
      const aIsUnconfirmed = a.slots[0].booking_status === BookingStatus.Requested;
      const bIsUnconfirmed = b.slots[0].booking_status === BookingStatus.Requested;

      if (aIsUnconfirmed && !bIsUnconfirmed) return -1;
      if (!aIsUnconfirmed && bIsUnconfirmed) return 1;
      return 0;
    });
  }

  return list;
});

// Handle column sorting
const handleColumnSort = (column: TableColumn) => {
  if (sortColumn.value === column) {
    // Toggle direction if same column
    sortDirection.value = sortDirection.value === SortDirection.Ascending ? SortDirection.Descending : SortDirection.Ascending;
  } else {
    // Set new column and default to ascending
    sortColumn.value = column;
    sortDirection.value = SortDirection.Ascending;
  }
};

// Get sort indicator for column
const getSortIndicator = (column: string) => {
  if (sortColumn.value !== column) return null;
  return sortDirection.value === SortDirection.Ascending ? IconCaretUpFilled : IconCaretDownFilled;
};

// handle single appointment modal
const selectedAppointment = ref(null);

const showAppointmentSlidingPanel = (appointment) => {
  selectedAppointment.value = appointment;
  appointmentSlidingPanelRef.value?.showPanel()
  router.replace(`/bookings/${appointment.slug}`);
};

const handleCloseAppointmentSlidingPanel = () => {
  selectedAppointment.value = null;
  // Shuffle them back to the appointments route.
  router.replace('/bookings');
};

const ariaSortForColumn = (column: TableColumn) => {
  if (sortColumn.value !== column) return null;
  return sortDirection.value === SortDirection.Ascending ? 'ascending' : 'descending'
}

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();

  // If we've got a slug
  if (route.params?.slug) {
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
  <!-- page title area -->
  <div class="page-title-area">
    <div class="page-title">{{ t('label.appointments') }}</div>
    <div class="page-controls">
      <appointment-multi-select-filter
        :options="filterOptions"
        :selected="selectedFilters"
        @update:selected="selectedFilters = $event"
      />
      <checkbox-input
        name="unconfirmed-first"
        :label="t('label.unconfirmedFirst')"
        v-model="unconfirmedFirst"
      />
    </div>
  </div>

  <!-- page content -->
  <div class="page-content">
    <!-- main section: list of appointments with filter -->
    <div class="appointments-container">
      <!-- appointments list -->
      <table v-show="view === BookingsViewTypes.List" class="appointments-table"
        data-testid="bookings-appointments-list-table">
        <caption>
          <span class="screen-reader-only">
            {{ t("label.columnHeadersSortable") }}
          </span>
        </caption>
        <thead>
          <tr class="table-header-row">
            <th
              class="table-header"
              :aria-sort="ariaSortForColumn('date')"
            >
              <button @click="handleColumnSort('date')" class="sortable-header sortable-header-with-border">
                <component
                  :is="getSortIndicator('date')"
                  v-if="getSortIndicator('date')"
                  class="sort-indicator"
                  aria-hidden="true"
                />
                {{ t("label.date") }}
              </button>
            </th>
            <th
              class="table-header"
              :aria-sort="ariaSortForColumn('date')"
            >
              <button @click="handleColumnSort('date')" class="sortable-header sortable-header-with-border">
                {{ t("label.time") }}
              </button>
            </th>
            <th
              class="table-header"
              :aria-sort="ariaSortForColumn('title')"
            >
              <button @click="handleColumnSort('title')" class="sortable-header sortable-header-with-border">
                <component
                  :is="getSortIndicator('title')"
                  v-if="getSortIndicator('title')"
                  class="sort-indicator"
                  aria-hidden="true"
                />
                {{ t("label.meetingTitle") }}
              </button>
            </th>
            <th class="table-header status-header">
              <div class="status-header-content">
                <span aria-hidden="true">&nbsp;</span>
                <span class="screen-reader-only">{{ t("label.status") }}</span>
              </div>
            </th>
            <th
              class="table-header"
              :aria-sort="ariaSortForColumn('calendar')"
            >
              <button @click="handleColumnSort('calendar')" class="sortable-header">
                <component
                  :is="getSortIndicator('calendar')"
                  v-if="getSortIndicator('calendar')"
                  class="sort-indicator"
                  aria-hidden="true"
                />
                {{ t("label.calendar") }}
              </button>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(appointment, i) in filteredAppointments"
            :key="i"
            class="cursor-pointer hover:bg-sky-400/10 hover:shadow-lg relative"
            @click.left.exact="showAppointmentSlidingPanel(appointment)"
          >
            <td class="table-cell">
              <!-- Hidden link spanning the whole table row -->
              <router-link
                :to="`/bookings/${appointment.slug}`"
                class="absolute inset-0 z-10 opacity-0"
                aria-label="Open appointment in new tab"
              ></router-link>

              <span>{{ dj(appointment?.slots[0].start).format('LL') }}</span>
            </td>
            <td class="table-cell">
              <span>
                {{ dj(appointment?.slots[0].start).format(timeFormat()) }}
                {{ t('label.to') }}
                {{ dj(appointment?.slots[0].start).add(appointment?.slots[0].duration, 'minutes').format(timeFormat())
                }}
              </span>
            </td>
            <td class="table-cell title-cell">
              <span>{{ appointment.title }}</span>
            </td>
            <td class="table-cell status-cell">
              <span
                v-if="appointment?.slots[0].booking_status === BookingStatus.Requested"
              >
                {{ t('label.unconfirmed')}}
              </span>
            </td>
            <td class="table-cell">
              <span>{{ appointment.calendar_title }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <appointment-sliding-panel
    ref="appointmentSlidingPanelRef"
    :appointment="selectedAppointment"
    @close="handleCloseAppointmentSlidingPanel"
  />
</template>

<style scoped>
.page-title-area {
  display: flex;
  user-select: none;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  text-align: center;
  flex-direction: row;
}

.page-title {
  margin-bottom: 0;
  font-size: 2.25rem;
  font-weight: 300;
}

.page-controls {
  margin: 0 0 0 auto;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;

  & .checkbox-input-wrapper {
    width: auto;
  }
}

.page-content {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
}

.appointments-container {
  width: 100%;
}

.appointments-table {
  margin-top: 1rem;
  width: 100%;
}

/* Table styles */
.table-header-row {
  background-color: var(--colour-neutral-lower);

  .dark & {
    background-color: var(--colour-neutral-raised);
  }
}

.table-header {
  padding: 0.5rem;
  text-align: left;
  font-weight: normal;
}

.status-header {
  min-width: 120px;
}

.status-header-content {
  border-right: 1px solid var(--colour-neutral-border);
  padding: 0.25rem 0;

  .dark & {
    border-right-color: var(--colour-neutral-border-intense);
  }
}

.table-row {
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: rgba(56, 189, 248, 0.1);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
}

.table-cell {
  padding: 0.5rem;
  font-size: 0.875rem;
}

.title-cell {
  width: 40%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-cell {
  text-align: center;
  text-transform: uppercase;
  width: 200px;
  color: var(--colour-ti-critical)
}

/* Sortable header styles */
.sortable-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  font-size: inherit;
  font-weight: inherit;
  color: inherit;
  cursor: pointer;
  transition: background-color 0.2s;
  padding: 0.25rem 0;

  &:hover {
    background-color: var(--colour-neutral-subtle);
  }
}

.sortable-header-with-border {
  border-right: 1px solid var(--colour-neutral-border);
  padding: 0.25rem 0;

  .dark & {
    border-right-color: var(--colour-neutral-border-intense);
  }
}

.sort-indicator {
  width: 1rem;
  height: 1rem;
  margin-block-start: 0.2rem;
  color: var(--colour-ti-base);
}
</style>
