<template>
  <div class="calendar">
    <page-heading :bold="today.month" :light="today.year" />
  </div>
</template>

<script setup>
import PageHeading from '@/elements/PageHeading.vue';

import { useI18n } from "vue-i18n";
const { locale } = useI18n();

const now = new Date();
const today = {
  month: now.toLocaleString(locale.value, { month: "long" }),
  year: now.getFullYear()
}
</script>
