<template>
  <div class="calendar">
    <h2 class="flex gap-3">
      <span class="text-4xl">{{ today.month }}</span>
      <span class="text-4xl font-light">{{ today.year }}</span>
    </h2>
  </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";
const { locale } = useI18n();

const now = new Date();
const today = {
  month: now.toLocaleString(locale.value, { month: "long" }),
  year: now.getFullYear()
}
</script>
