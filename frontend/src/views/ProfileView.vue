<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <div class="text-4xl font-light">{{ t('heading.yourProfile') }}</div>
  </div>
  <div class="grid grid-cols-2 w-max mt-4">
    <template v-for="(value, key) in user" :key="key">
      <pre>{{ key }}</pre>
      <div>{{ value }}</div>
    </template>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

// component constants
const { t } = useI18n();

// view properties
defineProps({
  calendars:    Array,  // list of calendars from db
  appointments: Array,  // list of appointments from db
  user:         Object, // currently logged in user, null if not logged in
});
</script>
