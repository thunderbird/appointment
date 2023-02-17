<template>
  <div>
    <div class="grid grid-cols-day gap-[1px] w-full bg-gray-200 border rounded-lg overflow-hidden">
      <!-- all day events -->
      <template v-if="!booking">
        <div class="text-gray-400 bg-white flex-center">{{ t('label.allDay') }}</div>
        <div class="bg-white grid auto-rows-max gap-1 p-1">
          <div
            v-for="event in eventsByDate?.allDay"
            :key="event"
            class="flex overflow-hidden"
          >
            <div class="w-full text-sm truncate rounded bg-amber-400/80 mx-8 px-2 py-0.5">
              {{ event.title }}
            </div>
          </div>
        </div>
      </template>
      <!-- events with times -->
      <div class="text-center text-gray-400 bg-white grid auto-rows-[4rem]">
        <div v-for="h in hours" :key="h" class="lowercase">
          {{ h }}
        </div>
      </div>
      <div class="bg-white grid auto-rows-[2rem]">
        <div
          v-for="event in eventsByDate?.duringDay"
          :key="event"
          class="flex overflow-hidden"
          :style="{ 'grid-row': event.offset + ' / span ' + event.span }"
        >
          <div
            v-if="!booking"
            class="w-full overflow-hidden rounded flex gap-4 text-gray-700 bg-sky-400/10 border-sky-400 my-1 mx-8 px-3 py-2"
            :class="{
              'border-2 border-dashed': !event.remote,
              'flex-col': event.span > 2,
              'flex-row': event.span <= 2,
            }"
            :style="{
              'border-color': eventColor(event, false).border,
              'background-color': !event.remote ? eventColor(event, false).background : event.calendar_color,
            }"
          >
            <div
              class="truncate"
              :class="{
                'self-center grow': event.span <= 2,
                'text-sm': event.span <= 1,
              }"
            >
              {{ event.title }}
            </div>
            <div
              class="flex text-xs"
              :class="{
                'flex-col gap-1 self-center': event.span <= 2,
                'items-center gap-4': event.span > 2,
              }"
            >
              <div class="flex gap-2">
                <icon-clock size="16" class="shrink-0" />
                <div class="whitespace-nowrap">
                  {{ event.times }}
                </div>
              </div>
              <div class="flex gap-2" :class="{ 'hidden': event.span <= 1 }">
                <icon-calendar size="16" class="shrink-0" />
                <div class="whitespace-nowrap">
                  {{ event.calendar_title }}
                </div>
              </div>
              <div class="flex gap-2" :class="{ 'hidden': event.span <= 2 }">
                <icon-link size="16" class="shrink-0" />
                <a :href="baseurl + event.slug" class="whitespace-nowrap text-teal-500 underline underline-offset-2" target="_blank">
                  {{ baseurl + event.slug }}
                </a>
              </div>
            </div>
          </div>
          <div
            v-else
            @click="bookSlot(event.start)"
            class="w-full text-sm text-gray-600 overflow-hidden rounded-md bg-teal-50 p-1 my-1 mx-8 cursor-pointer hover:shadow hover:bg-teal-100 flex"
            :class="{ 'shadow-lg bg-gradient-to-b from-teal-500 to-sky-600': event.selected }"
          >
            <div
              class="w-full truncate rounded lowercase p-1 font-semibold border-2 border-dashed border-teal-500"
              :class="{ 'text-white border-white': event.selected }"
            >
              <div :class="{ 'hidden': event.span <= 1 }">{{ event.times }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue';
import { eventColor } from '@/utils';
import { useI18n } from 'vue-i18n';

// icons
import {
  IconCalendar,
  IconClock,
  IconLink,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const dj = inject("dayjs");
const baseurl = inject("baseurl");

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
const eventsByDate = computed(() => {
  const key = dj(props.selected).format('YYYY-MM-DD');
  if (key in events.value) {
    return {
      duringDay: events.value[key].filter(e => !e.all_day),
      allDay:    events.value[key].filter(e => e.all_day),
    };
  } else {
    return null;
  }
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

</script>
