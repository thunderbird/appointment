<script setup lang="ts">
import { inject, computed, toRefs } from 'vue';
import { useI18n } from 'vue-i18n';
import { timeFormat } from '@/utils';
import { CalendarEvent } from '@/models';

// icons
import {
  IconCalendar,
  IconClock,
  IconUsers,
} from '@tabler/icons-vue';
import { dayjsKey } from '@/keys';

// component constants
const { t } = useI18n();
const dj = inject(dayjsKey);

// component properties
interface Props {
  event?: CalendarEvent, // event to show details in popup for
  position?: string, // Popup position relative to the trigger element
}
const props = defineProps<Props>();

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

<template>
  <div
    class="absolute z-30 -translate-y-1/2 rounded-md bg-white p-3 shadow-lg transition-all dark:bg-gray-800"
    :class="{
      '-translate-x-full': position === 'left',
      '-translate-x-1/2': position === 'top'
    }"
  >
    <div
      class="absolute size-3 rotate-45 bg-white dark:bg-gray-800"
      :class="{
        '-left-1.5 top-1/2 -translate-y-1/2': !position || position === 'right',
        '-right-1.5 top-1/2 -translate-y-1/2': position === 'left',
        '-bottom-1.5 left-1/2 -translate-x-1/2': position === 'top',
      }"
    ></div>
    <div class="flex flex-col gap-2 text-gray-700 dark:text-gray-200">
      <div class="max-w-sm truncate text-lg font-semibold text-teal-500">{{ event?.title }}</div>
      <div class="flex items-center gap-1.5 text-xs">
        <icon-clock class="size-4 fill-transparent stroke-teal-500 stroke-2" />
        {{ eventDateTime }}
      </div>
      <div class="flex items-center gap-1.5 text-xs">
        <icon-calendar class="size-4 fill-transparent stroke-teal-500 stroke-2" />
        {{ event?.customData?.calendar_title }}
      </div>
      <div v-if="event?.customData?.attendee" class="flex items-center gap-1.5 text-xs">
        <icon-users class="size-4 fill-transparent stroke-teal-500 stroke-2" />
        {{ t('label.guest', { 'count': 1 }) }}
      </div>
    </div>
  </div>
</template>
