<template>
  <div
    class="absolute p-3 -translate-y-1/2 transition-all shadow-lg rounded-md z-30 bg-white dark:bg-gray-800"
    :class="{
      '-translate-x-full': position === 'left',
      '-translate-x-1/2': position === 'top'
    }"
  >
    <div
      class="absolute rotate-45 w-3 h-3 bg-white dark:bg-gray-800"
      :class="{
        'top-1/2 -translate-y-1/2 -left-1.5': !position || position === 'right',
        'top-1/2 -translate-y-1/2 -right-1.5': position === 'left',
        'left-1/2 -translate-x-1/2 -bottom-1.5': position === 'top',
      }"
    ></div>
    <div class="flex flex-col gap-2 text-gray-700 dark:text-gray-200">
      <div class="text-lg font-semibold max-w-sm truncate text-teal-500">{{ event?.title }}</div>
      <div class="text-xs flex gap-1.5 items-center">
        <icon-clock class="h-4 w-4 stroke-2 fill-transparent stroke-teal-500" />
        {{ eventDateTime }}
      </div>
      <div class="text-xs flex gap-1.5 items-center">
        <icon-calendar class="h-4 w-4 stroke-2 fill-transparent stroke-teal-500" />
        {{ event?.customData?.calendar_title }}
      </div>
      <div v-if="event?.customData?.attendee" class="text-xs flex gap-1.5 items-center">
        <icon-users class="h-4 w-4 stroke-2 fill-transparent stroke-teal-500" />
        {{ t('label.guest' , { 'count': 1 }) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, computed, toRefs } from 'vue';
import { useI18n } from 'vue-i18n';
import { timeFormat } from '@/utils';

// icons
import {
  IconCalendar,
  IconClock,
  IconUsers,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const dj = inject('dayjs');

// component properties
const props = defineProps({
  event: Object, // event to show details in popup for
  position: String, // currently supported: right, left, top
});

const { event } = toRefs(props);

// format datetime of event
const eventDateTime = computed(
  () => {
    const dateTimeParts = [];
    if (props.event) {
      // calculate date for active event
      const start = dj(props.event.time.start);
      dateTimeParts.push(start.format('dddd L'));
      if (!props.event.customData.all_day) {
        // add time if it's not an all day event
        const end = dj(props.event.time.end);
        dateTimeParts.push(start.format(`, ${timeFormat()} - `));
        dateTimeParts.push(end.format(timeFormat()));
      }
    }
    return dateTimeParts.join('');
  },
);
</script>
