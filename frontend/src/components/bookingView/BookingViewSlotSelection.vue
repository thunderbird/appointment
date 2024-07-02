<template>
  <div v-if="appointment">
    <div class="mb-4 text-3xl text-gray-700 dark:text-gray-400">
      {{ appointment.title }}
    </div>
    <div class="mb-4 font-semibold">
      {{ t('text.nameIsInvitingYou', { name: appointment.owner_name }) }}
    </div>
    <div v-if="appointment.details" class="mb-6 text-gray-700 dark:text-gray-400">
      {{ appointment.details }}
    </div>
    <div class="mb-6 flex flex-col items-center justify-between md:flex-row">
      <div class="text-xl">{{ t('text.chooseDateAndTime') }}</div>
      <div class="text-sm text-teal-600 dark:text-teal-500">
        {{ t('text.timesAreDisplayedInLocalTimezone', { timezone: dj.tz.guess() }) }}
      </div>
    </div>
    <calendar-qalendar
      class="w-full"
      :current-date="activeDate"
      :appointments="[appointment]"
      :is-booking-route="true"
      :fixed-duration="appointment?.slot_duration ?? activeSchedules[0]?.slot_duration"
      @event-selected="selectEvent"
    >
    </calendar-qalendar>
  </div>
  <!-- fixed footer with action button -->
  <footer
    class="fixed bottom-0 left-0 h-24 w-full border-t border-gray-300 bg-white px-4 dark:border-gray-600 dark:bg-gray-700"
  >
    <div class="mx-auto flex h-full max-w-screen-2xl items-center justify-end">
      <primary-button
        class="btn-confirm p-7"
        :label="t('label.confirmSelection')"
        :disabled="!selectedEvent"
        @click="emit('openModal')"
        :title="t('label.confirm')"
      />
    </div>
  </footer>
</template>
<script setup>
import { inject } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';

import { useBookingViewStore } from '@/stores/booking-view-store';
import { dateFormatStrings } from '@/definitions';

import PrimaryButton from '@/elements/PrimaryButton';
import CalendarQalendar from '@/components/CalendarQalendar.vue';
import { useScheduleStore } from '@/stores/schedule-store';
import { dayjsKey } from "@/keys";

const { t } = useI18n();
const { activeSchedules } = storeToRefs(useScheduleStore());
const { appointment, activeDate, selectedEvent } = storeToRefs(useBookingViewStore());
const dj = inject(dayjsKey);

const emit = defineEmits(['openModal']);

defineProps({
  showNavigation: Boolean,
});

/**
 * Select a specific time slot
 * @param day string
 */
const selectEvent = (day) => {
  // set event selected
  for (let i = 0; i < appointment.value.slots.length; i += 1) {
    const slot = appointment.value.slots[i];
    if (slot.start.format(dateFormatStrings.qalendar) === day) {
      slot.selected = true;
      const e = { ...appointment.value, ...slot };
      delete e.slots;
      selectedEvent.value = e;
    } else {
      slot.selected = false;
    }
  }
};

</script>
