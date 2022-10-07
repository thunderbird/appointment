<template>
  <!-- page title area -->
  <div class="flex justify-between">
    <page-heading
      :bold="cal.active.date.format('MMMM')"
      :light="cal.active.date.year().toString()"
    />
    <div class="flex gap-8">
      <button @click="cal.active.date = dj()" class="font-semibold text-xl text-teal-500 px-4">
        {{ t('label.today') }}
      </button>
      <tab-bar :tab-items="tabItems" :active="2" />
      <primary-button :label="t('label.createEvent')" />
    </div>
  </div>
  <!-- page content -->
  <div class="flex justify-between gap-24 mt-8">
    <!-- main section: big calendar -->
    <calendar-month class="w-4/5" :selected="cal.active.date" />
    <!-- page side bar -->
    <div class="w-1/5">
      <calendar-month
        :selected="cal.active.date"
        :mini="true"
        :nav="true"
        @prev="cal.active.date = cal.active.date.subtract(1, 'month')"
        @next="cal.active.date = cal.active.date.add(1, 'month')"
      />
    </div>
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
