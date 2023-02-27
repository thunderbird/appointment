<template>
  <div class="select-none">
    <div v-if="nav" class="flex-center gap-2 mb-2 select-none">
      <div @click="dateNav(false)" class="group cursor-pointer">
        <icon-chevron-left class="h-6 w-6 stroke-2 fill-transparent stroke-slate-400 group-hover:stroke-teal-500" />
      </div>
      <div class="text-teal-500 font-semibold text-lg">
        {{ navDate.format('MMMM YYYY')}}
      </div>
      <div @click="dateNav(true)" class="group cursor-pointer">
        <icon-chevron-right class="h-6 w-6 stroke-2 fill-transparent stroke-slate-400 group-hover:stroke-teal-500" />
      </div>
    </div>
    <div class="
      grid grid-cols-7 gap-[1px] w-full border rounded-lg overflow-hidden 
    bg-gray-200 border-gray-200 dark:bg-gray-500 dark:border-gray-500
    ">
      <div
        v-for="h in weekdayNames()"
        :key="h"
        class="text-center py-2 text-gray-500 dark:text-gray-300 bg-gray-100 dark:bg-gray-600"
        :class="{ 'font-bold': !mini}"
      >
        {{ h }}
      </div>
      <calendar-month-day
        v-for="d in days"
        :key="d.date"
        :day="d.date"
        :is-active="d.active"
        :is-selected="d.date === date"
        :is-today="d.date === today"
        :mini="mini"
        :placeholder="placeholder"
        :events="eventsByDate(d.date)"
        :show-details="!placeholder"
        :disabled="dateDisabled(d.date)"
        @click="!placeholder && !dateDisabled(d.date) ? emit('daySelected', d.date) : null"
        @event-selected="eventSelected"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, watch } from 'vue';
import CalendarMonthDay from '@/elements/CalendarMonthDay';

// icons
import {
  IconChevronLeft,
  IconChevronRight,
} from '@tabler/icons-vue';
import { appointmentState } from '@/definitions';

// component constants
const dj = inject('dayjs');

// component properties
const props = defineProps({
  selected:     Object,  // currently active date (dayjs object)
  mini:         Boolean, // show small version of monthly calendar
  nav:          Boolean, // show month navigation
  placeholder:  Boolean, // format appointments as placeholder
  minDate:      Object,  // minimum active date in view (dayjs object)
  appointments: Array,   // data of appointments to show
  events:       Array,   // data of calendar events to show
});

// component emits
const emit = defineEmits(['daySelected', 'eventSelected']);

// handle events to show
// make all events accessible by date key
const events = computed(() => {
  const eventsOnDate = {};
  // add appointments
  props.appointments?.forEach(event => {
    event.slots.forEach(slot => {
      const key = dj(slot.start).format('YYYY-MM-DD');
      if (key in eventsOnDate) {
        eventsOnDate[key].push({...event, ...slot});
      } else {
        eventsOnDate[key] = [{...event, ...slot}];
      }
    });
  });
  // add calendar events
  props.events?.forEach(event => {
    const key = dj(event.start).format('YYYY-MM-DD');
    if (key in eventsOnDate) {
      eventsOnDate[key].push({ ...event, remote: true });
    } else {
      eventsOnDate[key] = [{ ...event, remote: true }];
    }
  });
  return eventsOnDate;
});
// get all relevant events on a given date (pending, with attendee or remote)
const eventsByDate = (d) => {
  const key = dj(d).format('YYYY-MM-DD');
  if (key in events.value) {
    return props.placeholder
      ? events.value[key].filter(e => dj(e.start).isAfter(dj()))
      : events.value[key].filter(
          e => dj(e.start).add(e.duration, 'minutes').isAfter(dj()) && e.status === appointmentState.pending
            || e.attendee && e.status === appointmentState.pending
            || e.remote
        );
  } else {
    return null;
  }
};
const eventSelected = (d) => {
  emit('eventSelected', d);
};
const dateDisabled = (d) => {
  return props.minDate && dj(d).isBefore(props.minDate, 'day');
};

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

// generate names for each day of week
const weekdayNames = () => {
  const list = props.mini ? dj.weekdaysMin() : dj.weekdaysShort();
  // handle Monday = 1 as first day of week (default is Sunday = 0)
  if (dj.localeData().firstDayOfWeek()) {
    const first = list.shift();
    list.push(first);
  }
  return list;
}

// all day cells in current month view
const days = computed(() => [
  ...previousMonthDays.value,
  ...currentMonthDays.value,
  ...nextMonthDays.value,
]);

// basic data for selected month
const today = computed(() => dj().format("YYYY-MM-DD"));
const date = computed(() => props.selected.format('YYYY-MM-DD'));
const month = computed(() => Number(navDate.value.format("M")));
const year = computed(() => Number(navDate.value.format("YYYY")));
const numberOfDaysInMonth = computed(() => dj(navDate.value).daysInMonth());

const currentMonthDays = computed(() => [...Array(numberOfDaysInMonth.value)].map((_, index) => {
  return {
    date: dj(`${year.value}-${month.value}-${index + 1}`).format("YYYY-MM-DD"),
    active: true,
  };
}));

const previousMonthDays = computed(() => {
  const firstDayOfTheMonthWeekday = dj(currentMonthDays.value[0].date).weekday()+1;
  const previousMonth = dj(`${year.value}-${month.value}-01`).subtract(1, "month");

  // Cover first day of the month being sunday (firstDayOfTheMonthWeekday === 0)
  const visibleNumberOfDaysFromPreviousMonth = firstDayOfTheMonthWeekday
    ? firstDayOfTheMonthWeekday - 1
    : 6;

  const previousMonthLastMondayDayOfMonth = dj(currentMonthDays.value[0].date)
    .subtract(visibleNumberOfDaysFromPreviousMonth, "day")
    .date();

  return [...Array(visibleNumberOfDaysFromPreviousMonth)].map(
    (_, index) => {
      return {
        date: dj(
          `${previousMonth.year()}-${previousMonth.month() + 1}-${
            previousMonthLastMondayDayOfMonth + index
          }`
        ).format("YYYY-MM-DD"),
        active: false,
      };
    }
  );
});

const nextMonthDays = computed(() => {
  const lastDayOfTheMonthWeekday = dj(`${year.value}-${month.value}-${currentMonthDays.value.length}`).weekday()+1;
  const nextMonth = dj(`${year.value}-${month.value}-01`).add(1, "month");

  const visibleNumberOfDaysFromNextMonth = lastDayOfTheMonthWeekday
    ? 7 - lastDayOfTheMonthWeekday
    : lastDayOfTheMonthWeekday;

  return [...Array(visibleNumberOfDaysFromNextMonth)].map((_, index) => {
    return {
      date: dj(
        `${nextMonth.year()}-${nextMonth.month() + 1}-${index + 1}`
      ).format("YYYY-MM-DD"),
      active: false,
    };
  });
});
</script>
