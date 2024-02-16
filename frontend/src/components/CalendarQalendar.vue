<script setup>
import {
  ref, computed, inject, toRefs,
} from 'vue';
import { Qalendar } from 'qalendar';
import 'qalendar/dist/style.css';
import CalendarEvent from '@/elements/CalendarEvent.vue';
import { appointmentState } from '@/definitions';
import { timeFormat } from '@/utils';

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
  display12Hour: 'hh:mma',
  display24Hour: 'HH:mm',
};
const displayFormat = timeFormat();
const calendarColors = ref({});
const selectedDate = ref(null);
const calendarMode = ref('month');

// component emits
const emit = defineEmits(['daySelected', 'eventSelected', 'dateChange']);

const timeSlotDuration = computed(() => {
  if (appointments?.value?.length === 0) {
    return 15;
  }
  const duration = appointments?.value[0].slots[0].duration;
  if (duration <= 15) {
    return 15;
  } if (duration <= 30) {
    return 30;
  }
  return 60;
});
const timeSlotHeight = ref(40);

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
    length: timeSlotDuration.value, // Length in minutes of each interval. Accepts values 15, 30 and 60 (the latter is the default)
    height: timeSlotHeight.value, // The height of each interval
    // displayClickableInterval: true, // Needs to be set explicitly to true, if you want to display clickable intervals
  },
  dayBoundaries: {
    start: 6,
    end: 18,
  },
  eventDialog: {
    // isCustom: true,
    isDisabled: true, //! isBookingRoute.value,
  },
});

/* Event Handlers */
const eventSelected = (evt) => {
  if (!isBookingRoute.value) {
    return;
  }
  selectedDate.value = evt.clickedEvent.id;
  emit('eventSelected', evt.clickedEvent.id);
};
const dateChange = (evt) => {
  emit('dateChange', evt);
};
const modeChange = (evt) => {
  calendarMode.value = evt?.mode ?? 'month';
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
  console.log('Events -> ', events?.value, appointments?.value);
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
    customData: {
      attendee: null,
      booking_status: appointmentState.booked,
      calendar_title: event.calendar_title,
      calendar_color: event.calendar_color,
      duration: event.duration,
      preview: false,
      all_day: event.all_day,
      remote: true,
      tentative: event.tentative,
    },
    isCustom: true,
  })) ?? [];

  // Mix in appointments
  const evtApmts = appointments?.value?.map((appointment) => appointment.slots.map((slot) => ({
    id: appointment.id ?? applyTimezone(slot.start).format(dateFormatStrings.qalendar),
    title: !isBookingRoute.value
      ? appointment.title
      : `${applyTimezone(slot.start).format(displayFormat)} - ${applyTimezone(slot.start).add(slot.duration, 'minutes').format(displayFormat)}`,
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
      attendee: null,
      booking_status: appointment.status,
      calendar_title: appointment.calendar_title,
      calendar_color: appointment.calendar_color,
      duration: slot.duration,
      preview: false,
      all_day: false,
      remote: false,
      tentative: false,
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
      @updated-mode="modeChange"
    >
      <template #weekDayEvent="eventProps">
        <CalendarEvent
          :isActive="true"
          :isSelected="selectedDate === eventProps.eventData.id"
          :isToday="false"
          :showDetails="!isBookingRoute"
          :disabled="false"
          :placeholder="isBookingRoute"
          :event="eventProps.eventData"
          :popup-position="calendarMode === 'day' ? 'top' : 'right'"
          :month-view="false"
        ></CalendarEvent>
      </template>

      <template #monthEvent="monthEventProps">
        <CalendarEvent
          :isActive="true"
          :isSelected="selectedDate === monthEventProps.eventData.id"
          :isToday="false"
          :showDetails="!isBookingRoute"
          :disabled="false"
          :placeholder="isBookingRoute"
          :event="monthEventProps.eventData"
          :month-view="true"
        ></CalendarEvent>
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
  @media (min-width: theme('screens.sm')) {
    min-height: theme('height.16') !important;
  }
  @media (min-width: theme('screens.md')) {
    min-height: theme('height.32') !important;
  }
}

/* Adjust the background of the entire component */
.calendar-root-wrapper .calendar-root {
  background-color: var(--qalendar-appointment-bg) !important;
  border-radius: var(--qalendar-appointment-border-radius) !important;
  border-color: var(--qalendar-appointment-border-color) !important;
}

/* Fix overflow:hidden preventing event details popup from clipping calendar */
.calendar-root-wrapper .calendar-week__event,
.calendar-root-wrapper .calendar-week__events,
.calendar-root-wrapper .calendar-week__wrapper,
.calendar-root-wrapper .calendar-month {
  overflow: visible !important;
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
