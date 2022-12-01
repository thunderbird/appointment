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
        class="text-2xl font-semibold w-10 h-10 flex justify-center items-center"
        :class="{'text-white rounded-full bg-teal-500': d.active }"
      >{{ d.day }}</div>
      <div class="text-lg">{{ d.weekday }}</div>
    </div>
    <!-- all day events -->
    <div class="text-center text-gray-400 bg-white">{{ t('label.allDay') }}</div>
    <div
      v-for="d in days"
      :key="d.day"
      class="bg-white py-2"
    >
    </div>
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
    >
      <div
        v-for="event in eventsByDate(d.date)"
        :key="event"
        class="flex overflow-hidden"
        :style="{ 'grid-row': event.offset + ' / span ' + event.span }"
      >
        <div class="w-full text-sm whitespace-nowrap overflow-hidden overflow-ellipsis rounded bg-sky-400/10 border-2 border-dashed border-sky-400 m-1 px-2 py-0.5">
          {{ event.title }}
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
  selected: Object, // currently active date
  events: Array,    // data of events to show
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
      if (key in eventsOnDate) {
        eventsOnDate[key].push({...event, offset: offset, span: span});
      } else {
        eventsOnDate[key] = [{...event, offset: offset, span: span}];
      }
    });
  });
  return eventsOnDate;
});
const eventsByDate = (d) => {
  const key = dj(d).format('YYYY-MM-DD');
  if (key in events.value) {
    return events.value[key];
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

</script>
