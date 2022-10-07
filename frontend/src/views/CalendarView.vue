<template>
  <div class="flex justify-between">
    <page-heading :bold="today.month" :light="today.year" />
    <div class="flex gap-8">
      <button class="font-semibold text-xl text-teal-500 px-4">
        {{ t('label.today') }}
      </button>
      <tab-bar :tab-items="tabItems" />
      <primary-button :label="t('label.createEvent')" />
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue';
import PageHeading from '@/elements/PageHeading.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// handle date output
const today = {
  month: dj().format('MMMM'),
  year: dj().year()
}

// menu items for tab navigation
const tabItems = ['day', 'week', 'month'];
</script>
