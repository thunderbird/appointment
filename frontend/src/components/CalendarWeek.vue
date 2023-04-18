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
        @mouseleave="hideEventPopup"
      >
        <div
          v-for="event in eventsByDate(d.date)?.allDay"
          :key="event"
          class="flex overflow-hidden"
          @mouseenter="element => showEventPopup(element, event)"
        >
          <div class="w-full text-sm truncate rounded px-2 py-0.5 bg-amber-400/80">
            {{ event.title }}
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
      class="grid bg-white dark:bg-gray-700"
      :style="{ gridAutoRows: unitRem + 'rem' }"
      @mouseleave="hideEventPopup"
    >
      <div
        v-for="event in eventsByDate(d.date)?.duringDay"
        :key="event"
        class="flex overflow-hidden"
        :class="{ 'hidden': event.offset < 0 }"
        :style="{ gridRow: event.offset + ' / span ' + event.span }"
        @mouseenter="element => !booking ? showEventPopup(element, event) : null"
      >
        <div
          v-if="!booking"
          class="w-full truncate rounded flex m-1 px-2 bg-sky-400/10 border-sky-400"
          :class="{
            'border-2 border-dashed': !event.remote,
            'py-0.5': event.span >= 30,
          }"
          :style="{
            'border-color': eventColor(event, false).border,
            'background-color': !event.remote ? eventColor(event, false).background : event.calendar_color,
          }"
        >
          <div
            class="truncate"
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
    <event-popup
      v-if="(events && !booking)"
      :style="{
        'display': popup.display,
        'top': popup.top,
        'left': popup.left,
      }"
      :event="popup.event"
    />
  </div>
</template>

<script setup>
import { computed, inject, reactive } from 'vue';
import { eventColor } from '@/utils';
import { useI18n } from 'vue-i18n';
import EventPopup from '@/elements/EventPopup';

const { t } = useI18n();
const dj = inject("dayjs");

// component properties
const props = defineProps({
  selected:     Object,  // currently active date
  booking:      Boolean, // flag indicating if calendar is used to book time slots
  appointments: Array,   // data of appointments to show
  events:       Array,   // data of calendar events to show
});

// component emits
const emit = defineEmits(['eventSelected']);

// time borders for display
const baseRem     = 4;          // height for one hour element in rem
const unitRem     = baseRem/60; // height for shortest event (1 minute) in rem

// compute limits depending on displayed data
// TODO: handle remote events too
// begin showing events 2 hours before first event or at least 2pm
const startHour = computed(() => {
  const start = props.appointments.reduce((p, c) => {
    const earliestSlot = c.slots.reduce((ps, cs) => {
      return dj(cs.start).isBetween(props.selected.startOf('week'), props.selected.endOf('week'))
        ? Math.min(dj(cs.start).format('H'), ps)
        : ps;
    }, 16);
    return Math.min(earliestSlot, p);
  }, 16);
  return start - 2 >= 0 ? start - 2 : 0;
});
// end showing events 2 hours after first event or at max 10am
const endHour = computed(() => {
  const end = props.appointments.reduce((p, c) => {
    const latestSlot = c.slots.reduce((ps, cs) => {
      const slotEnd = dj(cs.start).add(cs.duration, 'minutes');
      return slotEnd.isBetween(props.selected.startOf('week'), props.selected.endOf('week'))
        ? Math.max(slotEnd.format('H'), ps)
        : ps;
    }, 9);
    return Math.max(latestSlot, p);
  }, 9);
  return startHour.value > end
    ? startHour.value + 8
    : end + 1 < 24 ? end + 1 : 24;
});

// handle events to show
const timePosition = (start, duration) => {
  // create position of event, smallest unit is one minute
  return {
    offset: 60*dj(start).format('H') + 1*dj(start).format('m') - 60*startHour.value + 1,
    span: duration,
    times: dj(start).format('LT') + ' - ' + dj(start).add(duration, 'minutes').format('LT'),
  }
};
const events = computed(() => {
  const eventsOnDate = {};
  // add appointments
  props.appointments?.forEach(event => {
    event.slots.forEach(slot => {
      const key = dj(slot.start).format('YYYY-MM-DD');
      const extendedEvent = {...event, ...slot, ...timePosition(slot.start, slot.duration)};
      delete extendedEvent.slots;
      if (key in eventsOnDate) {
        eventsOnDate[key].push(extendedEvent);
      } else {
        eventsOnDate[key] = [extendedEvent];
      }
    });
  });
  // add calendar events
  props.events?.forEach(event => {
    const key = dj(event.start).format('YYYY-MM-DD');
    const extendedEvent = {...event, ...timePosition(event.start, event.duration), remote: true};
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
      duringDay: events.value[key].filter(e => !e.all_day),
      allDay:    events.value[key].filter(e => e.all_day),
    };
  } else {
    return null;
  }
};

// generate names for each day of week
const days = computed(() => {
  const list = [];
  let day = props.selected.startOf('week');
  for (let i = 0; i < 7; i++) {
    list.push({
      date: day.format('YYYY-MM-DD'),
      day: day.format('D'),
      weekday: day.format('ddd'),
      active: day.isSame(dj(), 'day')
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
  for (let i = 0; i <= range; i++) {
    list.push(d.format('h:mm A'));
    d = d.add(1, 'hour');
  }
  return list;
});

// user selects a slot for booking
const bookSlot = (d) => {
  emit('eventSelected', d);
};

// event details
const popup = reactive({
  event: null,
  display: 'none',
  top: 0,
  left: 0
});
const showEventPopup = (element, event) => {
  popup.event = event;
  popup.display = 'block';
  popup.top = element.target.offsetTop + element.target.clientHeight/2 - element.target.parentElement.scrollTop + 'px';
  popup.left = element.target.offsetLeft + element.target.clientWidth + 'px';
};
const hideEventPopup = () => {
  popup.event = null;
  popup.display = 'none';
};
</script>
