<template>
  <div>
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
        <div v-for="h in hours" :key="h" class="h-12">
          {{ h }}
        </div>
      </div>
      <div
        v-for="d in days"
        :key="d.day"
        class="bg-white py-2"
      >
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
});

// generate names for each day of week
const days = computed(() => {
  const list = [];
  let day = props.selected.startOf('week');
  for (let i = 0; i < 7; i++) {
    list.push({
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
  let d = dj().hour(6).minute(0);
  for (let i = 0; i < 13; i++) {
    list.push(d.format('h:mm A'));
    d = d.add(1, 'hour');
  }
  return list;
});

</script>
