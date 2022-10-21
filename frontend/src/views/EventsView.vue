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
            <icon-search class="h-4 w-4 stroke-2 stroke-gray-400 fill-transparent" /> 
          </label>
          <input type="search" id="events-search" class="rounded border border-gray-300 w-full pl-10 text-sm" placeholder="Search events" />
        </div>
        <div class="rounded border border-gray-300 flex">
          <div class="border-r border-gray-300 py-1 px-1.5 flex items-center">
            <icon-list class="h-6 w-6 stroke-1 stroke-gray-600 fill-transparent" />
          </div>
          <div class="py-1 px-1.5 flex items-center">
            <icon-grid class="h-6 w-6 stroke-1 stroke-gray-600 fill-transparent" />
          </div>
        </div>
        <div class="rounded border border-gray-300 py-1 px-1.5 flex items-center">
          <icon-adjustments class="h-6 w-6 stroke-1 stroke-gray-600 fill-transparent" />
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
import IconSearch from '@/elements/icons/IconSearch.vue';
import IconList from '@/elements/icons/IconList.vue';
import IconGrid from "../elements/icons/IconGrid.vue";
import IconAdjustments from "../elements/icons/IconAdjustments.vue";
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
