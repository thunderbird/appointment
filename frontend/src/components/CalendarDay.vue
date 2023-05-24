<template>
  <div>
    <div class="
      grid grid-cols-day gap-[1px] w-full border rounded-lg overflow-hidden
      bg-gray-200 border-gray-200 dark:bg-gray-600 dark:border-gray-600
    ">
      <!-- all day events -->
      <template v-if="!booking">
        <div class="flex-center text-gray-400 bg-white dark:bg-gray-700">
          {{ t('label.allDay') }}
        </div>
        <div class="grid auto-rows-max gap-1 p-1 bg-white dark:bg-gray-700">
          <div
            v-for="event in eventsByDate?.allDay"
            :key="event"
            class="flex overflow-hidden"
          >
            <div class="w-full text-sm truncate rounded mx-8 px-2 py-0.5 bg-amber-400/80">
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
        class="grid bg-white dark:bg-gray-700"
        :style="{ gridAutoRows: unitRem + 'rem' }"
      >
        <div
          v-for="event in eventsByDate?.duringDay"
          :key="event"
          class="flex overflow-hidden"
          :class="{ 'hidden': event.offset < 0 }"
          :style="{ gridRow: event.offset + ' / span ' + event.span }"
        >
          <div
            v-if="!booking"
            class="
              w-full overflow-hidden rounded flex gap-4 my-1 mx-8 px-3
              text-gray-700 bg-sky-400/10 border-sky-400
            "
            :class="{
              'border-2 border-dashed dark:text-white': !event.remote,
              'flex-col': event.span > 60,
              'flex-row': event.span <= 60,
              'py-2': event.span >= 30,
            }"
            :style="{
              'border-color': eventColor(event, false).border,
              'background-color': !event.remote ? eventColor(event, false).background : event.calendar_color,
            }"
          >
            <div
              class="truncate"
              :class="{
                'self-center grow': event.span <= 60,
                'text-sm': event.span < 60,
                'hidden': event.span < 30,
              }"
            >
              {{ event.title }}
            </div>
            <div
              class="flex text-xs"
              :class="{
                'items-center gap-4': event.span > 60,
                'flex-col gap-1 self-center': event.span <= 60,
                'hidden': event.span < 30,
              }"
            >
              <div class="flex gap-2">
                <icon-clock size="16" class="shrink-0" />
                <div class="whitespace-nowrap">
                  {{ event.times }}
                </div>
              </div>
              <div class="flex gap-2" :class="{ 'hidden': event.span <= 30 }">
                <icon-calendar size="16" class="shrink-0" />
                <div class="whitespace-nowrap">
                  {{ event.calendar_title }}
                </div>
              </div>
              <div class="flex gap-2" :class="{ 'hidden': event.span <= 60 }">
                <icon-link size="16" class="shrink-0" />
                <a
                  :href="bookingUrl + event.slug"
                  class="whitespace-nowrap underline underline-offset-2 text-teal-500"
                  target="_blank"
                >
                  {{ bookingUrl + event.slug }}
                </a>
              </div>
            </div>
          </div>
          <div
            v-else
            @click="bookSlot(event.start)"
            class="
              w-full text-sm overflow-hidden rounded-md p-1 my-1 mx-8 cursor-pointer hover:shadow flex
              text-gray-600 dark:text-gray-300 bg-teal-50 hover:bg-teal-100 dark:bg-teal-800 hover:dark:bg-teal-700
            "
            :class="{ 'shadow-lg bg-gradient-to-b from-teal-500 to-sky-600': event.selected }"
          >
            <div
              class="w-full truncate rounded lowercase p-1 font-semibold border-2 border-dashed border-teal-500"
              :class="{ 'text-white border-white': event.selected }"
            >
              <div :class="{ 'hidden': event.span <= 30 }">{{ event.times }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue';
import { eventColor, timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';

// icons
import {
  IconCalendar,
  IconClock,
  IconLink,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const dj = inject('dayjs');
const bookingUrl = inject('bookingUrl');

// component properties
const props = defineProps({
  selected: Object, // currently active date
  booking: Boolean, // flag indicating if calendar is used to book time slots
  appointments: Array, // data of appointments to show
  events: Array, // data of calendar events to show
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
  const start = elementsToShow.value.filter(e => !e.all_day).reduce(
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
const eventsByDate = computed(() => {
  const key = dj(props.selected).format('YYYY-MM-DD');
  if (key in events.value) {
    return {
      duringDay: events.value[key].filter((e) => !e.all_day),
      allDay: events.value[key].filter((e) => e.all_day),
    };
  }
  return null;
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

</script>
