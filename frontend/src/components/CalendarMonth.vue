<template>
  <div>
    <div v-if="nav" class="flex justify-center items-center gap-2 mb-2">
      <div @click="emit('prev')" class="cursor-pointer">
        <img class="h-6" src="@/assets/icon-nav-left.svg" alt="Go to previous month">
      </div>
      <div class="text-teal-500 font-semibold">
        {{ selected.format('MMMM YYYY')}}
      </div>
      <div @click="emit('next')" class="cursor-pointer">
        <img class="h-6" src="@/assets/icon-nav-right.svg" alt="Go to next month">
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
        :day="dj(d.date).format('D')"
        :is-active="d.active"
        :is-today="d.date === today"
        :mini="mini"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from "vue";
import CalendarMonthDay from '@/elements/CalendarMonthDay.vue';
const dj = inject("dayjs");

// component properties
const props = defineProps({
  selected: Object, // currently active date
  mini: Boolean,    // show small version of monthly calendar
  nav: Boolean      // show month navigation
});

// component emits
const emit = defineEmits(['prev', 'next']);

// generate names for each day of week
const weekdayNames = () => {
  const names = [];
  const init = dj('2022-10-10');
  for (let i = 0; i < 7; i++) {
    names.push(init.add(i, 'd').format(props.mini ? 'dd' : 'ddd'));
  }
  return names;
}

// all day cells in current month view
const days = computed(() => [
  ...previousMonthDays.value,
  ...currentMonthDays.value,
  ...nextMonthDays.value,
]);

// basic data for selected month
const today = computed(() => dj().format("YYYY-MM-DD"));
const month = computed(() => Number(props.selected.format("M")));
const year = computed(() => Number(props.selected.format("YYYY")));
const numberOfDaysInMonth = computed(() => dj(props.selected).daysInMonth());

const currentMonthDays = computed(() => [...Array(numberOfDaysInMonth.value)].map((_, index) => {
  return {
    date: dj(`${year.value}-${month.value}-${index + 1}`).format("YYYY-MM-DD"),
    active: true,
  };
}));

const previousMonthDays = computed(() => {
  const firstDayOfTheMonthWeekday = dj(currentMonthDays.value[0].date).weekday();
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
  const lastDayOfTheMonthWeekday = dj(`${year.value}-${month.value}-${currentMonthDays.value.length}`).weekday();
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
