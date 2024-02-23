<script setup>
import {
  ref, computed, inject, toRefs, watch,
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
  mini: Boolean, // show small version of monthly calendar
  placeholder: Boolean, // format appointments as placeholder
  minDate: Object, // minimum active date in view (dayjs object)
  appointments: Array, // data of appointments to show
  events: Array, // data of calendar events to show
  schedules: Array, // data of scheduled event previews to show
  isBookingRoute: Boolean,
  currentDate: Object,
});

const {
  events, appointments, schedules, isBookingRoute, currentDate,
} = toRefs(props);

const qalendarRef = ref();

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

/**
 * Calculate the minimum amount of time we want to display
 * Qalendar only supports [15, 30, 60] as values.
 * @type {ComputedRef<number>}
 */
const timeSlotDuration = computed(() => {
  if (appointments?.value?.length === 0) {
    return 15;
  }
  // Duration on slots are fixed, so grab the first one.
  const duration = appointments?.value[0].slots[0].duration;
  if (duration <= 15) {
    return 15;
  }
  if (duration <= 30) {
    return 30;
  }
  return 60;
});
const timeSlotHeight = ref(40);

/* Event Handlers */

/**
 * On event click / selected. Only emits on booking route
 * @param evt
 */
const eventSelected = (evt) => {
  if (!isBookingRoute.value) {
    return;
  }
  selectedDate.value = evt.clickedEvent.id;
  emit('eventSelected', evt.clickedEvent.id);
};
/**
 * On Date Change. Any internal date change triggers this.
 * @param evt
 */
const dateChange = (evt) => {
  emit('dateChange', evt);
};
/**
 * On mode change. e.g. month, week, day.
 */
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
  const slug = calendarTitle.replace(/[^a-zA-Z0-9]/g,'_').toLowerCase();
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
  const evts = events?.value?.map((event) => {
    const start = dj(event.start);
    const end = dj(event.end);

    return {
      id: event.title,
      title: event.title,
      colorScheme: processCalendarColorScheme(event.calendar_title, event.calendar_color),
      time: {
        start: event.all_day
          ? start.format(dateFormatStrings.qalendarFullDay)
          : start.format(dateFormatStrings.qalendar),
        end: event.all_day
          ? end.format(dateFormatStrings.qalendarFullDay)
          : end.format(dateFormatStrings.qalendar),
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
    };
  }) ?? [];

  // Merge appointment and schedule preview data, they're the same { appointment: { ...slots: [...] } } data structure.
  const appointmentsAndSchedules = [...appointments?.value ?? [], ...schedules?.value ?? []];

  // Mix in appointments
  const evtApmts = appointmentsAndSchedules?.map((appointment) => appointment.slots.map((slot) => {
    const start = applyTimezone(dj(slot.start));
    const end = start.add(slot.duration, 'minutes');

    return {
      id: appointment.id ?? start.format(dateFormatStrings.qalendar),
      title: !isBookingRoute.value
        ? appointment.title
        : `${start.format(displayFormat)} - ${end.format(displayFormat)}`,
      colorScheme: processCalendarColorScheme(
        appointment?.calendar_title ?? 'booking',
        appointment?.calendar_color ?? 'rgb(20, 184, 166)',
      ),
      time: {
        start: start.format(dateFormatStrings.qalendar),
        end: end.format(dateFormatStrings.qalendar),
      },
      description: appointment.details,
      with: slot.attendee ? [slot.attendee].map((attendee) => `${attendee.name} <${attendee.email}>`).join(', ') : '',
      customData: {
        attendee: null,
        booking_status: appointment.status,
        calendar_title: appointment.calendar_title,
        calendar_color: appointment?.calendar_color ?? 'rgb(20, 184, 166)',
        duration: slot.duration,
        preview: appointment?.type === 'schedule',
        all_day: false,
        remote: false,
        tentative: false,
      },
      isCustom: true,
    };
  })).flat(1) ?? [];

  return [...evts, ...evtApmts];
});

/**
 * Calculate the start and end times, and then space them our by 2 hours for style!
 * @type {ComputedRef<{start, end}>}
 */
const dayBoundary = computed(() => {
  let startHour = 99;
  let endHour = 0;

  if (calendarEvents?.value.length === 0) {
    return {
      start: 0,
      end: 24,
    };
  }

  calendarEvents.value.forEach((event) => {
    // Calculate start/end hours
    startHour = Math.min(startHour, dj(event.time.start).hour());
    endHour = Math.max(endHour, dj(event.time.end).hour());
  });

  return {
    start: Math.max(0, startHour - 2),
    end: Math.min(24, endHour + 2),
  };
});

/**
 * Calendar Config Object
 */
const config = ref({
  week: {
    startsOn: 'sunday',
  },
  style: {
    // Just the pre-calculated list from tailwind, could use some fine-tuning.
    fontFamily: [
      '"Open Sans"',
      'ui-sans-serif',
      'system-ui',
      'sans-serif',
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
      '"Noto Color Emoji"',
    ].join(', '),
    colorSchemes: calendarColors,
  },
  defaultMode: calendarMode.value, // mode happens to match up with our mode!
  dayIntervals: {
    length: timeSlotDuration.value, // Accepts [15, 30, 60]
    height: timeSlotHeight.value, // pixel height of each length
  },
  dayBoundaries: dayBoundary,
  eventDialog: {
    // We roll our own
    isDisabled: true,
  },
});

/**
 * Qalendar's selectedDate is only set on init and never updated. So we have to poke at their internals...
 */
watch(currentDate, () => {
  const period = {
    start: currentDate.value.startOf('month').toDate(),
    end: currentDate.value.endOf('month').toDate(),
    selectedDate: currentDate.value.toDate(),
  };

  qalendarRef.value.handleUpdatedPeriod(period);
  qalendarRef.value.$refs.appHeader.handlePeriodChange(period);
});

</script>
<template>
  <div class="w-full">
    <Qalendar
      :events="calendarEvents"
      :config="config"
      :selected-date="currentDate?.toDate()"
      @event-was-clicked="eventSelected"
      @updated-period="dateChange"
      @updated-mode="modeChange"
      ref="qalendarRef"
    >
      <template #weekDayEvent="eventProps">
        <calendar-event
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
  --qalendar-appointment-bg: theme('backgroundColor.white');
  --qalendar-appointment-fg: theme('backgroundColor.gray.100');
  --qalendar-appointment-border-color: theme('borderColor.gray.200');
  --qalendar-appointment-border-radius: theme('borderRadius.xl');
  --qalendar-appointment-text: theme('colors.gray.600');

  --qalendar-appointment-button-color: linear-gradient(to bottom right, theme('gradientColorStops.teal.400'), theme('gradientColorStops.sky.400'));
  --qalendar-appointment-button-hover-color: linear-gradient(to top left, theme('gradientColorStops.teal.400'), theme('gradientColorStops.sky.400'));
  --qalendar-appointment-button-hover-scale: theme('scale.102');
}

@media (prefers-color-scheme: dark) {
  :root {
    --qalendar-appointment-bg: theme('backgroundColor.gray.700');
    --qalendar-appointment-fg: theme('backgroundColor.gray.600');
    --qalendar-appointment-border-color: theme('borderColor.gray.500');
    --qalendar-appointment-text: theme('colors.gray.300');
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
  /* Colour overrides */
  --qalendar-blue: theme('colors.teal.500') !important;
  --qalendar-blue-transparent: theme('colors.teal.500') / 90% !important;
  --qalendar-gray-quite-dark: var(--qalendar-appointment-text) !important;
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

/* Add some minimum spacing to the numbered day, so events line up even with the "today" highlight. */
.calendar-root-wrapper .calendar-month__day-date {
  @media (min-width: theme('screens.lg')) {
    min-height: theme('height.8') !important;
  }
}

/* Add some spacing to the event list */
.calendar-root-wrapper .mode-is-month .is-event {
  margin-bottom: theme('margin.2');
}

/* Ignore text blocking pointer events for mobile day selection on month view */
.calendar-root-wrapper .calendar-month__day-date {
  pointer-events: none;
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

/* Unset calendar mode background and border radius to normalize it. */
.calendar-root-wrapper .calendar-header__mode-picker .calendar-header__mode-value {
  background-color: unset !important;
  border-radius: unset !important;
  display: flex;
  justify-content: center;
  color: white;
}

/* Follow-up fix for mode dropdown text colour */
.calendar-root-wrapper .calendar-header__mode-picker {
  color: var(--qalendar-appointment-text) !important;
}

/* Create some space between week day names */
.calendar-root-wrapper .date-picker__day-names.week {
  gap: theme('gap.2');
}

/* Apply our primary-btn style to the two buttons.
This was a fancy layer class, but @apply in sfc with custom layer classes is a nightmare. */
.calendar-root-wrapper .date-picker__value-display,
.calendar-root-wrapper .calendar-header__mode-picker {
  @apply relative h-10 text-base font-semibold whitespace-nowrap rounded-full bg-gradient-to-br
  md:px-2 transition-all ease-in-out flex items-center justify-center gap-2
  text-white from-teal-400 to-sky-600 md:min-w-32;
}

/* @apply doesn't seem to mesh well with states */
.calendar-root-wrapper .date-picker__value-display:hover,
.calendar-root-wrapper .calendar-header__mode-picker:hover {
  @apply from-sky-400 to-teal-600 shadow-md
}

/* ditto */
.calendar-root-wrapper .date-picker__value-display:disabled,
.calendar-root-wrapper .calendar-header__mode-picker:disabled {
  @apply opacity-50 shadow-none
}

/*
Loading bar, mostly works but needs some work and maybe a div relocation
.calendar-root-wrapper .calendar-root .top-bar-loader {
  z-index: 2;
  width: 100%;
  left: 0;
  top: 4.5rem;
  border-radius: var(--qalendar-appointment-border-radius) !important;

  @media (min-width: theme('screens.md')) {
    top: 4.5rem;
  }
  @media (min-width: theme('screens.lg')) {
    top: 5.5rem;
  }
}
*/
</style>
