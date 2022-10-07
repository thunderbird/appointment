<template>
  <!-- page title area -->
  <div class="flex justify-between">
    <page-heading
      :bold="cal.active.date.format('MMMM')"
      :light="cal.active.date.year().toString()"
    />
    <div class="flex gap-8">
      <button class="font-semibold text-xl text-teal-500 px-4">
        {{ t('label.today') }}
      </button>
      <tab-bar :tab-items="tabItems" />
      <primary-button :label="t('label.createEvent')" />
    </div>
  </div>
  <!-- page content -->
  <div class="flex justify-between gap-16 mt-8">
    <!-- main section: big calendar -->
    <calendar-month class="w-3/4" :selected="cal.active.date" />
    <!-- page side bar -->
    <div class="w-1/4">Small calendar</div>
  </div>

</template>

<script setup>
import { reactive, inject } from 'vue';
import PageHeading from '@/elements/PageHeading.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// handle calendar output
const cal = reactive({
	active: {
    date: dj()
  }
});

// menu items for tab navigation
const tabItems = ['day', 'week', 'month'];
</script>
