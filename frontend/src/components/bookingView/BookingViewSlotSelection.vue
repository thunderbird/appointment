<template>
  <div v-if="appointment">
    <div class="text-3xl text-gray-700 dark:text-gray-400 mb-4">{{ appointment.title }}</div>
    <div class="font-semibold">
      {{ t('text.nameIsInvitingYou', {name: appointment.owner_name}) }}
    </div>
    <div class="text-gray-700 dark:text-gray-400 mb-6">{{ appointment.details }}</div>
    <div class="text-xl mb-6">{{ t('text.chooseDateAndTime') }}</div>
    <calendar-page-heading
      :nav="showNavigation && activeView === views.month"
      :month="activeDate.format('MMMM')"
      :year="activeDate.year().toString()"
      :title="viewTitle"
      :backlink="activeView === views.weekAfterMonth"
      @prev="dateNav('month', false)"
      @next="dateNav('month')"
      @back="activeView = views.month"
    />
    <calendar-qalendar
      class="w-full"
      :selected="activeDate"
      :appointments="[appointment]"
      :booking="true"
      @event-selected="selectEvent"
    >
    </calendar-qalendar>
    <!--
    <calendar-month
      v-if="(activeView === views.month)"
      :selected="activeDate"
      :appointments="dayPlaceholder"
      :placeholder="true"
      @event-selected="showWeek"
    />
    <calendar-week
      v-if="(activeView === views.week || activeView === views.weekAfterMonth)"
      :selected="activeDate"
      :appointments="[appointment]"
      :booking="true"
      @event-selected="selectEvent"
    />
    <calendar-day
      v-if="(activeView === views.day)"
      :selected="activeDate"
      :appointments="[appointment]"
      :booking="true"
      @event-selected="selectEvent"
    />
    -->
  </div>
  <!-- fixed footer with action button -->
  <footer
    class="
          fixed bottom-0 left-0 h-24 w-full px-4 border-t
          bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600
        "
  >
    <div class="h-full max-w-screen-2xl mx-auto flex justify-end items-center">
      <primary-button
        class="p-7"
        :label="t('label.confirmSelection')"
        :disabled="!selectedEvent"
        @click="emit('openModal')"
      />
    </div>
  </footer>
</template>
<script setup>
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';

import { bookingCalendarViews as views } from '@/definitions';
import { useBookingViewStore } from '@/stores/booking-view-store';

import CalendarDay from '@/components/CalendarDay';
import CalendarMonth from '@/components/CalendarMonth';
import CalendarPageHeading from '@/elements/CalendarPageHeading';
import CalendarWeek from '@/components/CalendarWeek';
import PrimaryButton from '@/elements/PrimaryButton';
import { computed, inject } from 'vue';
import CalendarQalendar from '@/components/CalendarQalendar.vue';

const { t } = useI18n();
const dj = inject('dayjs');
const {
  appointment, activeView, activeDate, selectedEvent,
} = storeToRefs(useBookingViewStore());

const startOfActiveWeek = computed(() => activeDate.value.startOf('week'));
const endOfActiveWeek = computed(() => activeDate.value.endOf('week'));

const emit = defineEmits(['openModal']);
defineProps({
  showNavigation: Boolean,
});

// Computed

/**
 * Appointment data formatted for the month calendar view.
 * @type {ComputedRef<[{slots: [], title: string}]>}
 */
const dayPlaceholder = computed(() => {
  const apmt = { title: t('label.checkAvailableSlots'), slots: [] };
  const existingDates = [];
  appointment.value?.slots.forEach((slot) => {
    const key = dj(slot.start).format('YYYY-MM-DD');
    if (!existingDates.includes(key)) {
      existingDates.push(key);
      apmt.slots.push(slot);
    }
  });
  return [apmt];
});

/**
 * Returns the formatted date depending on the current calendar view
 * @type {ComputedRef<string>}
 */
const viewTitle = computed(() => {
  switch (activeView.value) {
    case views.day:
      return activeDate.value.format('dddd Do');
    case views.week:
    case views.weekAfterMonth:
      return `${startOfActiveWeek.value.format('ddd Do')} - ${endOfActiveWeek.value.format('ddd Do')}`;
    default:
      return '';
  }
});

// Functions

/**
 * Adjusts the date by 1 unit (e.g. month, day, week.) Direction is determined by forward.
 * @param unit string
 * @param forward bool
 */
const dateNav = (unit = 'month', forward = true) => {
  if (forward) {
    activeDate.value = activeDate.value.add(1, unit);
  } else {
    activeDate.value = activeDate.value.subtract(1, unit);
  }
};

/**
 * Display a specific week within our calendar view.
 * This is triggered when you click into an event on the monthly calendar view.
 * @param day string
 */
const showWeek = (day) => {
  activeDate.value = dj(day);
  activeView.value = views.weekAfterMonth;
};

/**
 * Select a specific time slot
 * @param day string
 */
const selectEvent = (day) => {
  // set event selected
  for (let i = 0; i < appointment.value.slots.length; i += 1) {
    const slot = appointment.value.slots[i];
    if (slot.start.format('YYYY-MM-DD HH:mm') === day) {
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
