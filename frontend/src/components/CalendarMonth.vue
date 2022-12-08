<template>
  <div class="select-none">
    <div v-if="nav" class="flex justify-center items-center gap-2 mb-2 select-none">
      <div @click="dateNav(false)" class="group cursor-pointer">
        <icon-chevron-left class="h-6 w-6 stroke-slate-400 group-hover:stroke-teal-500 stroke-2 fill-transparent" />
      </div>
      <div class="text-teal-500 font-semibold text-lg">
        {{ navDate.format('MMMM YYYY')}}
      </div>
      <div @click="dateNav(true)" class="group cursor-pointer">
        <icon-chevron-right class="h-6 w-6 stroke-slate-400 group-hover:stroke-teal-500 stroke-2 fill-transparent" />
      </div>
    </div>
    <div class="grid grid-cols-7 gap-[1px] w-full bg-gray-200 border rounded-lg overflow-hidden">
      <div
        v-for="h in weekdayNames()"
        :key="h"
        class="text-center text-gray-500 bg-gray-100 py-2"
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
        @click="!placeholder ? emit('daySelected', d.date) : null"
        @event-selected="eventSelected"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, watch } from "vue";
import CalendarMonthDay from '@/elements/CalendarMonthDay.vue';
import IconChevronRight from "@/elements/icons/IconChevronRight.vue";
import IconChevronLeft from "../elements/icons/IconChevronLeft.vue";
const dj = inject("dayjs");

// component properties
const props = defineProps({
  selected: Object,     // currently active date
  mini: Boolean,        // show small version of monthly calendar
  nav: Boolean,         // show month navigation
  placeholder: Boolean, // format events as placeholder
  events: Array,        // data of events to show
});

// component emits
const emit = defineEmits(['daySelected', 'eventSelected']);

// handle events to show
const events = computed(() => {
  const eventsOnDate = {};
  props.events?.forEach(event => {
    event.slots.forEach(slot => {
      const key = dj(slot.start).format('YYYY-MM-DD');
      if (key in eventsOnDate) {
        eventsOnDate[key].push({...event, ...slot});
      } else {
        eventsOnDate[key] = [{...event, ...slot}];
      }
    });
  });
  return eventsOnDate;
});
const eventsByDate = (d) => {
  const key = dj(d).format('YYYY-MM-DD');
  if (key in events.value) {
    return events.value[key];
  } else {
    return null;
  }
};
const eventSelected = (d) => {
  emit('eventSelected', d);
};

// handle nav date (only used if navigation is active)
const navDate = ref(dj(props.selected)); // current selected date for independent navigation
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
const date = computed(() => dj(props.selected).format('YYYY-MM-DD'));
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
