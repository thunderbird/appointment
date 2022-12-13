<template>
  <div class="absolute p-3 bg-white -translate-y-1/2 transition-all shadow-lg rounded-md z-30">
    <div class="absolute top-1/2 -translate-y-1/2 -left-1.5 rotate-45 w-3 h-3 bg-white"></div>
    <div class="flex flex-col gap-2">
      <div class="text-lg text-teal-500 font-semibold">{{ event?.title }}</div>
      <div class="text-xs text-gray-700">{{ eventDateTime }}</div>
      <div class="text-xs text-gray-700">{{ event?.calendar_title }}</div>
      <div v-if="event?.attendee" class="text-xs text-gray-700">{{ t('label.guest' , { 'count': 1 }) }}</div>
    </div>
  </div>
</template>

<script setup>
import { inject, computed } from "vue";
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const dj = inject("dayjs");

// component properties
const props = defineProps({
  event: Object, // event to show details in popup for
});

const eventDateTime = computed(() => {
  return props.event
    ? dj(props.event.start).format('dddd L, LT - ') + dj(props.event.start).add(props.event.duration, 'minutes').format('LT')
    : '';
});
</script>
