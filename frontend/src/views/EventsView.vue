<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <div class="text-4xl font-light">{{ t('label.events') }}</div>
    <div class="flex gap-8 items-center">
      <tab-bar :tab-items="Object.keys(tabItems)" :active="tabActive" @update="updateTab" />
      <primary-button :label="t('label.createEvent')" />
    </div>
  </div>
  <!-- page content -->
  <div class="flex justify-between gap-24 mt-8">
    <!-- main section: list/grid of events with filter -->
    <div class="w-4/5">
      <!-- filter bar -->
      <div class="relative flex gap-5 select-none">
        <select v-model="filter" class="rounded border border-gray-300 text-sm">
          <option v-for="(value, key) in filterOptions" :key="key" :value="value">{{ t('label.' + key) }}</option>
        </select>
        <div class="w-full relative">
          <label for="events-search" class="absolute top-1/2 -translate-y-1/2 left-3 cursor-text">
            <icon-search class="h-4 w-4 stroke-2 stroke-gray-400 fill-transparent" /> 
          </label>
          <input v-model="search" type="search" id="events-search" class="rounded border border-gray-300 w-full pl-10 text-sm" placeholder="Search events" />
        </div>
        <div class="rounded border border-gray-300 flex">
          <div
            class="border-r border-gray-300 py-1 px-1.5 flex items-center cursor-pointer overflow-hidden"
            :class="{
              'bg-gray-300': view === viewOptions.list,
              'hover:bg-gray-100': view !== viewOptions.list
            }"
            @click="view = viewOptions.list"
          >
            <icon-list class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
          </div>
          <div
            class="py-1 px-1.5 flex items-center cursor-pointer overflow-hidden"
            :class="{
              'bg-gray-300': view === viewOptions.grid,
              'hover:bg-gray-100': view !== viewOptions.grid
            }"
            @click="view = viewOptions.grid"
          >
            <icon-grid class="h-6 w-6 stroke-1 stroke-gray-700 fill-transparent" />
          </div>
        </div>
        <div
          class="rounded border border-gray-300 py-1 px-1.5 flex items-center cursor-pointer"
          :class="{
            'bg-gray-300': showAdjustments,
            'hover:bg-gray-100': !showAdjustments
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
      <!-- events list -->
      <table v-show="view === viewOptions.list" class="w-full mt-4">
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
          <tr v-for="(event, i) in filteredEvents" :key="i" class="hover:bg-sky-400/10 hover:shadow-lg cursor-pointer" @click="showEvent = event">
            <td class="align-middle">
              <div class="rounded-full w-3 h-3 bg-sky-400 mx-auto"></div>
            </td>
            <td v-if="columnVisible('title')" class="py-2 px-2">
              <span>{{ event.title }}</span>
            </td>
            <td v-if="columnVisible('status')" class="py-2 px-2 text-sm">
              <span>{{ t('label.' + event.status) }}</span>
            </td>
            <td v-if="columnVisible('mode')" class="py-2 px-2 text-sm">
              <span>{{ event.mode }}</span>
            </td>
            <td v-if="columnVisible('calendar')" class="py-2 px-2 text-sm">
              <span>{{ event.calendar }}</span>
            </td>
            <td v-if="columnVisible('bookingLink')" class="py-2 px-2 text-sm">
              <a :href="'https://apmt.day/' + event.slug" class="text-teal-500 underline" target="_blank" @click.stop="null">
                https://apmt.day/{{ event.slug }}
              </a>
            </td>
            <td v-if="columnVisible('replies')" class="py-2 px-2 text-sm">
              <span>{{ repliesCount(event) }} {{ t('label.bookings', repliesCount(event)) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
      <!-- events grid -->
      <div v-show="view === viewOptions.grid" class="w-full mt-4 flex flex-wrap justify-evenly gap-8">
        <div v-for="(event, i) in filteredEvents" :key="i" class="w-1/4 hover:bg-sky-400/10 hover:shadow-md rounded border-dashed border-t-2 border-r-2 border-b-2 border-sky-400 cursor-pointer" @click="showEvent = event">
          <div class="px-4 py-3 -my-0.5 rounded border-l-8 border-sky-400">
            <div>{{ event.title }}</div>
            <div class="pl-4 text-sm">{{ t('label.' + event.status) }}</div>
            <div class="pl-4 text-sm">{{ event.calendar }}</div>
            <div class="px-4 text-sm">
              <switch-toggle :active="event.mode === 'open'" :label="t('label.activeEvent')" @click.stop="null" />
            </div>
            <div class="pl-4 text-sm">
              <a :href="'https://apmt.day/' + event.slug" class="text-teal-500 underline" target="_blank" @click.stop="null">
                https://apmt.day/{{ event.slug }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- page side bar -->
    <div class="w-1/5 flex flex-col gap-8">
      <!-- monthly mini calendar -->
      <calendar-month
        :selected="activeDate"
        :mini="true"
        :nav="true"
        @prev="dateNav('month', false)"
        @next="dateNav('month')"
        @selected="selectDate"
      />
    </div>
  </div>
  <event-modal :open="showEvent !== null" :event="showEvent" @close="closeEventModal" />
</template>

<script setup>
import { ref, inject, computed } from 'vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import EventModal from '@/components/EventModal.vue';
import IconSearch from '@/elements/icons/IconSearch.vue';
import IconList from '@/elements/icons/IconList.vue';
import IconGrid from "@/elements/icons/IconGrid.vue";
import IconCheck from "@/elements/icons/IconCheck.vue";
import IconAdjustments from "@/elements/icons/IconAdjustments.vue";
import SwitchToggle from '@/elements/SwitchToggle.vue';
import { vOnClickOutside } from '@vueuse/components';
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from 'vue-router';
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject("dayjs");

// handle calendar output
const activeDate = ref(dj()); // current selected date, defaults to now
const selectDate = (d) => activeDate.value = dj(d);

// menu items for tab navigation
const tabItems = {
  'all':     0,
  'booked':  1,
  'pending': 2,
  'past':    3,
};
const tabActive = ref(route.params.view ? tabItems[route.params.view] : tabItems.all);
const updateTab = view => {
  router.replace({ name: route.name, params: { view: view } });
  tabActive.value = tabItems[view];
};
// date navigation
const dateNav = (unit = 'auto', forward = true) => {
  if (unit === 'auto') {
    unit = Object.keys(tabItems).find(key => tabItems[key] === tabActive.value);
  }
  if (forward) {
    activeDate.value = activeDate.value.add(1, unit);
  } else {
    activeDate.value = activeDate.value.subtract(1, unit);
  }
};

// columns for list view
const columns = {
  'title':       0,
  'status':      1,
  'mode':        2,
  'calendar':    3,
  'bookingLink': 4,
  'replies':     5,
};

// handle data filter
const filterOptions = {
  'allEvents':        0,
  'eventsToday':      1,
  'eventsNext7Days':  2,
  'eventsNext14Days': 3,
  'eventsNext31Days': 4,
  'eventsInMonth':    5,
  'allFutureEvents':  6,
};
const filter = ref(filterOptions.eventsToday);

// handle data search
const search = ref('');

// handle data view
const viewOptions = {
  'list': 0,
  'grid': 1,
};
const view = ref(viewOptions.list);

// handle view adjustments: column visibility
const showAdjustments = ref(false);
const visibleColumns = ref(Object.values(columns));
const openAdjustments = () => showAdjustments.value = true;
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
const fakeEvents = [
  { title: 'Bi-weekly Café Dates', status: 'past', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Online', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-10-30T10:00:00', duration: 60, attendee: null }] },
  { title: 'Weekly ZOOM', status: 'past', mode: 'open', calendar: 'Family', slug: 'sdfw83jc', location_name: 'ZOOM', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-10-31T10:00:00', duration: 60, attendee: { name: 'John Doe', email: 'john@doe.com' } }] },
  { title: 'Jour Fixe Team', status: 'booked', mode: 'open', calendar: 'Family', slug: 'sdfw83jc', location_name: 'Teams', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-11T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
  { title: 'Project Appointment', status: 'pending', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Jitsi', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-12T10:00:00', duration: 60, attendee: null }] },
  { title: 'Team Building Event', status: 'booked', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'BigBlueButton', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-13T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }, { start: '2022-11-13T11:00:00', duration: 60, attendee: null }, { start: '2022-11-13T12:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'jane@doe.com' } }] },
  { title: 'Bi-weekly Café Dates', status: 'pending', mode: 'closed', calendar: 'Family', slug: 'sdfw83jc', location_name: 'Signal', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-14T10:00:00', duration: 60, attendee: null }] },
  { title: 'Weekly ZOOM', status: 'booked', mode: 'closed', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Online', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-15T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
  { title: 'Jour Fixe Team', status: 'booked', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Phone', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-16T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
  { title: 'Project Appointment', status: 'booked', mode: 'closed', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Park', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-17T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
  { title: 'Team Building Event', status: 'booked', mode: 'closed', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Building 429, Room 5', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-18T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
  { title: 'Team Building Event', status: 'booked', mode: 'closed', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Building 429, Room 5', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-18T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
  { title: 'Team Building Event', status: 'booked', mode: 'closed', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Building 429, Room 5', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-11-18T10:00:00', duration: 60, attendee:  { name: 'John Doe', email: 'john@doe.com' } }] },
];

// handle filtered events list
const filteredEvents = computed(() => {
  let list = fakeEvents;
  // by search input
  if (search.value !== '') {
    list = list.filter(e => e.title.toLowerCase().includes(search.value.toLowerCase()))
  }
  // by active tab
  switch (tabActive.value) {
    case tabItems.booked:
      list = list.filter(e => e.status === 'booked');
      break;
    case tabItems.pending:
      list = list.filter(e => e.status === 'pending');
      break;
    case tabItems.past:
      list = list.filter(e => e.status === 'past');
      break;
    case tabItems.all:
    default:
      break;
  }
  return list;
});

// return number of booked slots (replies) for given event
const repliesCount = event => event.slots.filter(s => s.attendee !== null).length;

// handle single event modal
const showEvent = ref(null);
const closeEventModal = () => showEvent.value = null;
</script>
