<template>
  <div class="select-none">
    <div v-if="nav" class="flex-center mb-2 select-none gap-2">
      <div @click="dateNav(false)" class="btn-back group cursor-pointer" :title="t('label.goBack')">
        <icon-chevron-left class="size-6 fill-transparent stroke-slate-400 stroke-2 group-hover:stroke-teal-500" />
      </div>
      <div class="text-lg font-semibold text-teal-500">
        {{ navDate.format('MMMM YYYY')}}
      </div>
      <div @click="dateNav(true)" class="btn-forward group cursor-pointer" :title="t('label.goForward')">
        <icon-chevron-right class="size-6 fill-transparent stroke-slate-400 stroke-2 group-hover:stroke-teal-500" />
      </div>
    </div>
    <div class="
      grid w-full grid-cols-7 gap-px overflow-hidden rounded-lg border
    border-gray-200 bg-gray-200 dark:border-gray-500 dark:bg-gray-500
    ">
      <div
        v-for="h in isoWeekdays"
        :key="h"
        class="bg-gray-100 py-2 text-center text-gray-500 dark:bg-gray-600 dark:text-gray-300"
      >
        {{ h.min }}
      </div>
      <calendar-mini-month-day
        v-for="d in days"
        :key="d.date"
        :day="d.date"
        :is-active="d.active"
        :is-selected="d.date === date"
        :is-today="d.date === today"
        :placeholder="placeholder"
        :has-events="!!eventsByDate(d.date).length"
        :show-details="!placeholder"
        :popup-position="popupPosition"
        :disabled="dateDisabled(d.date)"
        @click="!placeholder && !dateDisabled(d.date) ? emit('daySelected', d.date) : null"
        @event-selected="eventSelected"
      />
    </div>
  </div>
</template>

<script setup>
import {
  ref, computed, inject, watch,
} from 'vue';
import CalendarMiniMonthDay from '@/elements/calendar/CalendarMiniMonthDay';
import { useI18n } from 'vue-i18n';

// icons
import {
  IconChevronLeft,
  IconChevronRight,
} from '@tabler/icons-vue';
import { appointmentState } from '@/definitions';
import { dayjsKey } from "@/keys";

// component constants
const { t } = useI18n();
const dj = inject(dayjsKey);
const isoWeekdays = inject('isoWeekdays');
const isoFirstDayOfWeek = inject('isoFirstDayOfWeek');

// component properties
const props = defineProps({
  selected: Object, // currently active date (dayjs object)
  nav: Boolean, // show month navigation
  placeholder: Boolean, // format appointments as placeholder
  minDate: Object, // minimum active date in view (dayjs object)
  appointments: Array, // data of appointments to show
  events: Array, // data of calendar events to show
  schedules: Array, // data of scheduled event previews to show
  popupPosition: String, // currently supported: right, left, top
});

// component emits
const emit = defineEmits(['daySelected', 'eventSelected']);

// handle events to show
// make all events accessible by date key
const events = computed(() => {
  const eventsOnDate = {};
  // add appointments
  props.appointments?.forEach((event) => {
    event.slots.forEach((slot) => {
      const key = dj(slot.start).format('YYYY-MM-DD');
      if (key in eventsOnDate) {
        eventsOnDate[key].push({ ...event, ...slot });
      } else {
        eventsOnDate[key] = [{ ...event, ...slot }];
      }
    });
  });
  // add calendar events
  props.events?.forEach((event) => {
    const key = dj(event.start).format('YYYY-MM-DD');
    if (key in eventsOnDate) {
      eventsOnDate[key].push({ ...event, remote: true });
    } else {
      eventsOnDate[key] = [{ ...event, remote: true }];
    }
  });
  // add schedules
  props.schedules?.forEach((event) => {
    event.slots?.forEach((slot) => {
      const key = dj(slot.start).format('YYYY-MM-DD');
      if (key in eventsOnDate) {
        eventsOnDate[key].push({ ...event, ...slot, preview: true });
      } else {
        eventsOnDate[key] = [{ ...event, ...slot, preview: true }];
      }
    });
  });
  return eventsOnDate;
});
// get all relevant events on a given date (pending, with attendee or remote)
const eventsByDate = (d) => {
  const key = dj(d).format('YYYY-MM-DD');
  if (key in events.value) {
    return props.placeholder
      ? events.value[key].filter((e) => dj(e.start).isAfter(dj()))
      : events.value[key].filter(
        (e) => (dj(e.start).add(e.duration, 'minutes').isAfter(dj()) && e.status === appointmentState.pending)
            || (e.attendee && e.status === appointmentState.pending)
            || e.remote
            || e.preview,
      );
  }
  return [];
};
const eventSelected = (d) => {
  emit('eventSelected', d);
};
const dateDisabled = (d) => props.minDate && dj(d).isBefore(props.minDate, 'day');

// handle nav date (only used if navigation is active)
const navDate = ref(props.selected); // current selected date for independent navigation
const dateNav = (forward = true) => {
  if (forward) {
    navDate.value = navDate.value.add(1, 'month');
  } else {
    navDate.value = navDate.value.subtract(1, 'month');
  }
};
watch(() => props.selected, (selection) => {
  navDate.value = dj(selection);
});

// basic data for selected month
const today = computed(() => dj().format('YYYY-MM-DD'));
const date = computed(() => props.selected.format('YYYY-MM-DD'));
const month = computed(() => Number(navDate.value.format('M')));
const year = computed(() => Number(navDate.value.format('YYYY')));
const numberOfDaysInMonth = computed(() => dj(navDate.value).daysInMonth());

const currentMonthDays = computed(() => [...Array(numberOfDaysInMonth.value)].map((_, index) => ({
  date: dj(`${year.value}-${month.value}-${index + 1}`).format('YYYY-MM-DD'),
  active: true,
})));

const previousMonthDays = computed(() => {
  // Cover first day of the month being sunday (firstDayOfTheMonthWeekday === 0)
  const firstDayOfTheMonthWeekday = dj(currentMonthDays.value[0].date).isoWeekday();
  const visibleNumberOfDaysFromPreviousMonth = firstDayOfTheMonthWeekday !== isoFirstDayOfWeek
    ? firstDayOfTheMonthWeekday - (isoFirstDayOfWeek % 7)
    : 0;

  const previousMonthLastMondayDayOfMonth = dj(currentMonthDays.value[0].date)
    .subtract(visibleNumberOfDaysFromPreviousMonth, 'day')
    .date();

  const previousMonth = dj(`${year.value}-${month.value}-01`).subtract(1, 'month');
  return [...Array(visibleNumberOfDaysFromPreviousMonth)].map(
    (_, index) => ({
      date: dj(
        `${previousMonth.year()}-${previousMonth.month() + 1}-${
          previousMonthLastMondayDayOfMonth + index
        }`,
      ).format('YYYY-MM-DD'),
      active: false,
    }),
  );
});

const nextMonthDays = computed(() => {
  // fill in rest days in calendar grid
  const restDays = 7 - ((previousMonthDays.value.length + currentMonthDays.value.length) % 7);
  const visibleNumberOfDaysFromNextMonth = restDays === 7 ? 0 : restDays;

  const nextMonth = dj(`${year.value}-${month.value}-01`).add(1, 'month');
  return [...Array(visibleNumberOfDaysFromNextMonth)].map((_, index) => ({
    date: dj(
      `${nextMonth.year()}-${nextMonth.month() + 1}-${index + 1}`,
    ).format('YYYY-MM-DD'),
    active: false,
  }));
});

// all day cells in current month view
const days = computed(() => [
  ...previousMonthDays.value,
  ...currentMonthDays.value,
  ...nextMonthDays.value,
]);
</script>
