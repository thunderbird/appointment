<template>
  <div class="
    grid w-full grid-cols-week gap-[1px] overflow-hidden rounded-lg border
    border-gray-200 bg-gray-200 dark:border-gray-600 dark:bg-gray-600
  ">
    <!-- header with weekdays -->
    <div class="bg-white dark:bg-gray-700"></div>
    <div
      v-for="d in days"
      :key="d.day"
      class="flex flex-col items-center bg-white py-2 text-gray-500 dark:bg-gray-700 dark:text-gray-300"
    >
      <div
        class="flex-center size-10 text-2xl font-semibold"
        :class="{ 'rounded-full bg-teal-500 text-white': d.active }"
      >
        {{ d.day }}
      </div>
      <div class="text-lg">{{ d.weekday }}</div>
    </div>
    <!-- all day events -->
    <template v-if="!booking">
      <div class="flex-center bg-white text-gray-400 dark:bg-gray-700">
        {{ t('label.allDay') }}
      </div>
      <div
        v-for="d in days"
        :key="d.day"
        class="grid auto-rows-max gap-1 bg-white p-1 dark:bg-gray-700"
        @mouseleave="popup = {...initialEventPopupData}"
      >
        <div
          v-for="event in eventsByDate(d.date)?.allDay"
          :key="event"
          class="flex overflow-hidden"
          @mouseenter="element => popup=showEventPopup(element, event, popupPosition)"
        >
          <div class="w-full truncate rounded bg-amber-400/80 px-2 py-0.5 text-sm">
            {{ event.title }}
          </div>
        </div>
      </div>
    </template>
    <!-- events with times -->
    <div
      class="grid bg-white text-center text-gray-400 dark:bg-gray-700"
      :style="{ gridAutoRows: baseRem + 'rem' }"
    >
      <div v-for="h in hours" :key="h" class="lowercase">
        {{ h }}
      </div>
    </div>
    <div
      v-for="d in days"
      :key="d.day"
      class="grid bg-white dark:bg-gray-700"
      :style="{ gridAutoRows: unitRem + 'rem' }"
      @mouseleave="popup = {...initialEventPopupData}"
    >
      <div
        v-for="event in eventsByDate(d.date)?.duringDay"
        :key="event"
        class="flex overflow-hidden"
        :class="{ 'hidden': event.offset < 0 }"
        :style="{ gridRow: event.offset + ' / span ' + event.span }"
        @mouseenter="element => !booking ? popup=showEventPopup(element, event, popupPosition) : null"
      >
        <div
          v-if="!booking"
          class="m-1 flex w-full truncate rounded border-sky-400 bg-sky-400/10 px-2"
          :class="{
            'border-2': !event.remote || event.tentative,
            'border-dashed': !event.remote,
            'py-0.5': event.span >= 30,
          }"
          :style="{
            color: event.tentative ? event.calendar_color : null,
            borderColor: eventColor(event, false).border,
            backgroundColor: (!event.remote || event.tentative)
              ? eventColor(event, false).background
              : event.calendar_color,
          }"
        >
          <div
            class="truncate"
            :class="{
              'grow self-center text-sm': event.span < 60,
              'hidden': event.span < 30,
            }"
          >
            {{ event.title }}
          </div>
        </div>
        <div
          v-else
          @click="bookSlot(event.start)"
          class="
            m-1 flex w-full cursor-pointer overflow-hidden rounded-md bg-teal-50 p-1 text-sm
            text-gray-600 hover:bg-teal-100 hover:shadow dark:bg-teal-800 dark:text-gray-300 hover:dark:bg-teal-700
          "
          :class="{ 'bg-gradient-to-b from-teal-500 to-sky-600 shadow-lg': event.selected }"
        >
          <div
            class="w-full truncate rounded border-2 border-dashed border-teal-500 p-1 font-semibold lowercase"
            :class="{ 'border-white text-white': event.selected }"
          >
            <span :class="{ 'hidden': event.span <= 30 }">
              {{ event.times }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <event-popup
      v-if="(events && !booking)"
      :style="{
        display: popup.display,
        top: popup.top,
        left: popup.left,
        right: popup.right,
      }"
      :event="popup.event"
      :position="popupPosition"
    />
  </div>
</template>

<script setup>
import { computed, inject, ref } from 'vue';
import {
  eventColor, timeFormat, initialEventPopupData, showEventPopup,
} from '@/utils';
import { useI18n } from 'vue-i18n';
import EventPopup from '@/elements/EventPopup';

const { t } = useI18n();
const dj = inject('dayjs');

// component properties
const props = defineProps({
  selected: Object, // currently active date
  booking: Boolean, // flag indicating if calendar is used to book time slots
  appointments: Array, // data of appointments to show
  events: Array, // data of calendar events to show
  popupPosition: String, // currently supported: right, left, top
});

// component emits
const emit = defineEmits(['eventSelected']);

// base data for display elements
const baseRem = 4; // height for one hour element in rem
const unitRem = baseRem / 60; // height for shortest event (1 minute) in rem

// all elements (appointment slots or remote events) to show in the current view
const elementsToShow = computed(() => {
  const slots = props.appointments.reduce((p, c) => [...p, ...c.slots], []);
  return props.booking ? slots : [...slots, ...props.events];
});

// compute start limit depending on data in view
// begin showing events 2 hours before first event or at least 2pm
const startHour = computed(() => {
  const start = elementsToShow.value.filter((e) => !e.all_day).reduce(
    (p, c) => (dj(c.start).isBetween(props.selected.startOf('week'), props.selected.endOf('week'))
      ? Math.min(dj(c.start).format('H'), p)
      : p),
    16,
  );
  return start - 2 >= 0 ? start - 2 : 0;
});

// compute start limit depending on data in view
// end showing events 2 hours after first event or at max 10am
const endHour = computed(() => {
  const end = elementsToShow.value.reduce((p, c) => {
    const slotEnd = dj(c.start).add(c.duration, 'minutes');
    return slotEnd.isBetween(props.selected.startOf('week'), props.selected.endOf('week'))
      ? Math.max(slotEnd.format('H'), p)
      : p;
  }, 9);
  if (startHour.value > end) {
    return startHour.value + 8;
  }
  return end + 1 < 24 ? end + 1 : 24;
});

// create position of event, smallest unit is one minute
const timePosition = (start, duration) => ({
  offset: 60 * dj(start).format('H') + 1 * dj(start).format('m') - 60 * startHour.value + 1,
  span: duration,
  times: `${dj(start).format(timeFormat())} - ${dj(start).add(duration, 'minutes').format(timeFormat())}`,
});

// handle events to show
const events = computed(() => {
  const eventsOnDate = {};
  // add appointments
  props.appointments?.forEach((event) => {
    event.slots.forEach((slot) => {
      const key = dj(slot.start).format('YYYY-MM-DD');
      const extendedEvent = { ...event, ...slot, ...timePosition(slot.start, slot.duration) };
      delete extendedEvent.slots;
      if (key in eventsOnDate) {
        eventsOnDate[key].push(extendedEvent);
      } else {
        eventsOnDate[key] = [extendedEvent];
      }
    });
  });
  // add calendar events
  props.events?.forEach((event) => {
    const key = dj(event.start).format('YYYY-MM-DD');
    const extendedEvent = { ...event, ...timePosition(event.start, event.duration), remote: true };
    if (key in eventsOnDate) {
      eventsOnDate[key].push(extendedEvent);
    } else {
      eventsOnDate[key] = [extendedEvent];
    }
  });
  return eventsOnDate;
});
const eventsByDate = (d) => {
  const key = dj(d).format('YYYY-MM-DD');
  if (key in events.value) {
    return {
      duringDay: events.value[key].filter((e) => !e.all_day),
      allDay: events.value[key].filter((e) => e.all_day),
    };
  }
  return null;
};

// generate names for each day of week
const days = computed(() => {
  const list = [];
  let day = props.selected.startOf('week');
  for (let i = 0; i < 7; i += 1) {
    list.push({
      date: day.format('YYYY-MM-DD'),
      day: day.format('D'),
      weekday: day.format('ddd'),
      active: day.isSame(dj(), 'day'),
    });
    day = day.add(1, 'day');
  }
  return list;
});

// generate hours
const hours = computed(() => {
  const list = [];
  const range = endHour.value - startHour.value;
  let d = dj().hour(startHour.value).minute(0);
  for (let i = 0; i <= range; i += 1) {
    list.push(d.format(timeFormat()));
    d = d.add(1, 'hour');
  }
  return list;
});

// user selects a slot for booking
const bookSlot = (d) => {
  emit('eventSelected', d);
};

// event details
const popup = ref({ ...initialEventPopupData });

</script>
