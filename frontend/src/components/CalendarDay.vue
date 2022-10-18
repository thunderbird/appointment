<template>
  <div>
    <div class="grid grid-cols-day gap-[1px] w-full bg-gray-200 border rounded-lg overflow-hidden">
      <!-- all day events -->
      <div class="text-center text-gray-400 bg-white py-2">{{ t('label.allDay') }}</div>
      <div class="bg-white py-2"></div>
      <!-- events with times -->
      <div class="text-center text-gray-400 bg-white grid grid-cols-1">
        <div v-for="h in hours" :key="h" class="h-12">
          {{ h }}
        </div>
      </div>
      <div class="bg-white py-2">
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
// const props = defineProps({
//   selected: Object, // currently active date
// });

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
