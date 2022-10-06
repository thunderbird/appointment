<template>
  <div class="flex justify-between">
    <page-heading :bold="today.month" :light="today.year" />
    <div class="flex gap-8">
      <button class="font-semibold text-xl text-teal-500 px-4">
        {{ t('label.today') }}
      </button>
      <tab-bar :tab-items="tabItems" />
    </div>
  </div>
</template>

<script setup>
import PageHeading from '@/elements/PageHeading.vue';
import TabBar from '@/components/TabBar.vue';
import { useI18n } from "vue-i18n";
const { t, locale } = useI18n();

// handle localized date output
const now = new Date();
const today = {
  month: now.toLocaleString(locale.value, { month: "long" }),
  year: now.getFullYear()
}

// menu items for tab navigation
const tabItems = ['day', 'week', 'month'];
</script>
