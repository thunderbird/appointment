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
      <table class="w-full mt-4">
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
          <tr v-for="(event, i) in filteredEvents" :key="i" class="hover:bg-sky-400/10 hover:shadow-lg">
            <td class="align-middle">
              <div class="rounded-full w-3 h-3 bg-sky-400 mx-auto"></div>
            </td>
            <template v-for="(value, key) in event" :key="key">
              <td
                v-if="columnVisible(key)"
                class="py-2 px-2"
                :class="{
                  'text-sm': key !== 'title',
                  'text-teal-500 underline': key === 'bookingLink',
                }"
              >
                {{ value }}
              </td>
            </template>
          </tr>
        </tbody>
      </table>
      <!-- events grid -->
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

</template>

<script setup>
import { ref, inject, computed } from 'vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import IconSearch from '@/elements/icons/IconSearch.vue';
import IconList from '@/elements/icons/IconList.vue';
import IconGrid from "../elements/icons/IconGrid.vue";
import IconCheck from "../elements/icons/IconCheck.vue";
import IconAdjustments from "../elements/icons/IconAdjustments.vue";
import { vOnClickOutside } from '@vueuse/components';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
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
const tabActive = ref(tabItems.all);
const updateTab = n => tabActive.value = n;

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
};

// handle filter
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

// handle search
const search = ref('');

// handle view
const viewOptions = {
  'list': 0,
  'grid': 1,
};
const view = ref(viewOptions.list);

// handle view adjustments
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
}
const restoreColumnOrder = () => {
  visibleColumns.value = Object.values(columns);
}

// TODO: fake data
const fakeEvents = [
  { title: 'Bi-weekly Café Dates', status: 'past', mode: 'open', calendar: 'Work', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Weekly ZOOM', status: 'past', mode: 'open', calendar: 'Family', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Jour Fixe Team', status: 'booked', mode: 'open', calendar: 'Family', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Project Appointment', status: 'pending', mode: 'open', calendar: 'Work', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Team Building Event', status: 'booked', mode: 'open', calendar: 'Work', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Bi-weekly Café Dates', status: 'pending', mode: 'closed', calendar: 'Family', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Weekly ZOOM', status: 'booked', mode: 'closed', calendar: 'Work', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Jour Fixe Team', status: 'booked', mode: 'open', calendar: 'Work', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Project Appointment', status: 'booked', mode: 'closed', calendar: 'Work', bookingLink: 'https://apmt.day/sdfw83jc' },
  { title: 'Team Building Event', status: 'booked', mode: 'closed', calendar: 'Work', bookingLink: 'https://apmt.day/sdfw83jc' },
]

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
})
</script>
