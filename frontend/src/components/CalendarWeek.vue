<template>
  <div class="grid grid-cols-week gap-[1px] w-full bg-gray-200 border rounded-lg overflow-hidden">
    <!-- header with weekdays -->
    <div class="bg-white"></div>
    <div
      v-for="d in days"
      :key="d.day"
      class="flex flex-col items-center text-gray-700 bg-white py-2"
    >
      <div
        class="text-2xl font-semibold w-10 h-10 flex-center"
        :class="{'text-white rounded-full bg-teal-500': d.active }"
      >{{ d.day }}</div>
      <div class="text-lg">{{ d.weekday }}</div>
    </div>
    <!-- all day events -->
    <template v-if="!booking">
      <div class="text-gray-400 bg-white flex-center">{{ t('label.allDay') }}</div>
      <div
        v-for="d in days"
        :key="d.day"
        class="bg-white grid auto-rows-max gap-1 p-1"
        @mouseleave="hideEventPopup"
      >
        <div
          v-for="event in eventsByDate(d.date)?.allDay"
          :key="event"
          class="flex overflow-hidden"
          @mouseenter="element => showEventPopup(element, event)"
        >
          <div class="w-full text-sm truncate rounded bg-amber-400/80 px-2 py-0.5">
            {{ event.title }}
          </div>
        </div>
      </div>
    </template>
    <!-- events with times -->
    <div class="text-center text-gray-400 bg-white grid grid-cols-1">
      <div v-for="h in hours" :key="h" class="h-12 lowercase">
        {{ h }}
      </div>
    </div>
    <div
      v-for="d in days"
      :key="d.day"
      class="bg-white grid auto-rows-[1.5rem]"
      @mouseleave="hideEventPopup"
    >
      <div
        v-for="event in eventsByDate(d.date)?.duringDay"
        :key="event"
        class="flex overflow-hidden"
        :style="{ 'grid-row': event.offset + ' / span ' + event.span }"
        @mouseenter="element => !booking ? showEventPopup(element, event) : null"
      >
        <div
          v-if="!booking"
          class="w-full text-sm truncate rounded bg-sky-400/10 border-sky-400 m-1 px-2 py-0.5"
          :class="{
            'border-2 border-dashed': !event.remote
          }"
          :style="{
            'border-color': eventColor(event, false).border,
            'background-color': !event.remote ? eventColor(event, false).background : event.calendar_color,
          }"
        >
          {{ event.title }}
        </div>
        <div
          v-else
          @click="bookSlot(event.start)"
          class="w-full text-sm text-gray-600 overflow-hidden rounded-md bg-teal-50 p-1 m-1 cursor-pointer hover:shadow hover:bg-teal-100 flex"
          :class="{ 'shadow-lg bg-gradient-to-b from-teal-500 to-sky-600': event.selected }"
        >
          <div
            class="w-full truncate rounded lowercase p-1 font-semibold border-2 border-dashed border-teal-500"
            :class="{ 'text-white border-white': event.selected }"
          >
            {{ event.times }}
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
const startHour = 6;
const endHour = 18;

// handle events to show
const timePosition = (start, duration) => {
  // create position of event based on *half hours* | TODO: handle quarter hours or less
  return {
    offset: 2*dj(start).format('H') + dj(start).format('m')/30 - 2*startHour + 1,
    span: Math.round(duration / 30),
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
  const range = endHour - startHour;
  let d = dj().hour(startHour).minute(0);
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
