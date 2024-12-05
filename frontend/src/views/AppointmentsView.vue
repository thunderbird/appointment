<script setup lang="ts">
import {
  BookingStatus,
  BookingsTableColumns,
  BookingsViews,
  BookingsTableFilterOptions,
  BookingsViewTypes,
} from '@/definitions';
import { keyByValue, timeFormat, enumToObject } from '@/utils';

import {
  ref, inject, provide, computed, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { vOnClickOutside } from '@vueuse/components';
import AppointmentGridItem from '@/elements/AppointmentGridItem.vue';
import AppointmentModal from '@/components/AppointmentModal.vue';
import CalendarMiniMonth from '@/components/CalendarMiniMonth.vue';
import TabBar from '@/components/TabBar.vue';

// icons
import {
  IconAdjustments,
  IconCheck,
  IconLayoutGrid,
  IconList,
  IconSearch,
} from '@tabler/icons-vue';
import { useAppointmentStore } from '@/stores/appointment-store';
import { storeToRefs } from 'pinia';
import { dayjsKey, refreshKey, paintBackgroundKey } from '@/keys';

// component constants
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject(dayjsKey);
const refresh = inject(refreshKey);
const columns = enumToObject(BookingsTableColumns);

const appointmentStore = useAppointmentStore();

const { appointments } = storeToRefs(appointmentStore);

// handle calendar output
const activeDate = ref(dj()); // current selected date, defaults to now
const selectDate = (d: string) => {
  activeDate.value = dj(d);
};

const viewToParam = (view: number) => {
  switch (view) {
    case BookingsViews.Booked:
      return 'booked';
    case BookingsViews.Pending:
      return 'pending';
    case BookingsViews.Past:
      return 'past';
    case BookingsViews.All:
    default:
      return 'all';
  }
};
const paramToView = (param: string): number => {
  switch (param) {
    case 'booked':
      return BookingsViews.Booked;
    case 'pending':
      return BookingsViews.Pending;
    case 'past':
      return BookingsViews.Past;
    case 'all':
    default:
      return BookingsViews.All;
  }
};

// active menu item for tab navigation of appointment views
const tabActive = ref(route.params.view ? paramToView(route.params.view as string) : BookingsViews.All);
const updateTab = (view: string) => {
  router.replace({ name: route.name, params: { view } });
  tabActive.value = paramToView(view);
};

// date navigation
const dateNav = (forward = true) => {
  if (forward) {
    activeDate.value = activeDate.value.add(1, 'month');
  } else {
    activeDate.value = activeDate.value.subtract(1, 'month');
  }
};

// handle data filter
const filter = ref(BookingsTableFilterOptions.AppointmentsInMonth);

// handle data search
const search = ref('');

// handle data view
const view = ref(BookingsViewTypes.List);

// handle view adjustments: column visibility
const showAdjustments = ref(false);
const visibleColumns = ref(Object.values(columns));
const openAdjustments = () => {
  if (view.value === BookingsViewTypes.List) {
    showAdjustments.value = true;
  }
};
const closeAdjustments = () => {
  showAdjustments.value = false;
};
const toggleColumnVisibility = (key) => {
  if (visibleColumns.value.includes(key)) {
    visibleColumns.value = visibleColumns.value.filter(
      (column) => column !== key,
    );
  } else {
    visibleColumns.value.push(key);
  }
};
const columnVisible = (key: string) => visibleColumns.value.includes(columns[key]);
const restoreColumnOrder = () => {
  visibleColumns.value = Object.values(columns);
};

// handle filtered appointments list
const filteredAppointments = computed(() => {
  let list = appointments.value ? [...appointments.value] : [];
  // by search input
  if (search.value !== '') {
    list = list.filter((a) => a.title.toLowerCase().includes(search.value.toLowerCase()));
  }
  // by active tab
  switch (tabActive.value) {
    case BookingsViews.Booked:
      list = list.filter((a) => a.slots[0].booking_status === BookingStatus.Booked);
      break;
    case BookingsViews.Pending:
      list = list.filter((a) => a.slots[0].booking_status === BookingStatus.Requested);
      break;
    case BookingsViews.Past:
      list = list.filter((a) => a.slots[0].start < dj());
      break;
    case BookingsViews.All:
    default:
      break;
  }
  // by select filter
  switch (filter.value) {
    case BookingsTableFilterOptions.AppointmentsToday:
      list = list.filter((a) => a.slots.reduce((p, c) => p || dj(c.start).isToday(), false));
      break;
    case BookingsTableFilterOptions.AppointmentsNext7Days:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p
            || dj(c.start).isToday()
            || dj(c.start).isBetween(dj(), dj().add(7, 'days')),
        false,
      ));
      break;
    case BookingsTableFilterOptions.AppointmentsNext14Days:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p
            || dj(c.start).isToday()
            || dj(c.start).isBetween(dj(), dj().add(14, 'days')),
        false,
      ));
      break;
    case BookingsTableFilterOptions.AppointmentsNext31Days:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p
            || dj(c.start).isToday()
            || dj(c.start).isBetween(dj(), dj().add(31, 'days')),
        false,
      ));
      break;
    case BookingsTableFilterOptions.AppointmentsInMonth:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p || dj(c.start).isToday() || dj(c.start).isSame(dj(), 'month'),
        false,
      ));
      break;
    case BookingsTableFilterOptions.AllFutureAppointments:
      list = list.filter((a) => a.slots.reduce((p, c) => p || dj(c.start).isAfter(dj()), false));
      break;
    case BookingsTableFilterOptions.AllAppointments:
    default:
      break;
  }
  return list;
});

// handle single appointment modal
const showAppointment = ref(null);
const showAppointmentModal = (appointment) => {
  showAppointment.value = appointment;
  router.replace(`/appointments/${viewToParam(tabActive.value)}/${appointment.slug}`);
};
const closeAppointmentModal = () => {
  showAppointment.value = null;

  // Shuffle them back to the appointments route.
  router.replace(`/appointments/${viewToParam(tabActive.value)}`);
};

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();

  // If we've got a slug
  if (route.params?.slug) {
    showAppointmentModal(appointments.value.filter((appointment) => appointment.slug === route.params.slug)[0]);
  }
});

// paint elements background or reset it to transparent
const paintBackground = (element: Event, hexColor: string, hexTransparency = 'ff', reset = false) => {
  if (hexColor) {
    (element.currentTarget as HTMLTableRowElement).style.backgroundColor = reset
      ? 'transparent'
      : hexColor + hexTransparency;
  }
};
provide(paintBackgroundKey, paintBackground);
</script>

<template>
  <!-- page title area -->
  <div class="flex select-none flex-col justify-between text-center lg:flex-row lg:items-start">
    <div class="mb-8 text-4xl font-light lg:mb-0">{{ t('label.appointments') }}</div>
    <div class="mx-auto flex flex-col items-center gap-8 lg:mx-0 lg:flex-row">
      <tab-bar
        :tab-items="enumToObject(BookingsViews)"
        :active="tabActive"
        @update="updateTab"
        class="text-xl"
      />
    </div>
  </div>
  <!-- page content -->
  <div class="mt-8 flex flex-col justify-between gap-4 lg:flex-row xl:gap-24">
    <!-- main section: list/grid of appointments with filter -->
    <div class="w-full lg:w-4/5">
      <!-- filter bar -->
      <div class="relative flex select-none gap-5">
        <select v-model="filter" class="rounded border text-sm" data-testid="bookings-filter-select">
          <option v-for="(value, key) in enumToObject(BookingsTableFilterOptions)" :key="key" :value="value">
            {{ t("label." + key) }}
          </option>
        </select>
        <div class="relative w-full">
          <label
            for="appointments-search"
            class="absolute left-3 top-1/2 -translate-y-1/2 cursor-text"
          >
            <icon-search class="size-4 fill-transparent stroke-gray-300 stroke-2 dark:stroke-gray-500" />
          </label>
          <input
            v-model="search"
            type="search"
            id="appointments-search"
            class="w-full rounded pl-10 text-sm"
            :placeholder="t('label.searchAppointments')"
            data-testid="bookings-search-input"
          />
        </div>
        <div class="flex rounded border border-gray-300 dark:border-gray-500">
          <div
            class="
              btn-toggle flex cursor-pointer items-center overflow-hidden border-r border-gray-300 px-1.5
              py-1 dark:border-gray-500
            "
            :class="{
              'bg-gray-300 dark:bg-gray-600': view === BookingsViewTypes.List,
              'hover:bg-gray-100 dark:hover:bg-gray-500': view !== BookingsViewTypes.List,
            }"
            @click="view = BookingsViewTypes.List"
            data-testid="bookings-list-view-btn"
          >
            <icon-list class="size-6 fill-transparent stroke-gray-700 stroke-1 dark:stroke-gray-300" />
          </div>
          <div
            class="btn-toggle flex cursor-pointer items-center overflow-hidden px-1.5 py-1"
            :class="{
              'bg-gray-300 dark:bg-gray-600': view === BookingsViewTypes.Grid,
              'hover:bg-gray-100 dark:hover:bg-gray-500': view !== BookingsViewTypes.Grid,
            }"
            @click="view = BookingsViewTypes.Grid"
            data-testid="bookings-grid-view-btn"
          >
            <icon-layout-grid class="size-6 fill-transparent stroke-gray-700 stroke-1 dark:stroke-gray-300" />
          </div>
        </div>
        <div
          class="btn-toggle flex items-center rounded border border-gray-300 px-1.5 py-1 dark:border-gray-500"
          :class="{
            'bg-gray-300 dark:bg-gray-600': showAdjustments,
            'hover:bg-gray-100 dark:hover:bg-gray-500': !showAdjustments && view === BookingsViewTypes.List,
            'opacity-30': view === BookingsViewTypes.Grid,
            'cursor-pointer': view === BookingsViewTypes.List,
          }"
          @click="openAdjustments"
          data-testid="bookings-adjust-table-btn"
        >
          <icon-adjustments class="size-6 fill-transparent stroke-gray-700 stroke-1 dark:stroke-gray-300" />
        </div>
        <div
          v-show="showAdjustments"
          class="
            absolute right-0 top-10 z-40 rounded border border-gray-300 bg-white
            p-2 shadow-md dark:border-gray-500 dark:bg-gray-700
          "
          v-on-click-outside="closeAdjustments"
        >
          <div
            v-for="(value, key) in columns"
            :key="key"
            :data-testid="'bookings-adjust-table-' + key + '-menu'"
            class="
              grid cursor-pointer grid-cols-context rounded py-1 pl-1 pr-3
              hover:bg-gray-100 dark:hover:bg-gray-500
            "
            @click="toggleColumnVisibility(value)"
          >
            <div class="flex items-center">
              <icon-check
                v-show="visibleColumns.includes(value)"
                class="size-4 fill-transparent stroke-gray-800 stroke-1 dark:stroke-gray-200"
              />
            </div>
            <div class="text-sm">{{ t("label." + key) }}</div>
          </div>
          <div class="my-2 border-t border-gray-300 dark:border-gray-500"></div>
          <div
            class="
              grid cursor-pointer grid-cols-context rounded py-1 pl-1 pr-3
              hover:bg-gray-100 dark:hover:bg-gray-500
            "
            @click="restoreColumnOrder"
            data-testid="bookings-adjust-table-restore-menu"
          >
            <div></div>
            <div class="text-sm">{{ t("label.restoreColumnOrder") }}</div>
          </div>
        </div>
      </div>
      <!-- appointments list -->
      <table v-show="view === BookingsViewTypes.List" class="mt-4 w-full" data-testid="bookings-appointments-list-table">
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
          <tr
            v-for="(appointment, i) in filteredAppointments"
            :key="i"
            class="cursor-pointer hover:bg-sky-400/10 hover:shadow-lg"
            @mouseover="(el) => paintBackground(el, appointment.calendar_color, '22')"
            @mouseout="(el) => paintBackground(el, appointment.calendar_color, undefined, true)"
            @click="showAppointmentModal(appointment)"
          >
            <td class="align-middle">
              <div
                class="mx-auto size-3 rounded-full bg-sky-400"
                :style="{ backgroundColor: appointment.calendar_color }"
              ></div>
            </td>
            <td v-if="columnVisible('title')" class="max-w-2xs truncate p-2">
              <span>{{ appointment.title }}</span>
            </td>
            <td v-if="columnVisible('status')" class="p-2 text-sm">
              <span>{{ t('label.' + keyByValue(BookingStatus, appointment?.slots[0].booking_status ?? 'Unknown', true)) }}</span>
            </td>
            <td v-if="columnVisible('calendar')" class="p-2 text-sm">
              <span>{{ appointment.calendar_title }}</span>
            </td>
            <td v-if="columnVisible('time')" class="p-2 text-sm">
              <div>{{ dj(appointment?.slots[0].start).format('LL') }}</div>
              <div>
                {{ dj(appointment?.slots[0].start).format(timeFormat()) }}
                {{ t('label.to')}}
                {{ dj(appointment?.slots[0].start).add(appointment?.slots[0].duration, 'minutes').format(timeFormat()) }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <!-- appointments grid -->
      <div
        v-show="view === BookingsViewTypes.Grid"
        class="mt-4 grid w-full grid-cols-[repeat(_auto-fit,_minmax(250px,_1fr))] gap-8 p-4 xl:grid-cols-3"
      >
        <appointment-grid-item
          v-for="(appointment, i) in filteredAppointments"
          :key="i"
          :appointment="appointment"
          @click="showAppointmentModal(appointment)"
        />
      </div>
    </div>
    <!-- page side bar -->
    <div class="mx-auto mb-10 w-full min-w-[310px] sm:w-1/2 md:mb-0 lg:w-1/5">
      <div>
        <!-- monthly mini calendar -->
        <calendar-mini-month
          :selected="activeDate"
          :nav="true"
          @prev="dateNav(false)"
          @next="dateNav()"
          @day-selected="selectDate"
        />
      </div>
    </div>
  </div>
  <appointment-modal
    :open="showAppointment !== null"
    :appointment="showAppointment"
    @close="closeAppointmentModal"
  />
</template>
