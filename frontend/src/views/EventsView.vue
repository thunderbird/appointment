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
    <!-- main section: big calendar showing active month, week or day -->
    <div>test</div>
    <!-- page side bar -->
    <div class="w-1/5 flex flex-col gap-8">
      <!-- monthly mini calendar -->
      <calendar-month
        :selected="cal.active.date"
        :mini="true"
        :nav="true"
        @prev="dateNav('month', false)"
        @next="dateNav('month')"
      />
    </div>
  </div>

</template>

<script setup>
import { reactive, ref, inject } from 'vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// handle calendar output
const cal = reactive({
	active: {
    date: dj() // current selected date, defaults to now
  }
});

// menu items for tab navigation
const tabItems = { 'all': 0, 'booked': 1, 'pending': 2, 'past': 2 };
const tabActive = ref(tabItems.all);
const updateTab = n => tabActive.value = n;

// date navigation
const dateNav = (unit = 'auto', forward = true) => {
  if (unit === 'auto') {
    unit = Object.keys(tabItems).find(key => tabItems[key] === tabActive.value);
  }
  if (forward) {
    cal.active.date = cal.active.date.add(1, unit);
  } else {
    cal.active.date = cal.active.date.subtract(1, unit);
  }
};
</script>
