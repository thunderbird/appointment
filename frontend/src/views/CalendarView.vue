<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <calendar-page-heading
      :month="activeDate.format('MMMM')"
      :year="activeDate.year().toString()"
      :title="pageTitle"
      @prev="dateNav('auto', false)"
      @next="dateNav('auto')"
    />
    <div class="flex gap-8 items-center">
      <button @click="activeDate = dj()" class="font-semibold text-xl text-teal-500 px-4">
        {{ t('label.today') }}
      </button>
      <tab-bar :tab-items="Object.keys(tabItems)" :active="tabActive" @update="updateTab" />
      <primary-button :label="t('label.createEvent')" />
    </div>
  </div>
  <!-- page content -->
  <div class="flex justify-between gap-24 mt-8">
    <!-- main section: big calendar showing active month, week or day -->
    <calendar-month v-show="tabActive === tabItems.month" class="w-4/5" :selected="activeDate" />
    <calendar-week v-show="tabActive === tabItems.week" class="w-4/5" :selected="activeDate" />
    <calendar-day v-show="tabActive === tabItems.day" class="w-4/5" :selected="activeDate" />
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
      <!-- events -->
      <div>
        <div class="flex justify-between items-center">
          <div class="font-semibold text-lg">{{ t('heading.pendingAndActive') }}</div>
          <router-link class="px-2 py-1 border-r rounded-full bg-teal-500 text-white text-xs uppercase" :to="{ name: 'events' }">
            {{ t('label.viewAll') }}
          </router-link>
        </div>
        <div class="text-slate-500 mt-4">
          {{ t('info.noEventsInList') }}
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref, inject, computed } from 'vue';
import CalendarPageHeading from '@/elements/CalendarPageHeading.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import CalendarWeek from '@/components/CalendarWeek.vue';
import CalendarDay from '@/components/CalendarDay.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// handle calendar output
const activeDate = ref(dj()); // current selected date, defaults to now
const selectDate = (d) => activeDate.value = dj(d);

// date calculations
const startOfActiveWeek = computed(() => {
  return activeDate.value.startOf('week');
});
const endOfActiveWeek = computed(() => {
  return activeDate.value.endOf('week');
});

// menu items for tab navigation
const tabItems = { 'day': 0, 'week': 1, 'month': 2 };
const tabActive = ref(tabItems.month);
const updateTab = (n) => tabActive.value = n;

// calculate page title
const pageTitle = computed(() => {
  switch (tabActive.value) {
    case tabItems.day:
      return activeDate.value.format('dddd Do');
    case tabItems.week:
      return startOfActiveWeek.value.format('ddd Do') + ' - ' + endOfActiveWeek.value.format('ddd Do');
    case tabItems.month:
    default:
      return ''
  }
});

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
</script>
