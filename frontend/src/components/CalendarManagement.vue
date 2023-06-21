<template>
  <div class="flex max-w-2xl">
    <div class="text-xl">{{ title }}</div>
    <div class="inline-flex mx-auto mr-0" v-if="type === calendarManagementType.connect">
      <button class="bg-transparent disabled:scale-100 disabled:shadow-none disabled:opacity-50" :disabled="loading" @click="emit('sync')">
        <span class="inline-block mr-2">
          {{ t('label.syncCalendars') }}
        </span>
        <icon-refresh class="inline-block h-5 w-5 stroke-2 stroke-white fill-transparent"></icon-refresh>
      </button>
    </div>
  </div>
  <div v-if="filteredCalendars?.length" class="pl-6 flex flex-col gap-2 max-w-2xl">
    <div v-for="cal in filteredCalendars" :key="cal.id" class="flex gap-2 items-center">
      <div class="flex-center w-6 h-6 rounded-lg" :style="{ backgroundColor: cal.color ?? '#38bdf8' }">
        <icon-calendar class="w-4 h-4 fill-transparent stroke-2 stroke-white"/>
      </div>
      <span class="calendar-title">
      {{ cal.title }}
      </span>
      <button
          v-if="type === calendarManagementType.connect"
          @click="emit('modify', cal.id)"
          :disabled="loading"
          class="ml-auto flex items-center gap-0.5 px-2 py-1 rounded-full bg-teal-500 text-white text-xs disabled:scale-100 disabled:shadow-none disabled:opacity-50"
      >
        <icon-arrow-right class="h-3 w-3 stroke-2 stroke-white fill-transparent"/>
        {{ t('label.connectCalendar') }}
      </button>
      <button
          v-if="type === calendarManagementType.edit"
          @click="emit('modify', cal.id)"
          :disabled="loading"
          class="ml-auto flex items-center gap-0.5 px-2 py-1 rounded-full bg-teal-500 text-white text-xs disabled:scale-100 disabled:shadow-none disabled:opacity-50"
      >
        <icon-pencil class="h-3 w-3 stroke-2 stroke-white fill-transparent"/>
        {{ t('label.editCalendar') }}
      </button>
      <button v-if="cal.connected" class="bg-transparent p-0.5 disabled:scale-100 disabled:shadow-none disabled:opacity-50" :disabled="loading" @click="emit('remove', cal.id)">
        <icon-x class="h-5 w-5 stroke-2 stroke-rose-500 fill-transparent"/>
      </button>
    </div>
  </div>
</template>

<script setup>
import {
  IconArrowRight, IconCalendar, IconPencil, IconX, IconRefresh,
} from '@tabler/icons-vue';
import { calendarManagementType } from '@/definitions';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' });
const emit = defineEmits(['modify', 'remove', 'sync']);

const props = defineProps({
  calendars: Array, // List of calendars to display
  title: String,
  type: {
    validator(value) {
      return Object.values(calendarManagementType).includes(value);
    },
  },
  loading: Boolean,
});

// Filter by connected or not connected depending on the list type
const filteredCalendars = computed(() => props.calendars.filter((calendar) => (
  props.type === calendarManagementType.edit ? calendar.connected : !calendar.connected
)));

</script>