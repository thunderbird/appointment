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
      <div class="flex gap-5">
        <select class="rounded border border-gray-300 text-sm">
          <option v-for="(k, o) in filter" :key="k" :value="k">{{ t('label.' + o) }}</option>
        </select>
        <div class="w-full relative">
          <label for="events-search" class="absolute top-1/2 -translate-y-1/2 left-3 cursor-text">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 stroke-2 stroke-gray-400 fill-transparent" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
              <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
              <circle cx="10" cy="10" r="7" />
              <line x1="21" y1="21" x2="15" y2="15" />
            </svg>
          </label>
          <input type="search" id="events-search" class="rounded border border-gray-300 w-full pl-10 text-sm" placeholder="Search events" />
        </div>
        <div class="rounded border border-gray-300 flex">
          <div class="border-r border-gray-300 py-1 px-1.5 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 stroke-1 stroke-gray-600 fill-transparent" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
              <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
              <line x1="9" y1="6" x2="20" y2="6" />
              <line x1="9" y1="12" x2="20" y2="12" />
              <line x1="9" y1="18" x2="20" y2="18" />
              <line x1="5" y1="6" x2="5" y2="6.01" />
              <line x1="5" y1="12" x2="5" y2="12.01" />
              <line x1="5" y1="18" x2="5" y2="18.01" />
            </svg>
          </div>
          <div class="py-1 px-1.5 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 stroke-1 stroke-gray-600 fill-transparent" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
              <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
              <rect x="4" y="4" width="6" height="6" rx="1" />
              <rect x="14" y="4" width="6" height="6" rx="1" />
              <rect x="4" y="14" width="6" height="6" rx="1" />
              <rect x="14" y="14" width="6" height="6" rx="1" />
            </svg>
          </div>
        </div>
        <div class="rounded border border-gray-300 py-1 px-1.5 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 stroke-1 stroke-gray-600 fill-transparent" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
            <circle cx="6" cy="10" r="2" />
            <line x1="6" y1="4" x2="6" y2="8" />
            <line x1="6" y1="12" x2="6" y2="20" />
            <circle cx="12" cy="16" r="2" />
            <line x1="12" y1="4" x2="12" y2="14" />
            <line x1="12" y1="18" x2="12" y2="20" />
            <circle cx="18" cy="7" r="2" />
            <line x1="18" y1="4" x2="18" y2="5" />
            <line x1="18" y1="9" x2="18" y2="20" />
          </svg>
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
      />
    </div>
  </div>

</template>

<script setup>
import { ref, inject } from 'vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// handle calendar output
const activeDate = ref(dj()); // current selected date, defaults to now

// menu items for tab navigation
const tabItems = {
  'all': 0,
  'booked': 1,
  'pending': 2,
  'past': 3
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

// filter fields
const filter = {
  'allEvents': 0,
  'eventsToday': 1,
  'eventsNext7Days': 2,
  'eventsNext14Days': 3,
  'eventsNext31Days': 4,
  'eventsInMonth': 5,
  'allFutureEvents': 6,
}
</script>
