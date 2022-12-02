<template>
  <div>
    <div class="grid grid-cols-day gap-[1px] w-full bg-gray-200 border rounded-lg overflow-hidden">
      <!-- all day events -->
      <div class="text-center text-gray-400 bg-white py-2">{{ t('label.allDay') }}</div>
      <div class="bg-white py-2"></div>
      <!-- events with times -->
      <div class="text-center text-gray-400 bg-white grid grid-cols-1">
        <div v-for="h in hours" :key="h" class="h-12 lowercase">
          {{ h }}
        </div>
      </div>
      <div class="bg-white grid auto-rows-[1.5rem]">
        <div
          v-for="event in eventsByDate"
          :key="event"
          class="flex overflow-hidden"
          :style="{ 'grid-row': event.offset + ' / span ' + event.span }"
        >
          <div v-if="!booking" class="w-full text-sm whitespace-nowrap overflow-hidden overflow-ellipsis rounded bg-sky-400/10 border-2 border-dashed border-sky-400 my-1 mx-8 px-2 py-0.5">
            {{ event.title }}
          </div>
          <div v-else class="w-full text-sm text-gray-600 overflow-hidden group rounded-md bg-teal-50 p-1 my-1 mx-8 cursor-pointer hover:shadow-lg hover:text-white hover:bg-gradient-to-b hover:from-teal-500 hover:to-sky-600 flex">
            <div class="w-full whitespace-nowrap overflow-hidden overflow-ellipsis rounded lowercase p-1 font-semibold border-2 border-dashed border-teal-500 group-hover:border-white">
              {{ event.times }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from "vue";
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// component properties
const props = defineProps({
  selected: Object,  // currently active date
  events:   Array,   // data of events to show
  booking:  Boolean, // flag indicating if calendar is used to book time slots
});

// time borders for display
const startHour = 6;
const endHour = 18;

// handle events to show
const events = computed(() => {
  const eventsOnDate = {};
  props.events?.forEach(event => {
    event.slots.forEach(slot => {
      const key = dj(slot.start).format('YYYY-MM-DD');
      // create position of event based on *half hours* | TODO: handle quarter hours
      const offset = 2*dj(slot.start).format('H') + dj(slot.start).format('m')/30 - 2*startHour + 1;
      const span = Math.round(slot.duration / 30);
      const times = dj(slot.start).format('LT') + ' - ' + dj(slot.start).add(slot.duration, 'minutes').format('LT');
      const extendedEvent = {...event, offset: offset, span: span, times: times};
      if (key in eventsOnDate) {
        eventsOnDate[key].push(extendedEvent);
      } else {
        eventsOnDate[key] = [extendedEvent];
      }
    });
  });
  return eventsOnDate;
});
const eventsByDate = computed(() => {
  const key = dj(props.selected).format('YYYY-MM-DD');
  if (key in events.value) {
    return events.value[key];
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

</script>
