<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { SelectOption } from '@/models';
import { useCalendarStore } from '@/stores/calendar-store';
import { SelectInput } from '@thunderbirdops/services-ui';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const calendarStore = useCalendarStore();
const { isLoaded, connectedCalendars } = storeToRefs(calendarStore);

const calendarOptions = computed<SelectOption[]>(() => connectedCalendars.value.map((calendar) => ({
  label: calendar.title,
  value: calendar.id,
})));

onMounted(async () => {
  if (!isLoaded.value) {
    await calendarStore.fetch();
  }
})
</script>

<template>
  <select-input
    name="calendar"
    class="select-input"
    :options="calendarOptions"
  >
    {{ t("label.bookingTo") }}
  </select-input>
</template>

<style scoped>
  .select-input {
    width: 100%;
  }
</style>