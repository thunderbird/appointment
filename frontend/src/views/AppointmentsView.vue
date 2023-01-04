<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <div class="text-4xl font-light">{{ t('label.appointments') }}</div>
    <div class="flex gap-8 items-center">
      <tab-bar :tab-items="views" :active="tabActive" @update="updateTab" class="text-xl" />
      <primary-button
        :label="t('label.createAppointments')"
        :disabled="creationStatus !== creationState.hidden"
        @click="creationStatus = creationState.details"
      />
    </div>
  </div>
  <!-- page content -->
  <div class="flex justify-between gap-24 mt-8">
    <!-- main section: list/grid of appointments with filter -->
    <div class="w-4/5">
      <!-- filter bar -->
      <div class="relative flex gap-5 select-none">
        <select v-model="filter" class="rounded border border-gray-300 text-sm">
          <option v-for="(value, key) in filterOptions" :key="key" :value="value">{{ t('label.' + key) }}</option>
        </select>
        <div class="w-full relative">
          <label for="appointments-search" class="absolute top-1/2 -translate-y-1/2 left-3 cursor-text">
            <icon-search class="h-4 w-4 stroke-2 stroke-gray-400 fill-transparent" /> 
          </label>
          <input v-model="search" type="search" id="appointments-search" class="rounded border border-gray-300 w-full pl-10 text-sm" :placeholder="t('label.searchAppointments')" />
        </div>
        <div class="rounded border border-gray-300 flex">
          <div
            class="border-r border-gray-300 py-1 px-1.5 flex items-center cursor-pointer overflow-hidden"
            :class="{
              'bg-gray-300': view === viewTypes.list,
              'hover:bg-gray-100': view !== viewTypes.list
            }"
            @click="view = viewTypes.list"
          >
            <icon-list class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
          </div>
          <div
            class="py-1 px-1.5 flex items-center cursor-pointer overflow-hidden"
            :class="{
              'bg-gray-300': view === viewTypes.grid,
              'hover:bg-gray-100': view !== viewTypes.grid
            }"
            @click="view = viewTypes.grid"
          >
            <icon-grid class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
          </div>
        </div>
        <div
          class="rounded border border-gray-300 py-1 px-1.5 flex items-center"
          :class="{
            'bg-gray-300': showAdjustments,
            'hover:bg-gray-100': !showAdjustments && view === viewTypes.list,
            'opacity-30': view === viewTypes.grid,
            'cursor-pointer': view === viewTypes.list
          }"
          @click="openAdjustments"
        >
          <icon-adjustments class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
        </div>
        <div
          v-show="showAdjustments"
          class="absolute z-40 top-10 right-0 p-2 rounded shadow-md border border-gray-300 bg-white"
          v-on-click-outside="closeAdjustments"
        >
          <div
            v-for="(value, key) in columns"
            :key="key"
            class="grid grid-cols-context hover:bg-gray-100 rounded py-1 pl-1 pr-3 cursor-pointer"
            @click="toggleColumnVisibility(value)"
          >
            <div class="flex items-center">
              <icon-check v-show="visibleColumns.includes(value)" class="h-4 w-4 stroke-1 stroke-gray-800 fill-transparent" />
            </div>
            <div class="text-sm">{{ t('label.' + key) }}</div>
          </div>
          <div class="border-t border-gray-300 my-2"></div>
          <div class="grid grid-cols-context hover:bg-gray-100 rounded py-1 pl-1 pr-3 cursor-pointer" @click="restoreColumnOrder">
            <div></div>
            <div class="text-sm">{{ t('label.restoreColumnOrder') }}</div>
          </div>
        </div>
      </div>
      <!-- appointments list -->
      <table v-show="view === viewTypes.list" class="w-full mt-4">
        <thead>
          <tr>
            <th class="bg-gray-100 py-1"></th>
            <template v-for="(_, key) in columns" :key="key">
              <th v-if="columnVisible(key)" class="group bg-gray-100 font-normal text-left py-1 px-2">
                <div class="py-1 border-r border-gray-300 group-last:border-none">{{ t('label.' + key) }}</div>
              </th>
            </template>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(appointment, i) in filteredAppointments"
            :key="i"
            class="hover:bg-sky-400/10 hover:shadow-lg cursor-pointer"
            @mouseover="el => el.currentTarget.style.backgroundColor=appointment.calendar_color + '22'"
            @mouseout="el => el.currentTarget.style.backgroundColor='transparent'"
            @click="showAppointment = appointment"
          >
            <td class="align-middle">
              <div
                class="rounded-full w-3 h-3 bg-sky-400 mx-auto"
                :style="{ 'background-color': appointment.calendar_color }"
              ></div>
            </td>
            <td v-if="columnVisible('title')" class="py-2 px-2">
              <span>{{ appointment.title }}</span>
            </td>
            <td v-if="columnVisible('status')" class="py-2 px-2 text-sm">
              <span>{{ t('label.' + keyByValue(appointmentState, appointment.status)) }}</span>
            </td>
            <td v-if="columnVisible('active')" class="py-2 px-2 text-sm">
              <span>{{ appointment.active ? t('label.open') : t('label.closed') }}</span>
            </td>
            <td v-if="columnVisible('calendar')" class="py-2 px-2 text-sm">
              <span>{{ appointment.calendar_title }}</span>
            </td>
            <td v-if="columnVisible('bookingLink')" class="py-2 px-2 text-sm max-w-2xs truncate">
              <a
                :href="baseurl + appointment.slug"
                class="text-teal-500 underline"
                target="_blank"
                @click.stop="null"
              >
                {{ baseurl + appointment.slug }}
              </a>
            </td>
            <td v-if="columnVisible('replies')" class="py-2 px-2 text-sm">
              <span>{{ repliesCount(appointment) }} {{ t('label.bookings', repliesCount(appointment)) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
      <!-- appointments grid -->
      <div v-show="view === viewTypes.grid" class="w-full mt-4 grid grid-cols-3 gap-8 p-4">
        <appointment-grid-item
          v-for="(appointment, i) in filteredAppointments" :key="i"
          :appointment="appointment"
          @click="showAppointment = appointment"
        />
      </div>
    </div>
    <!-- page side bar -->
    <div class="w-1/5 min-w-[310px]">
      <div v-if="creationStatus === creationState.hidden">
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
        :calendars="calendars"
        @start="creationStatus = creationState.details"
        @next="creationStatus = creationState.availability"
        @create="creationStatus = creationState.finished; refresh();"
        @cancel="creationStatus = creationState.hidden"
      />
    </div>
  </div>
  <appointment-modal :open="showAppointment !== null" :appointment="showAppointment" @close="closeAppointmentModal" />
</template>

<script setup>
import { appointmentState } from '@/definitions';
import { keyByValue } from '@/utils';
import { listColumns as columns, appointmentViews as views, filterOptions, viewTypes, creationState } from '@/definitions';
import { ref, inject, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { vOnClickOutside } from '@vueuse/components';
import AppointmentCreation from '@/components/AppointmentCreation';
import AppointmentGridItem from '@/elements/AppointmentGridItem';
import AppointmentModal from '@/components/AppointmentModal';
import CalendarMonth from '@/components/CalendarMonth';
import IconAdjustments from '@/elements/icons/IconAdjustments';
import IconCheck from '@/elements/icons/IconCheck';
import IconGrid from '@/elements/icons/IconGrid';
import IconList from '@/elements/icons/IconList';
import IconSearch from '@/elements/icons/IconSearch';
import PrimaryButton from '@/elements/PrimaryButton';
import TabBar from '@/components/TabBar';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject('dayjs');
const baseurl = inject('baseurl');
const refresh = inject('refresh');

// view properties
const props = defineProps({
  calendars: Array,    // list of calendars from db
  appointments: Array, // list of appointments from db
});

// handle calendar output
const activeDate = ref(dj()); // current selected date, defaults to now
const selectDate = (d) => activeDate.value = dj(d);

// active menu item for tab navigation of appointment views
const tabActive = ref(route.params.view ? views[route.params.view] : views.all);
const updateTab = view => {
  router.replace({ name: route.name, params: { view: view } });
  tabActive.value = views[view];
};
// date navigation
const dateNav = (unit = 'auto', forward = true) => {
  if (unit === 'auto') {
    unit = Object.keys(views).find(key => views[key] === tabActive.value);
  }
  if (forward) {
    activeDate.value = activeDate.value.add(1, unit);
  } else {
    activeDate.value = activeDate.value.subtract(1, unit);
  }
};

// handle data filter
const filter = ref(filterOptions.appointmentsToday);

// handle data search
const search = ref('');

// handle data view
const view = ref(viewTypes.list);

// handle view adjustments: column visibility
const showAdjustments = ref(false);
const visibleColumns = ref(Object.values(columns));
const openAdjustments = () => {
  if (view.value == viewTypes.list) {
    showAdjustments.value = true;
  }
};
const closeAdjustments = () => showAdjustments.value = false;
const toggleColumnVisibility = (key) => {
  if (visibleColumns.value.includes(key)) {
    visibleColumns.value = visibleColumns.value.filter((column) => column !== key);
  } else {
    visibleColumns.value.push(key);
  }
};
const columnVisible = (key) => {
  return visibleColumns.value.includes(columns[key]);
};
const restoreColumnOrder = () => {
  visibleColumns.value = Object.values(columns);
};

// TODO: fake data
// const fakeAppointments = [
//   { title: 'Bi-weekly Café Dates', status: 'past', active: true, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Online', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-10-30T10:00:00', duration: 60, attendee: null }] },
//   { title: 'Weekly ZOOM', status: 'past', active: true, calendar_title: 'Family', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'ZOOM', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-10-31T10:00:00', duration: 60, attendee: { name: 'John Doe', email: 'john@doe.com' } }] },
//   { title: 'Jour Fixe Team', status: 'booked', active: true, calendar_title: 'Family', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Teams', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-11T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
//   { title: 'Project Appointment', status: 'pending', active: true, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Jitsi', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-12T10:00:00', duration: 60, attendee: null }] },
//   { title: 'Team Building Event', status: 'booked', active: true, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'BigBlueButton', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-13T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }, { start: '2022-11-13T11:00:00', duration: 60, attendee: null }, { start: '2022-11-13T12:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'jane@doe.com' } }] },
//   { title: 'Bi-weekly Café Dates', status: 'pending', active: false, calendar_title: 'Family', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Signal', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-14T10:00:00', duration: 60, attendee: null }] },
//   { title: 'Weekly ZOOM', status: 'booked', active: false, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Online', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-15T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
//   { title: 'Jour Fixe Team', status: 'booked', active: true, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Phone', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-16T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
//   { title: 'Project Appointment', status: 'booked', active: false, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Park', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-17T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
//   { title: 'Team Building Event', status: 'booked', active: false, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Building 429, Room 5', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-18T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
//   { title: 'Team Building Event', status: 'booked', active: false, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Building 429, Room 5', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-18T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
//   { title: 'Team Building Event', status: 'booked', active: false, calendar_title: 'Work', calendar_color: '#978FEE', slug: 'sdfw83jc', location_name: 'Building 429, Room 5', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-18T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
// ];

// handle filtered appointments list
const filteredAppointments = computed(() => {
  let list = [...props.appointments];
  // by search input
  if (search.value !== '') {
    list = list.filter(e => e.title.toLowerCase().includes(search.value.toLowerCase()))
  }
  // by active tab
  switch (tabActive.value) {
    case views.booked:
      list = list.filter(e => e.status === appointmentState.booked);
      break;
    case views.pending:
      list = list.filter(e => e.status === appointmentState.pending);
      break;
    case views.past:
      list = list.filter(e => e.status === appointmentState.past);
      break;
    case views.all:
    default:
      break;
  }
  return list;
});

// return number of booked slots (replies) for given appointment
const repliesCount = appointment => appointment.slots.filter(s => s.attendee != null).length;

// handle single appointment modal
const showAppointment = ref(null);
const closeAppointmentModal = () => showAppointment.value = null;

// appointment creation
const creationStatus = ref(creationState.hidden);

// initially load data when component gets remounted
onMounted(() => {
  refresh();
});
</script>
