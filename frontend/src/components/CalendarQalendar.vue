<script setup>
import {
  ref, computed, inject, toRefs,
} from 'vue';
import { Qalendar } from 'qalendar';
import 'qalendar/dist/style.css';
import CalendarMonthDay from '@/elements/CalendarMonthDay.vue';
import QalendarMonthDay from '@/elements/QalendarMonthDay.vue';

// component constants
const dj = inject('dayjs');

// component properties
const props = defineProps({
  selected: Object, // currently active date (dayjs object)
  mini: Boolean, // show small version of monthly calendar
  nav: Boolean, // show month navigation
  placeholder: Boolean, // format appointments as placeholder
  minDate: Object, // minimum active date in view (dayjs object)
  appointments: Array, // data of appointments to show
  events: Array, // data of calendar events to show
  schedules: Array, // data of scheduled event previews to show
  popupPosition: String, // currently supported: right, left, top
  isBookingRoute: Boolean,
});

const { events, appointments, isBookingRoute } = toRefs(props);

const dateFormatStrings = {
  qalendar: 'YYYY-MM-DD HH:mm',
  qalendarFullDay: 'YYYY-MM-DD',
  // Display formats
  display12Hour: 'hh:mm',
  display24Hour: 'HH:mm',
};
const detectedTimeFormat = Number(dj('2022-05-24 20:00:00').format('LT').split(':')[0]) > 12 ? 24 : 12;
const timeFormat = ref(Number(localStorage?.getItem('timeFormat')) ?? detectedTimeFormat);
const displayFormat = ref(timeFormat.value === 12 ? dateFormatStrings.display12Hour : dateFormatStrings.display24Hour);
const calendarColors = ref({});
const selectedDate = ref(null);

// component emits
const emit = defineEmits(['daySelected', 'eventSelected', 'dateChange']);

const config = ref({
  week: {
    startsOn: 'sunday',
  },
  style: {
    // When adding a custom font, please also set the fallback(s) yourself
    fontFamily: 'Open Sans", ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji',
    colorSchemes: calendarColors,
  },
  defaultMode: 'month',
  dayIntervals: {
    length: 15, // Length in minutes of each interval. Accepts values 15, 30 and 60 (the latter is the default)
    height: 40, // The height of each interval
    // displayClickableInterval: true, // Needs to be set explicitly to true, if you want to display clickable intervals
  },
  dayBoundaries: {
    start: 6,
    end: 18,
  },
  eventDialog: {
    isCustom: true,
    isDisabled: !isBookingRoute.value,
  },
});

/* Event Handlers */
const eventSelected = (evt) => {
  console.log('Selected', evt.clickedEvent.id);
  selectedDate.value = evt.clickedEvent.id;
  emit('eventSelected', evt.clickedEvent.id);
};
const dateChange = (evt) => {
  emit('dateChange', evt);
};

/* Functions */

/**
 * Processes a calendar colour for a specific event.
 * If that calendar hasn't been used before it's added to our colourScheme map for Qalendar
 * @param calendarTitle {string}
 * @param calendarColor {string}
 * @returns {string} id for the colorScheme property
 */
const processCalendarColorScheme = (calendarTitle, calendarColor) => {
  // TODO: Replace the replace pattern with some regex
  const slug = calendarTitle.replace(' ', '_').replace('@', '_').toLowerCase();
  if (!calendarColors.value[slug]) {
    calendarColors.value[slug] = {
      color: '#fff',
      backgroundColor: calendarColor,
    };
  }

  return slug;
};

/**
 * Converts time to utc and applies the best guessed timezone
 * @param d - DayJS date object
 * @returns {*}
 */
const applyTimezone = (d) => dj.utc(d).tz(dj.tz.guess());

/**
 * Generates a list of Qalendar friendly event objects from events and appointments props.
 * @type {ComputedRef<*[]>}
 */
const calendarEvents = computed(() => {
  const evts = events?.value?.map((event) => ({
    id: event.title,
    title: event.title,
    colorScheme: processCalendarColorScheme(event.calendar_title, event.calendar_color),
    time: {
      start: event.all_day
        ? dj(event.start).format(dateFormatStrings.qalendarFullDay)
        : dj(event.start).format(dateFormatStrings.qalendar),
      end: event.all_day
        ? dj(event.end).format(dateFormatStrings.qalendarFullDay)
        : dj(event.end).format(dateFormatStrings.qalendar),
    },
    description: event.description,
  })) ?? [];

  console.log(appointments.value);
  // Mix in appointments
  const evtApmts = appointments?.value?.map((appointment) => appointment.slots.map((slot) => ({
    id: appointment.id ?? applyTimezone(slot.start).format(dateFormatStrings.qalendar),
    title: isBookingRoute.value
      ? appointment.title
      : `${applyTimezone(slot.start).format(displayFormat.value)} - ${applyTimezone(slot.start).add(slot.duration, 'minutes').format(displayFormat.value)}`,
    colorScheme: processCalendarColorScheme(
      appointment?.calendar_title ?? 'booking',
      appointment?.calendar_color ?? 'rgb(45, 212, 191)',
    ),
    time: {
      start: applyTimezone(slot.start).format(dateFormatStrings.qalendar),
      end: applyTimezone(slot.start).add(slot.duration, 'minutes').format(dateFormatStrings.qalendar),
    },
    description: appointment.details,
    with: slot.attendee ? [slot.attendee].map((attendee) => `${attendee.name} <${attendee.email}>`).join(', ') : '',
    customData: {
      booking_status: slot?.booking_status ?? 1,
      calendar_title: 'booking',
      calendar_color: 'rgb(45, 212, 191)',
      duration: slot.duration,
      preview: false,
      all_day: false,
      remote: false,
    },
    isCustom: true,
  }))).flat(1) ?? [];

  return [...evts, ...evtApmts];
});
</script>
<template>
  <div class="w-full">
    <Qalendar
      :events="calendarEvents"
      :config="config"
      @event-was-clicked="eventSelected"
      @updated-period="dateChange"
    >
      <template #eventDialog="props">
      <div v-if="(props.eventDialogData && props.eventDialogData.title)">
        <div :style="{marginBottom: '8px'}">Edit event</div>

        <input class="flyout-input" type="text" :style="{ width: '90%', padding: '8px', marginBottom: '8px' }" >

        <button class="close-flyout" @click="props.closeEventDialog">
          Finished!
        </button>
      </div>
    </template>

      <template #weekDayEvent="eventProps">
        <QalendarMonthDay
          :isActive="true"
          :isSelected="selectedDate === eventProps.eventData.id"
          :isToday="false"
          :showDetails="false"
          :disabled="false"
          :placeholder="true"
          :event="eventProps.eventData"
        ></QalendarMonthDay>
      </template>

      <template #monthEvent="monthEventProps">
        <QalendarMonthDay
          :isActive="true"
          :isSelected="selectedDate === monthEventProps.eventData.id"
          :isToday="false"
          :showDetails="false"
          :disabled="false"
          :placeholder="true"
          :event="monthEventProps.eventData"
        ></QalendarMonthDay>
      </template>
    </Qalendar>
  </div>
</template>
<style>
/*
 * Re-theme of Qalendar for Appointment
 */
:root {
  --qalendar-appointment-bg: theme('backgroundColor.gray.300');
  --qalendar-appointment-fg: theme('backgroundColor.gray.100');
  --qalendar-appointment-border-color: theme('borderColor.gray.200');
  --qalendar-appointment-border-radius: theme('borderRadius.xl');
}

@media (prefers-color-scheme: dark) {
  :root {
    --qalendar-appointment-bg: theme('backgroundColor.gray.700');
    --qalendar-appointment-fg: theme('backgroundColor.gray.600');
    --qalendar-appointment-border-color: theme('borderColor.gray.500');
  }
}

/* Override some of Qalendar's css variables */
.calendar-root-wrapper * {
  /** Font overrides */
  --qalendar-font-3xs: theme('fontSize.xs') !important;
  --qalendar-font-2xs: theme('fontSize.sm') !important;
  --qalendar-font-xs: theme('fontSize.base') !important;
  --qalendar-font-s: theme('fontSize.lg') !important;
  --qalendar-font-m: theme('fontSize.xl') !important;
  --qalendar-font-l: theme('fontSize.2xl') !important;
  --qalendar-font-xl: theme('fontSize.3xl') !important;
  /* Sizing overrides */
  --qalendar-border-gray-thin: theme('borderWidth.DEFAULT') solid var(--qalendar-appointment-border-color) !important;
  --qalendar-border-radius: var(--qalendar-appointment-border-radius) !important;
  /* Colours */
  --qalendar-blue: theme('colors.teal.500') !important;
  --qalendar-blue-transparent: theme('colors.teal.500') / 90% !important;
  --qalendar-gray-quite-dark: theme('colors.gray.300') !important;
  --qalendar-gray: var(--qalendar-appointment-fg) !important;
  --qalendar-green: var(--qalendar-blue) !important;
  --qalendar-theme-color: var(--qalendar-blue) !important;
  --qalendar-light-gray: theme('colors.gray.600') !important;
  --qalendar-dark-mode-line-color: var(--qalendar-appointment-border-color);
}

/* Ensure month days are at minimum 8rem */
.calendar-root-wrapper .calendar-month__weekday {
  min-height: theme('height.32') !important;
}

/* Adjust the background of the entire component */
.calendar-root-wrapper .calendar-root {
  background-color: var(--qalendar-appointment-bg) !important;
  border-radius: var(--qalendar-appointment-border-radius) !important;
  border-color: var(--qalendar-appointment-border-color) !important;
}

/* Make the header are our cool foreground colour */
.calendar-root-wrapper .calendar-header,
.calendar-root-wrapper .calendar-month__week-day-names,
.calendar-root-wrapper .week-timeline {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  background-color: var(--qalendar-appointment-fg) !important;
}

/* Make trailing days (days not in this month) our cool foreground colour */
.calendar-root-wrapper .trailing-or-leading {
  background-color: var(--qalendar-appointment-fg);
}

</style>
