<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { SelectOption } from '@/models';
import { SelectInput } from '@thunderbirdops/services-ui';
import { useI18n } from 'vue-i18n';
import { useCalendarStore } from '@/stores/calendar-store';
import { useAvailabilityStore } from '@/stores/availability-store';

const { t } = useI18n();
const calendarStore = useCalendarStore();
const availabilityStore = useAvailabilityStore();

const { currentState } = storeToRefs(availabilityStore);
const { isLoaded, connectedCalendars } = storeToRefs(calendarStore);

const calendarOptions = computed<SelectOption[]>(() => connectedCalendars.value.map((calendar) => ({
  label: calendar.title,
  value: calendar.id,
})));

const selectedCalendar = computed({
  get: () => currentState.value.calendar_id,
  set: (value) => {
    availabilityStore.$patch({ currentState: { calendar_id: value } })
  }
})

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
    v-model="selectedCalendar"
  >
    {{ t("label.bookingTo") }}
  </select-input>
</template>

<style scoped>
.select-input {
  width: 100%;
}
</style>