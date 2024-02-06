<template>
  <!-- page title area -->
  <div class="flex flex-col lg:flex-row justify-between text-center lg:items-start select-none">
    <div class="text-4xl font-light mb-8 lg:mb-0">{{ t('label.appointments') }}</div>
    <div class="flex flex-col lg:flex-row gap-8 mx-auto lg:ml-0 lg:mr-0 items-center">
      <tab-bar :tab-items="views" :active="tabActive" @update="updateTab" class="text-xl" />
      <primary-button
        :label="t('label.createAppointments')"
        :disabled="!connectedCalendars.length || creationStatus !== appointmentCreationState.hidden"
        @click="creationStatus = appointmentCreationState.details"
      />
    </div>
  </div>
  <!-- page content -->
  <div class="flex flex-col flex-col-reverse lg:flex-row justify-between gap-4 xl:gap-24 mt-8">
    <!-- main section: list/grid of appointments with filter -->
    <div class="w-full lg:w-4/5">
      <!-- filter bar -->
      <div class="relative flex gap-5 select-none">
        <select v-model="filter" class="rounded border text-sm">
          <option v-for="(value, key) in filterOptions" :key="key" :value="value">
            {{ t("label." + key) }}
          </option>
        </select>
        <div class="w-full relative">
          <label
            for="appointments-search"
            class="absolute top-1/2 -translate-y-1/2 left-3 cursor-text"
          >
            <icon-search class="h-4 w-4 stroke-2 stroke-gray-300 dark:stroke-gray-500 fill-transparent" />
          </label>
          <input
            v-model="search"
            type="search"
            id="appointments-search"
            class="rounded w-full pl-10 text-sm"
            :placeholder="t('label.searchAppointments')"
          />
        </div>
        <div class="rounded border border-gray-300 dark:border-gray-500 flex">
          <div
            class="
              border-r py-1 px-1.5 flex items-center cursor-pointer overflow-hidden
              border-gray-300 dark:border-gray-500
            "
            :class="{
              'bg-gray-300 dark:bg-gray-600': view === viewTypes.list,
              'hover:bg-gray-100 dark:hover:bg-gray-500': view !== viewTypes.list,
            }"
            @click="view = viewTypes.list"
          >
            <icon-list class="h-6 w-6 stroke-1 stroke-gray-700 dark:stroke-gray-300 fill-transparent" />
          </div>
          <div
            class="py-1 px-1.5 flex items-center cursor-pointer overflow-hidden"
            :class="{
              'bg-gray-300 dark:bg-gray-600': view === viewTypes.grid,
              'hover:bg-gray-100 dark:hover:bg-gray-500': view !== viewTypes.grid,
            }"
            @click="view = viewTypes.grid"
          >
            <icon-layout-grid class="h-6 w-6 stroke-1 stroke-gray-700 dark:stroke-gray-300 fill-transparent" />
          </div>
        </div>
        <div
          class="rounded border border-gray-300 dark:border-gray-500 py-1 px-1.5 flex items-center"
          :class="{
            'bg-gray-300 dark:bg-gray-600': showAdjustments,
            'hover:bg-gray-100 dark:hover:bg-gray-500': !showAdjustments && view === viewTypes.list,
            'opacity-30': view === viewTypes.grid,
            'cursor-pointer': view === viewTypes.list,
          }"
          @click="openAdjustments"
        >
          <icon-adjustments class="h-6 w-6 stroke-1 stroke-gray-700 dark:stroke-gray-300 fill-transparent" />
        </div>
        <div
          v-show="showAdjustments"
          class="
            absolute z-40 top-10 right-0 p-2 rounded shadow-md border
            border-gray-300 dark:border-gray-500 bg-white dark:bg-gray-700
          "
          v-on-click-outside="closeAdjustments"
        >
          <div
            v-for="(value, key) in columns"
            :key="key"
            class="
              grid grid-cols-context rounded py-1 pl-1 pr-3 cursor-pointer
              hover:bg-gray-100 dark:hover:bg-gray-500
            "
            @click="toggleColumnVisibility(value)"
          >
            <div class="flex items-center">
              <icon-check
                v-show="visibleColumns.includes(value)"
                class="h-4 w-4 stroke-1 stroke-gray-800 dark:stroke-gray-200 fill-transparent"
              />
            </div>
            <div class="text-sm">{{ t("label." + key) }}</div>
          </div>
          <div class="border-t border-gray-300 dark:border-gray-500 my-2"></div>
          <div
            class="
              grid grid-cols-context rounded py-1 pl-1 pr-3 cursor-pointer
              hover:bg-gray-100 dark:hover:bg-gray-500
            "
            @click="restoreColumnOrder"
          >
            <div></div>
            <div class="text-sm">{{ t("label.restoreColumnOrder") }}</div>
          </div>
        </div>
      </div>
      <!-- appointments list -->
      <table v-show="view === viewTypes.list" class="w-full mt-4">
        <thead>
          <tr class="bg-gray-100 dark:bg-gray-600">
            <th class="py-1"></th>
            <template v-for="(_, key) in columns" :key="key">
              <th v-if="columnVisible(key)" class="group font-normal text-left py-1 px-2">
                <div class="py-1 border-r border-gray-300 dark:border-gray-500 group-last:border-none">
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
            class="hover:bg-sky-400/10 hover:shadow-lg cursor-pointer"
            @mouseover="(el) => paintBackground(el, appointment.calendar_color, '22')"
            @mouseout="(el) => paintBackground(el, appointment.calendar_color, _, true)"
            @click="showAppointment = appointment"
          >
            <td class="align-middle">
              <div
                class="rounded-full w-3 h-3 bg-sky-400 mx-auto"
                :style="{ backgroundColor: appointment.calendar_color }"
              ></div>
            </td>
            <td v-if="columnVisible('title')" class="py-2 px-2 max-w-2xs truncate">
              <span>{{ appointment.title }}</span>
            </td>
            <td v-if="columnVisible('status')" class="py-2 px-2 text-sm">
              <span>{{ t("label." + keyByValue(appointmentState, appointment.status)) }}</span>
            </td>
            <td v-if="columnVisible('active')" class="py-2 px-2 text-sm">
              <span>{{ appointment.active ? t("label.open") : t("label.closed") }}</span>
            </td>
            <td v-if="columnVisible('calendar')" class="py-2 px-2 text-sm">
              <span>{{ appointment.calendar_title }}</span>
            </td>
            <td v-if="columnVisible('bookingLink')" class="py-2 px-2 text-sm max-w-2xs truncate">
              <a
                :href="bookingUrl + appointment.slug"
                class="text-teal-500 underline underline-offset-2"
                target="_blank"
                @click.stop="null"
              >
                {{ bookingUrl + appointment.slug }}
              </a>
            </td>
            <td v-if="columnVisible('replies')" class="py-2 px-2 text-sm">
              <span>
                {{ repliesCount(appointment) }}
                {{ t("label.bookings", repliesCount(appointment)) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <!-- appointments grid -->
      <div
        v-show="view === viewTypes.grid"
        class="w-full mt-4 grid grid-cols-[repeat(_auto-fit,_minmax(250px,_1fr))] xl:grid-cols-3 gap-8 p-4"
      >
        <appointment-grid-item
          v-for="(appointment, i) in filteredAppointments"
          :key="i"
          :appointment="appointment"
          @click="showAppointment = appointment"
        />
      </div>
    </div>
    <!-- page side bar -->
    <div class="w-full sm:w-1/2 lg:w-1/5 mx-auto mb-10 md:mb-0 min-w-[310px]">
      <div v-if="creationStatus === appointmentCreationState.hidden">
        <!-- monthly mini calendar -->
        <calendar-month
          :selected="activeDate"
          :mini="true"
          :nav="true"
          @prev="dateNav('month', false)"
          @next="dateNav('month')"
          @day-selected="selectDate"
        />
      </div>
      <!-- appointment creation dialog -->
      <appointment-creation
        v-else
        :status="creationStatus"
        :calendars="connectedCalendars"
        @start="creationStatus = appointmentCreationState.details"
        @next="creationStatus = appointmentCreationState.availability"
        @create="creationStatus = appointmentCreationState.finished; refresh();"
        @cancel="creationStatus = appointmentCreationState.hidden"
      />
    </div>
  </div>
  <appointment-modal
    :open="showAppointment !== null"
    :appointment="showAppointment"
    @close="closeAppointmentModal"
  />
</template>

<script setup>
import {
  appointmentState,
  listColumns as columns,
  appointmentViews as views,
  filterOptions,
  viewTypes,
  appointmentCreationState,
} from '@/definitions';
import { keyByValue } from '@/utils';

import {
  ref, inject, provide, computed, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { vOnClickOutside } from '@vueuse/components';
import AppointmentCreation from '@/components/AppointmentCreation';
import AppointmentGridItem from '@/elements/AppointmentGridItem';
import AppointmentModal from '@/components/AppointmentModal';
import CalendarMonth from '@/components/CalendarMonth';
import PrimaryButton from '@/elements/PrimaryButton';
import TabBar from '@/components/TabBar';

// icons
import {
  IconAdjustments,
  IconCheck,
  IconLayoutGrid,
  IconList,
  IconSearch,
} from '@tabler/icons-vue';
import { useAppointmentStore } from "@/stores/appointment-store";
import { useCalendarStore } from "@/stores/calendar-store";
import { storeToRefs } from 'pinia';

// component constants
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject('dayjs');
const bookingUrl = inject('bookingUrl');
const refresh = inject('refresh');

const appointmentStore = useAppointmentStore();
const calendarStore = useCalendarStore();

const { appointments } = storeToRefs(appointmentStore);
const { connectedCalendars } = storeToRefs(calendarStore);

// handle calendar output
const activeDate = ref(dj()); // current selected date, defaults to now
const selectDate = (d) => {
  activeDate.value = dj(d);
};

// active menu item for tab navigation of appointment views
const tabActive = ref(route.params.view ? views[route.params.view] : views.all);
const updateTab = (view) => {
  router.replace({ name: route.name, params: { view } });
  tabActive.value = views[view];
};
// date navigation
const dateNav = (unit = 'auto', forward = true) => {
  if (unit === 'auto') {
    unit = Object.keys(views).find((key) => views[key] === tabActive.value);
  }
  if (forward) {
    activeDate.value = activeDate.value.add(1, unit);
  } else {
    activeDate.value = activeDate.value.subtract(1, unit);
  }
};

// handle data filter
const filter = ref(filterOptions.appointmentsInMonth);

// handle data search
const search = ref('');

// handle data view
const view = ref(viewTypes.list);

// handle view adjustments: column visibility
const showAdjustments = ref(false);
const visibleColumns = ref(Object.values(columns));
const openAdjustments = () => {
  if (view.value === viewTypes.list) {
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
const columnVisible = (key) => visibleColumns.value.includes(columns[key]);
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
    case views.booked:
      list = list.filter((a) => a.status === appointmentState.booked);
      break;
    case views.pending:
      list = list.filter((a) => a.status === appointmentState.pending);
      break;
    case views.past:
      list = list.filter((a) => a.status === appointmentState.past);
      break;
    case views.all:
    default:
      break;
  }
  // by select filter
  switch (filter.value) {
    case filterOptions.appointmentsToday:
      list = list.filter((a) => a.slots.reduce((p, c) => p || dj(c.start).isToday(), false));
      break;
    case filterOptions.appointmentsNext7Days:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p
            || dj(c.start).isToday()
            || dj(c.start).isBetween(dj(), dj().add(7, 'days')),
        false,
      ));
      break;
    case filterOptions.appointmentsNext14Days:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p
            || dj(c.start).isToday()
            || dj(c.start).isBetween(dj(), dj().add(14, 'days')),
        false,
      ));
      break;
    case filterOptions.appointmentsNext31Days:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p
            || dj(c.start).isToday()
            || dj(c.start).isBetween(dj(), dj().add(31, 'days')),
        false,
      ));
      break;
    case filterOptions.appointmentsInMonth:
      list = list.filter((a) => a.slots.reduce(
        (p, c) => p || dj(c.start).isToday() || dj(c.start).isSame(dj(), 'month'),
        false,
      ));
      break;
    case filterOptions.allFutureAppointments:
      list = list.filter((a) => a.slots.reduce((p, c) => p || dj(c.start).isAfter(dj()), false));
      break;
    case filterOptions.allAppointments:
    default:
      break;
  }
  return list;
});

// return number of booked slots (replies) for given appointment
const repliesCount = (appointment) => appointment.slots.filter((s) => s.attendee != null).length;

// handle single appointment modal
const showAppointment = ref(null);
const closeAppointmentModal = () => {
  showAppointment.value = null;
};

// appointment creation
const creationStatus = ref(appointmentCreationState.hidden);

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
});

// paint elements background or reset it to transparent
const paintBackground = (element, hexColor, hexTransparency, reset = false) => {
  if (hexColor) {
    element.currentTarget.style.backgroundColor = reset
      ? 'transparent'
      : hexColor + hexTransparency;
  }
};
provide('paintBackground', paintBackground);
</script>
