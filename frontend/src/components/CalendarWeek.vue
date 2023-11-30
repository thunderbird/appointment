<template>
  <div class="
    grid grid-cols-week gap-[1px] w-full border rounded-lg overflow-hidden
    bg-gray-200 border-gray-200 dark:bg-gray-600 dark:border-gray-600
  ">
    <!-- header with weekdays -->
    <div class="bg-white dark:bg-gray-700"></div>
    <div
      v-for="d in days"
      :key="d.day"
      class="flex flex-col items-center py-2 text-gray-500 dark:text-gray-300 bg-white dark:bg-gray-700"
    >
      <div
        class="text-2xl font-semibold w-10 h-10 flex-center"
        :class="{ 'rounded-full text-white bg-teal-500': d.active }"
      >
        {{ d.day }}
      </div>
      <div class="text-lg">{{ d.weekday }}</div>
    </div>
    <!-- all day events -->
    <template v-if="!booking">
      <div class="flex-center text-gray-400 bg-white dark:bg-gray-700">
        {{ t('label.allDay') }}
      </div>
      <div
        v-for="d in days"
        :key="d.day"
        class="grid auto-rows-max gap-1 p-1 bg-white dark:bg-gray-700"
        @mouseleave="popup = {...initialEventPopupData}"
      >
        <div
          v-for="eventDate in (d.date in allDayEvents ? allDayEvents[d.date] : {})"
          :key="eventDate"
          class="flex overflow-hidden"
        >
          <div
            v-for="event in eventDate.items"
            :key="event"
            class="flex overflow-hidden w-full"
            @mouseenter="element => popup=showEventPopup(element, event, popupPosition)"
          >
            <div class="w-full text-sm truncate rounded px-2 py-0.5 bg-amber-400/80">
              {{ event.title }}
            </div>
          </div>
        </div>
      </div>
    </template>
    <!-- events with times -->
    <div
      class="text-center grid text-gray-400 bg-white dark:bg-gray-700"
      :style="{ gridAutoRows: baseRem + 'rem' }"
    >
      <div v-for="h in hours" :key="h" class="lowercase">
        {{ h }}
      </div>
    </div>
    <div
      v-for="d in days"
      :key="d.day"
      class="grid bg-white dark:bg-gray-700 relative"
      @mouseleave="popup = {...initialEventPopupData}"
    >
      <div
        v-for="eventTimeStart in (d.date in events ? events[d.date] : {})"
        :key="eventTimeStart"
        class="absolute flex overflow-hidden w-full"
        :style="{top: eventTimeStart.offset + 'px', zIndex: eventTimeStart.order }"
      >
      <div
        v-for="event in eventTimeStart.items"
        :key="event"
        class="grid w-full"
      >
        <div
          class="flex overflow-hidden"
          :class="{ 'hidden': event.offset < 0 }"
          :style="{ height: (event.span*unitRem) + 'rem' }"
          @mouseenter="element => !booking ? popup=showEventPopup(element, event, popupPosition) : null"
        >
          <div
            v-if="!booking"
            class="w-full truncate rounded flex m-1 px-2 bg-sky-400/10 border-sky-400"
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
              : event.calendar_color + 'cc',
          }"
          >
            <div
              class="truncate opacity-100 w-full"
              :class="{
              'self-center grow text-sm': event.span < 60,
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
            w-full text-sm overflow-hidden rounded-md p-1 m-1 cursor-pointer hover:shadow flex
            text-gray-600 dark:text-gray-300 bg-teal-50 hover:bg-teal-100 dark:bg-teal-800 hover:dark:bg-teal-700
          "
            :class="{ 'shadow-lg bg-gradient-to-b from-teal-500 to-sky-600': event.selected }"
          >
            <div
              class="w-full truncate rounded lowercase p-1 font-semibold border-2 border-dashed border-teal-500"
              :class="{ 'text-white border-white': event.selected }"
            >
            <span :class="{ 'hidden': event.span <= 30 }">
              {{ event.times }}
            </span>
            </div>
          </div>
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
import { eventColor, timeFormat, initialEventPopupData, showEventPopup } from '@/utils';
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
  offset: (60 * dj(start).format('H') + 1 * dj(start).format('m') - 60 * startHour.value + 1) + 30,
  span: duration,
  times: `${dj(start).format(timeFormat())} - ${dj(start).add(duration, 'minutes').format(timeFormat())}`,
});

const processEvents = ((allDays) => {
  const eventsOnDate = {};
  const offsets = {};

  // add appointments, only for allDays === false
  if (!allDays) {
    props.appointments?.forEach((event) => {
      event.slots.forEach((slot) => {
        const key = dj(slot.start).format('YYYY-MM-DD');
        const innerKey = dj(slot.start).format('HH:mm');
        const extendedEvent = {...event, ...slot, ...timePosition(slot.start, slot.duration)};
        delete extendedEvent.slots;
        offsets[extendedEvent.offset] = extendedEvent.offset;

        if (!(key in eventsOnDate)) {
          eventsOnDate[key] = {};
        }

        if (innerKey in eventsOnDate[key] && eventsOnDate[key][innerKey]['items'].length < 4) {
          eventsOnDate[key][innerKey]['items'].push(extendedEvent);
        } else if (!(innerKey in eventsOnDate[key])) {
          eventsOnDate[key][innerKey] = {
            'items': [extendedEvent],
            'order': 0,
            'offset': extendedEvent.offset,
          };
        }

      });
    });
  }
  // add calendar events
  props.events?.forEach((event) => {
    if (!allDays && event.all_day) {
      return;
    } else if (allDays && !event.all_day) {
      return;
    }
    const key = dj(event.start).format('YYYY-MM-DD');
    const innerKey = dj(event.start).format('HH:mm');
    const extendedEvent = { ...event, ...timePosition(event.start, event.duration), remote: true };
    offsets[extendedEvent.offset] = extendedEvent.offset;

    if (!(key in eventsOnDate)) {
      eventsOnDate[key] = {};
    }

    if (innerKey in eventsOnDate[key] && eventsOnDate[key][innerKey]['items'].length < 4) {
      eventsOnDate[key][innerKey]['items'].push(extendedEvent);
    } else if (!(innerKey in eventsOnDate[key])) {
      eventsOnDate[key][innerKey] = {
        'items': [extendedEvent],
        'order': 0,
        'offset': extendedEvent.offset,
      };
    }
  });

  const orderedOffsets = Object.values(offsets).sort();

  // Sort offset for order - it's ugly sorry.
  // We don't store offsets by day, so you might see order: 4, and order: 7. Since it's sorted by value it should be fine.
  Object.keys(eventsOnDate).map((eventDate) => {
    Object.keys(eventsOnDate[eventDate]).map((eventTime) => {
      eventsOnDate[eventDate][eventTime]['order'] = orderedOffsets.indexOf(eventsOnDate[eventDate][eventTime]['items'][0].offset);
    });
  });

  return eventsOnDate;
})

// handle events to show

// Events excluding all day events
const events = computed(() => {
  const evts = processEvents(false);
  console.log(">> DURING DAY ", evts);

  return evts;
});
// Events excluding during day events
const allDayEvents = computed(() => {
  const evts = processEvents(true);
  console.log(">> ALL DAY ", evts);
  return evts;
});

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
const popup = ref({...initialEventPopupData});

</script>
